from __future__ import annotations

import json
import tempfile
import unittest
import urllib.parse
import zipfile
from dataclasses import replace
from pathlib import Path
from typing import Any
from unittest.mock import patch

from scripts.release import draft_release
from scripts.release.draft_release import (
    DraftError,
    GitHubHttpError,
    WORKFLOW_BY_KEY,
    WORKFLOW_CONTRACTS,
    CandidateEvidence,
    DraftPlan,
    canonical_artifact_digest,
    create_draft_release,
    dispatch_release_gates,
    prepare_draft_plan,
    verify_candidate_artifact,
    verify_candidate_bundle,
    verify_draft_progression,
    verify_latest_release_baseline,
    verify_workflow_run,
)
from scripts.release.prepare_candidate import (
    CandidateBaseline,
    candidate_manifest_data,
    verify_package_sizes,
)
from scripts.release.prepare_release import (
    ABI_ORDER,
    ReleaseContext,
    collect_records,
    create_bundle,
    load_release_context,
)


REPOSITORY = "SuperMonster003/AutoJs6-Plugin-OpenCC"
SOURCE_SHA = "1" * 40
BASELINE_SHA = "2" * 40
SIGNER_SHA256 = "A" * 64
ARTIFACT_DIGEST = f"sha256:{'a' * 64}"
REPOSITORY_ID = 1300385798
CANDIDATE_RUN_ID = 300
BUILD_RUN_ID = 101
MARKDOWN_RUN_ID = 201


class FixtureApi:
    def __init__(self, candidate: CandidateEvidence) -> None:
        self.candidate = candidate
        self.master_sha = SOURCE_SHA
        self.deleted_release_ids: list[int] = []
        self.created_release: dict[str, Any] | None = None
        self.create_body: dict[str, Any] | None = None
        self.fail_upload_name = ""
        self.posts: list[tuple[str, dict[str, Any]]] = []
        self.tags = {candidate.baseline.tag: candidate.baseline.source_sha}
        self.latest = {
            "id": 500,
            "tag_name": candidate.baseline.tag,
            "draft": False,
            "prerelease": False,
            "assets": self.baseline_assets(),
        }
        self.runs = {
            BUILD_RUN_ID: self.run(WORKFLOW_BY_KEY["build"], BUILD_RUN_ID, "completed", "success"),
            MARKDOWN_RUN_ID: self.run(WORKFLOW_BY_KEY["markdown"], MARKDOWN_RUN_ID, "completed", "success"),
            CANDIDATE_RUN_ID: self.candidate_run(),
        }
        self.jobs = {
            BUILD_RUN_ID: self.job_values(WORKFLOW_BY_KEY["build"]),
            MARKDOWN_RUN_ID: self.job_values(WORKFLOW_BY_KEY["markdown"]),
        }
        self.workflow_runs = {
            "build.yml": [self.run(WORKFLOW_BY_KEY["build"], 90, "completed", "success")],
            "markdown.yml": [self.run(WORKFLOW_BY_KEY["markdown"], 190, "completed", "success")],
        }
        self.artifact = {
            "id": 700,
            "name": candidate.artifact_name,
            "expired": False,
            "digest": ARTIFACT_DIGEST,
            "size_in_bytes": 10_000,
            "workflow_run": {
                "id": CANDIDATE_RUN_ID,
                "head_sha": SOURCE_SHA,
                "repository_id": REPOSITORY_ID,
                "head_repository_id": REPOSITORY_ID,
            },
        }

    def baseline_assets(self) -> list[dict[str, Any]]:
        values = [
            {
                "name": (
                    f"{self.candidate.context.project_name}-v{self.candidate.baseline.version_name}-"
                    f"{abi}-deadbeef.apk"
                ),
                "size": self.candidate.baseline.package_sizes[abi],
            }
            for abi in ABI_ORDER
        ]
        values.extend(({"name": "SHA256SUMS.txt", "size": 1}, {"name": "RELEASE_NOTES.md", "size": 1}))
        return values

    @staticmethod
    def run(
        contract: draft_release.WorkflowContract,
        run_id: int,
        status: str,
        conclusion: str | None,
    ) -> dict[str, Any]:
        return {
            "id": run_id,
            "name": contract.name,
            "path": f".github/workflows/{contract.file}@refs/heads/master",
            "event": "workflow_dispatch",
            "head_branch": "master",
            "head_sha": SOURCE_SHA,
            "status": status,
            "conclusion": conclusion,
            "repository": {"full_name": REPOSITORY},
            "head_repository": {"full_name": REPOSITORY},
            "html_url": f"https://github.com/{REPOSITORY}/actions/runs/{run_id}",
        }

    @staticmethod
    def job_values(contract: draft_release.WorkflowContract) -> list[dict[str, Any]]:
        return [
            {"name": name, "status": "completed", "conclusion": "success"}
            for name in sorted(contract.jobs)
        ]

    @staticmethod
    def candidate_run() -> dict[str, Any]:
        return {
            "id": CANDIDATE_RUN_ID,
            "name": draft_release.RELEASE_WORKFLOW_NAME,
            "path": f".github/workflows/{draft_release.RELEASE_WORKFLOW_FILE}@refs/heads/master",
            "event": "workflow_dispatch",
            "head_branch": "master",
            "head_sha": SOURCE_SHA,
            "status": "in_progress",
            "conclusion": None,
            "repository": {"full_name": REPOSITORY},
            "head_repository": {"full_name": REPOSITORY},
            "html_url": f"https://github.com/{REPOSITORY}/actions/runs/{CANDIDATE_RUN_ID}",
        }

    def get_json(self, path: str, *, query: dict[str, object] | None = None) -> dict[str, Any]:
        if path == f"/repos/{REPOSITORY}":
            return {
                "id": REPOSITORY_ID,
                "full_name": REPOSITORY,
                "default_branch": "master",
                "html_url": f"https://github.com/{REPOSITORY}",
            }
        if path == f"/repos/{REPOSITORY}/git/ref/heads/master":
            return {"object": {"type": "commit", "sha": self.master_sha}}
        if path == f"/repos/{REPOSITORY}/releases/latest":
            return self.latest
        if path.startswith(f"/repos/{REPOSITORY}/actions/workflows/") and not path.endswith("/runs"):
            workflow_file = path.rsplit("/", 1)[-1]
            contract = next(item for item in WORKFLOW_CONTRACTS if item.file == workflow_file)
            return {
                "name": contract.name,
                "path": f".github/workflows/{contract.file}",
                "state": "active",
            }
        if path.startswith(f"/repos/{REPOSITORY}/actions/runs/") and not path.endswith(("/jobs", "/artifacts")):
            run_id = int(path.rsplit("/", 1)[-1])
            return self.runs[run_id]
        if path.startswith(f"/repos/{REPOSITORY}/releases/"):
            release_id = int(path.rsplit("/", 1)[-1])
            if self.created_release is not None and self.created_release["id"] == release_id:
                return self.created_release
            raise GitHubHttpError(404, path, "not found")
        raise AssertionError(f"unexpected get_json call: {path}, {query}")

    def get_optional_json(self, path: str, *, query: dict[str, object] | None = None) -> dict[str, Any] | None:
        if path.startswith(f"/repos/{REPOSITORY}/actions/runs/"):
            return self.get_json(path, query=query)
        tag_prefix = f"/repos/{REPOSITORY}/git/ref/tags/"
        if path.startswith(tag_prefix):
            tag = urllib.parse.unquote(path.removeprefix(tag_prefix))
            sha = self.tags.get(tag)
            return None if sha is None else {"object": {"type": "commit", "sha": sha}}
        if path.startswith(f"/repos/{REPOSITORY}/releases/"):
            try:
                return self.get_json(path, query=query)
            except GitHubHttpError as error:
                if error.status == 404:
                    return None
                raise
        raise AssertionError(f"unexpected get_optional_json call: {path}, {query}")

    def get_paginated(
        self,
        path: str,
        *,
        key: str | None = None,
        query: dict[str, object] | None = None,
    ) -> list[dict[str, Any]]:
        workflow_prefix = f"/repos/{REPOSITORY}/actions/workflows/"
        if path.startswith(workflow_prefix) and path.endswith("/runs"):
            workflow_file = path.removeprefix(workflow_prefix).removesuffix("/runs")
            return self.workflow_runs[workflow_file]
        run_prefix = f"/repos/{REPOSITORY}/actions/runs/"
        if path.startswith(run_prefix) and path.endswith("/jobs"):
            run_id = int(path.removeprefix(run_prefix).removesuffix("/jobs"))
            return self.jobs[run_id]
        if path == f"/repos/{REPOSITORY}/actions/runs/{CANDIDATE_RUN_ID}/artifacts":
            return [self.artifact]
        if path == f"/repos/{REPOSITORY}/releases":
            values = [self.latest]
            if self.created_release is not None:
                values.append(self.created_release)
            return values
        raise AssertionError(f"unexpected get_paginated call: {path}, {key}, {query}")

    def post_json(
        self,
        path: str,
        body: dict[str, Any],
        *,
        expected_statuses: frozenset[int] = frozenset({201}),
    ) -> dict[str, Any] | None:
        self.posts.append((path, body))
        dispatch_prefix = f"/repos/{REPOSITORY}/actions/workflows/"
        if path.startswith(dispatch_prefix) and path.endswith("/dispatches"):
            workflow_file = path.removeprefix(dispatch_prefix).removesuffix("/dispatches")
            contract = next(item for item in WORKFLOW_CONTRACTS if item.file == workflow_file)
            run_id = BUILD_RUN_ID if contract.key == "build" else MARKDOWN_RUN_ID
            run = self.run(contract, run_id, "completed", "success")
            self.runs[run_id] = run
            self.jobs[run_id] = self.job_values(contract)
            self.workflow_runs[workflow_file].append(run)
            return {"workflow_run_id": run_id}
        if path == f"/repos/{REPOSITORY}/releases":
            self.create_body = dict(body)
            self.created_release = {
                "id": 600,
                "tag_name": body["tag_name"],
                "target_commitish": body["target_commitish"],
                "name": body["name"],
                "body": body["body"],
                "draft": body["draft"],
                "prerelease": body["prerelease"],
                "published_at": None,
                "author": {"login": draft_release.EXPECTED_BOT_LOGIN},
                "assets": [],
                "html_url": f"https://github.com/{REPOSITORY}/releases/tag/untagged-test",
            }
            return self.created_release
        raise AssertionError(f"unexpected post_json call: {path}, {body}, {expected_statuses}")

    def upload_asset(
        self,
        repository: str,
        release_id: int,
        asset: draft_release.ReleaseAsset,
    ) -> dict[str, Any]:
        if asset.name == self.fail_upload_name:
            raise DraftError("simulated asset upload failure")
        if self.created_release is None or release_id != self.created_release["id"]:
            raise AssertionError("upload targeted an unknown draft")
        value = {
            "name": asset.name,
            "state": "uploaded",
            "size": asset.size,
            "digest": f"sha256:{asset.sha256}",
            "content_type": asset.content_type,
            "uploader": {"login": draft_release.EXPECTED_BOT_LOGIN},
        }
        self.created_release["assets"].append(value)
        return value

    def delete(self, path: str) -> None:
        release_id = int(path.rsplit("/", 1)[-1])
        if self.created_release is None or self.created_release["id"] != release_id:
            raise AssertionError("delete targeted an unknown draft")
        self.deleted_release_ids.append(release_id)
        self.created_release = None


class DraftReleaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        (self.root / ".changelog").mkdir()
        (self.root / "scripts" / "release").mkdir(parents=True)
        (self.root / "settings.gradle.kts").write_text(
            'rootProject.name = "autojs6-plugin-opencc"\n',
            encoding="utf-8",
        )
        (self.root / "version.properties").write_text(
            "VERSION_NAME=1.4.0\nVERSION_BUILD=21\n",
            encoding="utf-8",
        )
        changelog = {
            "changelog_label_improvement": "Improvement",
            "$data": {
                "v1.4.0": {
                    "released_date": "2026/10/01",
                    "improvement": ["Exercise the trusted draft controller."],
                },
            },
        }
        (self.root / ".changelog" / "lang_en.json").write_text(
            json.dumps(changelog),
            encoding="utf-8",
        )
        (self.root / "opencc-upstream.properties").write_text(
            "\n".join(
                (
                    "OPENCC_VERSION=1.5.0",
                    "OPENCC_TAG=ver.1.5.0",
                    f"OPENCC_COMMIT={'3' * 40}",
                    "OPENCC_RESOURCE_ASSET=opencc-v1.5.0-resources.zip",
                    f"OPENCC_RESOURCE_SHA256={'4' * 64}",
                    "OPENCC_RESOURCE_SIZE=1237704",
                    "",
                ),
            ),
            encoding="utf-8",
        )
        self.input_dir = self.root / "input"
        self.input_dir.mkdir()
        self.create_raw_apks()
        self.context = load_release_context(self.root)
        raw_records, foreign = collect_records(self.input_dir, self.context)
        self.assertEqual([], foreign)
        self.baseline = CandidateBaseline(
            "v1.3.0",
            BASELINE_SHA,
            "1.3.0",
            20,
            SIGNER_SHA256,
            {record.abi: record.size for record in raw_records},
        )
        baseline_json = {
            "schema_version": 1,
            "release": {
                "tag": self.baseline.tag,
                "source_sha": self.baseline.source_sha,
                "version_name": self.baseline.version_name,
                "version_build": self.baseline.version_build,
                "signer_certificate_sha256": self.baseline.signer_certificate_sha256,
            },
            "package_sizes": self.baseline.package_sizes,
            "limits": {"max_growth_bytes": 524288, "max_growth_percent": 25},
        }
        (self.root / "scripts" / "release" / "candidate-baseline.json").write_text(
            json.dumps(baseline_json),
            encoding="utf-8",
        )
        self.bundle = create_bundle(
            self.context,
            raw_records,
            self.root / "build" / "release" / "v1.4.0",
            SIGNER_SHA256,
        )
        records, foreign = collect_records(self.bundle, self.context)
        self.assertEqual([], foreign)
        maximum_sizes = verify_package_sizes(records, self.baseline)
        manifest = candidate_manifest_data(
            self.context,
            self.bundle,
            SOURCE_SHA,
            21,
            SIGNER_SHA256,
            records,
            self.baseline,
            maximum_sizes,
        )
        (self.bundle / "CANDIDATE.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        self.apksigner = self.root / "apksigner"
        self.zipalign = self.root / "zipalign"
        self.apksigner.write_text("fixture", encoding="utf-8")
        self.zipalign.write_text("fixture", encoding="utf-8")
        self.candidate = self.validated_candidate()
        self.api = FixtureApi(self.candidate)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def create_raw_apks(self) -> None:
        all_abis = {"arm64-v8a", "armeabi-v7a", "x86_64", "x86"}
        for abi in ABI_ORDER:
            with zipfile.ZipFile(self.input_dir / f"app-{abi}-release.apk", "w") as archive:
                archive.writestr("AndroidManifest.xml", f"manifest-{abi}")
                archive.writestr("classes.dex", f"classes-{abi}")
                for native_abi in sorted(all_abis if abi == "universal" else {abi}):
                    archive.writestr(f"lib/{native_abi}/libopencc_jni.so", f"native-{abi}")

    def validated_candidate(self) -> CandidateEvidence:
        with (
            patch("scripts.release.draft_release.verify_git_source"),
            patch("scripts.release.draft_release.git_is_ancestor", return_value=True),
            patch("scripts.release.draft_release.verify_signatures", return_value=SIGNER_SHA256),
            patch("scripts.release.draft_release.verify_deep_apk_content"),
            patch("scripts.release.draft_release.verify_zip_alignment"),
        ):
            return verify_candidate_bundle(
                self.root,
                self.bundle,
                SOURCE_SHA,
                SIGNER_SHA256,
                self.apksigner,
                self.zipalign,
            )

    def plan(self) -> DraftPlan:
        return prepare_draft_plan(
            self.api,  # type: ignore[arg-type]
            REPOSITORY,
            self.candidate,
            BUILD_RUN_ID,
            MARKDOWN_RUN_ID,
        )

    def test_candidate_bundle_is_independently_reverified(self) -> None:
        candidate = self.validated_candidate()
        self.assertEqual("v1.4.0", candidate.tag)
        self.assertEqual(21, candidate.version_build)
        self.assertEqual(tuple(ABI_ORDER), tuple(record.abi for record in candidate.records))
        self.assertEqual(64, len(candidate.manifest_sha256))

        manifest_path = self.bundle / "CANDIDATE.json"
        value = json.loads(manifest_path.read_text(encoding="utf-8"))
        value["source_sha"] = "9" * 40
        manifest_path.write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaisesRegex(DraftError, "CANDIDATE.json differs"):
            self.validated_candidate()

    def test_draft_requires_strict_version_and_build_progression(self) -> None:
        verify_draft_progression(self.context, 21, self.baseline)
        same_version = replace(self.context, version_name="1.3.0")
        with self.assertRaisesRegex(DraftError, "must be newer"):
            verify_draft_progression(same_version, 21, self.baseline)
        with self.assertRaisesRegex(DraftError, "Draft build"):
            verify_draft_progression(self.context, 20, self.baseline)

    def test_artifact_digest_is_canonical(self) -> None:
        self.assertEqual(ARTIFACT_DIGEST, canonical_artifact_digest("a" * 64))
        self.assertEqual(ARTIFACT_DIGEST, canonical_artifact_digest(ARTIFACT_DIGEST))
        for value in ("", "sha256:" + "A" * 64, "md5:" + "a" * 64):
            with self.assertRaisesRegex(DraftError, "Malformed candidate artifact"):
                canonical_artifact_digest(value)

    def test_candidate_artifact_is_bound_to_this_active_workflow_run(self) -> None:
        verify_candidate_artifact(
            self.api,  # type: ignore[arg-type]
            REPOSITORY,
            self.candidate,
            700,
            "a" * 64,
            CANDIDATE_RUN_ID,
        )
        self.api.artifact["workflow_run"]["head_sha"] = "8" * 40
        with self.assertRaisesRegex(DraftError, "Artifact source SHA changed"):
            verify_candidate_artifact(
                self.api,  # type: ignore[arg-type]
                REPOSITORY,
                self.candidate,
                700,
                ARTIFACT_DIGEST,
                CANDIDATE_RUN_ID,
            )

    def test_exact_workflow_job_inventory_includes_min_sdk(self) -> None:
        evidence = verify_workflow_run(
            self.api,  # type: ignore[arg-type]
            REPOSITORY,
            SOURCE_SHA,
            WORKFLOW_BY_KEY["build"],
            BUILD_RUN_ID,
        )
        self.assertIn("Debug/release runtime (x86, API 24 minSdk)", evidence.job_names)
        self.api.jobs[BUILD_RUN_ID] = self.api.jobs[BUILD_RUN_ID][1:]
        with self.assertRaisesRegex(DraftError, "job inventory changed"):
            verify_workflow_run(
                self.api,  # type: ignore[arg-type]
                REPOSITORY,
                SOURCE_SHA,
                WORKFLOW_BY_KEY["build"],
                BUILD_RUN_ID,
            )

    def test_release_gate_dispatches_are_explicit_and_exact_sha(self) -> None:
        evidence = dispatch_release_gates(
            self.api,  # type: ignore[arg-type]
            REPOSITORY,
            SOURCE_SHA,
            "release",
            timeout_seconds=10,
            poll_seconds=1,
            monotonic=lambda: 0,
            sleep=lambda _seconds: None,
        )
        self.assertEqual({"build", "markdown"}, {item.contract.key for item in evidence})
        dispatches = [path for path, body in self.api.posts if path.endswith("/dispatches") and body == {"ref": "master"}]
        self.assertEqual(2, len(dispatches))

    def test_release_gate_dispatch_fails_before_side_effect_if_master_moved(self) -> None:
        self.api.master_sha = "8" * 40
        with self.assertRaisesRegex(DraftError, "Remote master moved"):
            dispatch_release_gates(
                self.api,  # type: ignore[arg-type]
                REPOSITORY,
                SOURCE_SHA,
                "release",
                timeout_seconds=10,
                poll_seconds=1,
            )
        self.assertEqual([], self.api.posts)

    def test_latest_release_must_match_checked_in_baseline(self) -> None:
        self.assertEqual(500, verify_latest_release_baseline(self.api, REPOSITORY, self.candidate))  # type: ignore[arg-type]
        self.api.latest["assets"][0]["size"] += 1
        with self.assertRaisesRegex(DraftError, "sizes differ"):
            verify_latest_release_baseline(self.api, REPOSITORY, self.candidate)  # type: ignore[arg-type]

    def test_draft_plan_rejects_any_tag_or_release_conflict(self) -> None:
        plan = self.plan()
        self.assertEqual(7, len(plan.assets))
        self.api.tags[self.candidate.tag] = SOURCE_SHA
        with self.assertRaisesRegex(DraftError, "tag already exists"):
            self.plan()

        self.api.tags.pop(self.candidate.tag)
        self.api.created_release = {
            "id": 601,
            "tag_name": self.candidate.tag,
            "draft": True,
        }
        with self.assertRaisesRegex(DraftError, "already uses"):
            self.plan()

    def test_create_draft_uploads_exact_assets_without_tag_or_latest_change(self) -> None:
        plan = self.plan()
        result = create_draft_release(self.api, REPOSITORY, plan)  # type: ignore[arg-type]
        self.assertEqual(600, result.release_id)
        self.assertEqual(self.candidate.tag, result.tag)
        self.assertEqual(7, len(result.assets))
        self.assertIsNotNone(self.api.created_release)
        self.assertNotIn(self.candidate.tag, self.api.tags)
        self.assertEqual(500, self.api.latest["id"])
        self.assertEqual(
            {
                "tag_name": self.candidate.tag,
                "target_commitish": SOURCE_SHA,
                "name": self.candidate.tag,
                "body": plan.notes,
                "draft": True,
                "prerelease": False,
                "generate_release_notes": False,
                "make_latest": "false",
            },
            self.api.create_body,
        )

    def test_asset_failure_rolls_back_only_the_new_draft(self) -> None:
        plan = self.plan()
        self.api.fail_upload_name = plan.assets[1].name
        with self.assertRaisesRegex(DraftError, "was rolled back"):
            create_draft_release(self.api, REPOSITORY, plan)  # type: ignore[arg-type]
        self.assertEqual([600], self.api.deleted_release_ids)
        self.assertIsNone(self.api.created_release)
        self.assertEqual(500, self.api.latest["id"])
        self.assertEqual({self.baseline.tag: BASELINE_SHA}, self.api.tags)

    def test_remote_master_race_prevents_draft_creation(self) -> None:
        plan = self.plan()
        self.api.master_sha = "8" * 40
        with self.assertRaisesRegex(DraftError, "Remote master moved"):
            create_draft_release(self.api, REPOSITORY, plan)  # type: ignore[arg-type]
        release_posts = [path for path, _body in self.api.posts if path == f"/repos/{REPOSITORY}/releases"]
        self.assertEqual([], release_posts)


if __name__ == "__main__":
    unittest.main()
