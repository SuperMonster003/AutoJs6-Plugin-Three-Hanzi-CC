from __future__ import annotations

import base64
import hashlib
import sys
import unittest
import urllib.parse
from pathlib import Path
from typing import Any


SCRIPT_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIRECTORY))

import check_upstream  # noqa: E402
import merge_upstream  # noqa: E402
import update_upstream  # noqa: E402
import verify_upstream  # noqa: E402


REPOSITORY = "Owner/Repo"
BASE_SHA = "a" * 40
HEAD_SHA = "b" * 40
MERGE_SHA = "c" * 40
BRANCH = "automation/opencc-1.5.0"
ARCHIVE = b"validated official resource archive"

BASE_LOCK = {
    "OPENCC_VERSION": "1.4.2",
    "OPENCC_TAG": "ver.1.4.2",
    "OPENCC_COMMIT": "1" * 40,
    "OPENCC_SOURCE_URL": "https://github.com/BYVoid/OpenCC.git",
    "OPENCC_RESOURCE_ASSET": "opencc-v1.4.2-resources.zip",
    "OPENCC_RESOURCE_SHA256": "2" * 64,
    "OPENCC_RESOURCE_SIZE": "123",
    "OPENCC_RESOURCE_MANIFEST_VERSION": "1",
}

HEAD_LOCK = {
    **BASE_LOCK,
    "OPENCC_VERSION": "1.5.0",
    "OPENCC_TAG": "ver.1.5.0",
    "OPENCC_COMMIT": "3" * 40,
    "OPENCC_RESOURCE_ASSET": "opencc-v1.5.0-resources.zip",
    "OPENCC_RESOURCE_SHA256": hashlib.sha256(ARCHIVE).hexdigest(),
    "OPENCC_RESOURCE_SIZE": str(len(ARCHIVE)),
}


def repository_file(data: bytes) -> dict[str, Any]:
    return {
        "type": "file",
        "encoding": "base64",
        "content": base64.b64encode(data).decode("ascii"),
        "size": len(data),
        "sha": "f" * 40,
    }


class FixtureApi:
    def __init__(self) -> None:
        title = "chore(deps): upgrade OpenCC to 1.5.0"
        self.pull = {
            "number": 7,
            "state": "open",
            "merged": False,
            "draft": False,
            "title": title,
            "html_url": f"https://github.com/{REPOSITORY}/pull/7",
            "user": {"login": "github-actions[bot]", "type": "Bot"},
            "base": {"ref": "master", "sha": BASE_SHA, "repo": {"full_name": REPOSITORY}},
            "head": {"ref": BRANCH, "sha": HEAD_SHA, "repo": {"full_name": REPOSITORY}},
            "commits": 1,
            "changed_files": 4,
            "labels": [],
            "mergeable": True,
            "mergeable_state": "clean",
        }
        self.commits = [
            {
                "sha": HEAD_SHA,
                "author": {"login": "github-actions[bot]", "type": "Bot"},
                "commit": {
                    "message": title,
                    "author": {
                        "name": "github-actions[bot]",
                        "email": "41898282+github-actions[bot]@users.noreply.github.com",
                    },
                },
                "parents": [{"sha": BASE_SHA}],
            },
        ]
        self.files = [
            {"filename": verify_upstream.LOCK_FILE, "status": "modified"},
            {"filename": verify_upstream.SOURCE_DIRECTORY.as_posix(), "status": "modified"},
            {
                "filename": (verify_upstream.ASSET_DIRECTORY / BASE_LOCK["OPENCC_RESOURCE_ASSET"]).as_posix(),
                "status": "removed",
            },
            {
                "filename": (verify_upstream.ASSET_DIRECTORY / HEAD_LOCK["OPENCC_RESOURCE_ASSET"]).as_posix(),
                "status": "added",
            },
        ]
        self.reviews: list[dict[str, Any]] = []
        self.workflow_runs = {
            "build.yml": [self.workflow_run("build.yml", "Build integrity", 100)],
            "markdown.yml": [self.workflow_run("markdown.yml", "Markdown integrity", 200)],
        }
        self.jobs = {
            100: [self.job(name) for name in sorted(merge_upstream.EXPECTED_WORKFLOWS["build.yml"][1])],
            200: [self.job(name) for name in sorted(merge_upstream.EXPECTED_WORKFLOWS["markdown.yml"][1])],
        }
        self.calls: list[tuple[str, str, Any]] = []
        self.merge_body: dict[str, Any] | None = None
        self.deleted_path = ""
        self.license_changed = False

    @staticmethod
    def job(name: str) -> dict[str, Any]:
        return {"name": name, "status": "completed", "conclusion": "success"}

    @staticmethod
    def workflow_run(workflow_file: str, name: str, run_id: int) -> dict[str, Any]:
        return {
            "id": run_id,
            "name": name,
            "path": f".github/workflows/{workflow_file}@{BRANCH}",
            "event": "workflow_dispatch",
            "head_branch": BRANCH,
            "head_sha": HEAD_SHA,
            "status": "completed",
            "conclusion": "success",
            "repository": {"full_name": REPOSITORY},
            "head_repository": {"full_name": REPOSITORY},
            "html_url": f"https://github.com/{REPOSITORY}/actions/runs/{run_id}",
        }

    def get_json(self, path: str, *, query: dict[str, str | int] | None = None) -> Any:
        self.calls.append(("GET", path, query))
        if path == f"/repos/{REPOSITORY}/pulls/7":
            return self.pull
        if path == f"/repos/{REPOSITORY}/git/ref/heads/master":
            return {"object": {"sha": BASE_SHA, "type": "commit"}}
        encoded_branch = urllib.parse.quote(BRANCH, safe="/")
        if path == f"/repos/{REPOSITORY}/git/ref/heads/{encoded_branch}":
            return {"object": {"sha": HEAD_SHA, "type": "commit"}}
        prefix = f"/repos/{REPOSITORY}/contents/"
        if path.startswith(prefix):
            file_path = urllib.parse.unquote(path.removeprefix(prefix))
            ref = str((query or {}).get("ref", ""))
            if file_path == verify_upstream.LOCK_FILE:
                properties = BASE_LOCK if ref == BASE_SHA else HEAD_LOCK
                return repository_file(update_upstream.render_lock(properties))
            if file_path == verify_upstream.SOURCE_DIRECTORY.as_posix():
                properties = BASE_LOCK if ref == BASE_SHA else HEAD_LOCK
                return {
                    "type": "file",
                    "sha": properties["OPENCC_COMMIT"],
                    "submodule_git_url": properties["OPENCC_SOURCE_URL"],
                    "size": 0,
                }
            base_resource = (verify_upstream.ASSET_DIRECTORY / BASE_LOCK["OPENCC_RESOURCE_ASSET"]).as_posix()
            head_resource = (verify_upstream.ASSET_DIRECTORY / HEAD_LOCK["OPENCC_RESOURCE_ASSET"]).as_posix()
            if file_path == base_resource and ref == BASE_SHA:
                return {"type": "file", "size": int(BASE_LOCK["OPENCC_RESOURCE_SIZE"]), "sha": "4" * 40}
            if file_path == head_resource and ref == HEAD_SHA:
                return {"type": "file", "size": len(ARCHIVE), "sha": "5" * 40}
        raise AssertionError(f"unexpected get_json call: {path}, {query}")

    def get_bytes(
        self,
        path: str,
        *,
        query: dict[str, str | int] | None = None,
        maximum_bytes: int = merge_upstream.MAX_CONTENT_BYTES,
    ) -> bytes:
        self.calls.append(("GET_BYTES", path, query))
        if path.startswith("/repos/BYVoid/OpenCC/contents/"):
            ref = str((query or {}).get("ref", ""))
            data = b"changed license" if self.license_changed and ref == HEAD_LOCK["OPENCC_COMMIT"] else b"stable license"
        else:
            self.assert_head_resource_call(path, query)
            data = ARCHIVE
        if len(data) > maximum_bytes:
            raise AssertionError("fixture bytes exceed requested maximum")
        return data

    @staticmethod
    def assert_head_resource_call(path: str, query: dict[str, str | int] | None) -> None:
        resource = (verify_upstream.ASSET_DIRECTORY / HEAD_LOCK["OPENCC_RESOURCE_ASSET"]).as_posix()
        expected = merge_upstream.encoded_contents_path(REPOSITORY, resource)
        if path != expected or query != {"ref": HEAD_SHA}:
            raise AssertionError(f"unexpected resource call: {path}, {query}")

    def get_paginated(
        self,
        path: str,
        *,
        key: str | None = None,
        query: dict[str, str | int] | None = None,
    ) -> list[dict[str, Any]]:
        self.calls.append(("GET_PAGES", path, query))
        if path == f"/repos/{REPOSITORY}/pulls":
            return [{"number": 7}]
        if path == f"/repos/{REPOSITORY}/pulls/7/commits":
            return self.commits
        if path == f"/repos/{REPOSITORY}/pulls/7/files":
            return self.files
        if path == f"/repos/{REPOSITORY}/pulls/7/reviews":
            return self.reviews
        workflow_prefix = f"/repos/{REPOSITORY}/actions/workflows/"
        if path.startswith(workflow_prefix) and path.endswith("/runs"):
            workflow_file = path.removeprefix(workflow_prefix).removesuffix("/runs")
            return self.workflow_runs[workflow_file]
        jobs_prefix = f"/repos/{REPOSITORY}/actions/runs/"
        if path.startswith(jobs_prefix) and path.endswith("/jobs"):
            run_id = int(path.removeprefix(jobs_prefix).removesuffix("/jobs"))
            return self.jobs[run_id]
        raise AssertionError(f"unexpected get_paginated call: {path}, {key}, {query}")

    def put_json(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(("PUT", path, body))
        if path != f"/repos/{REPOSITORY}/pulls/7/merge":
            raise AssertionError(f"unexpected put_json call: {path}")
        self.merge_body = body
        return {"merged": True, "message": "Pull Request successfully merged", "sha": MERGE_SHA}

    def delete(self, path: str) -> None:
        self.calls.append(("DELETE", path, None))
        self.deleted_path = path


def validated_release(_api_base: str, source_url: str) -> check_upstream.ValidatedRelease:
    if source_url != HEAD_LOCK["OPENCC_SOURCE_URL"]:
        raise AssertionError(f"unexpected source URL: {source_url}")
    return check_upstream.ValidatedRelease(
        properties=dict(HEAD_LOCK),
        archive_data=ARCHIVE,
        release_url="https://github.com/BYVoid/OpenCC/releases/tag/ver.1.5.0",
        release_name="OpenCC 1.5.0",
        release_body="fixture",
        published_at="2026-10-01T00:00:00Z",
    )


def evaluate(api: FixtureApi, mode: str = "pr-only") -> merge_upstream.Evaluation:
    return merge_upstream.evaluate_candidate(
        api,  # type: ignore[arg-type]
        REPOSITORY,
        BRANCH,
        HEAD_SHA,
        mode,
        release_loader=validated_release,
    )


class MergeUpstreamTest(unittest.TestCase):
    def test_build_workflow_contract_includes_every_current_runtime_gate(self) -> None:
        self.assertEqual(
            {
                "Unit tests and debug/release APKs",
                "Debug/release runtime (x86, API 24 minSdk)",
                "Binder round trip (arm64-v8a)",
                "Binder round trip (x86_64)",
                "Binder round trip (x86_64, 16 KB pages)",
            },
            merge_upstream.EXPECTED_WORKFLOWS["build.yml"][1],
        )

    def test_exact_candidate_is_eligible_in_pr_only_mode(self) -> None:
        result = evaluate(FixtureApi())
        self.assertTrue(result.eligible, result.reason)
        self.assertEqual(7, result.pull_number)
        self.assertEqual("1.5.0", result.version)
        self.assertEqual(BASE_SHA, result.base_sha)
        self.assertEqual({"build.yml", "markdown.yml"}, {item.workflow_file for item in result.evidence})
        self.assertFalse(result.merged)

    def test_stale_base_sha_is_rejected(self) -> None:
        api = FixtureApi()
        api.pull["base"]["sha"] = "9" * 40
        result = evaluate(api)
        self.assertFalse(result.eligible)
        self.assertIn("base SHA is stale", result.reason)

    def test_conflicted_or_blocked_pull_request_is_rejected(self) -> None:
        api = FixtureApi()
        api.pull["mergeable"] = False
        api.pull["mergeable_state"] = "dirty"
        result = evaluate(api)
        self.assertFalse(result.eligible)
        self.assertIn("cleanly mergeable", result.reason)

    def test_extra_or_replaced_path_is_rejected(self) -> None:
        api = FixtureApi()
        api.files[-1] = {"filename": "unexpected.txt", "status": "added"}
        result = evaluate(api)
        self.assertFalse(result.eligible)
        self.assertIn("path/status inventory", result.reason)

    def test_success_from_a_different_head_sha_is_rejected(self) -> None:
        api = FixtureApi()
        api.workflow_runs["build.yml"][0]["head_sha"] = "8" * 40
        result = evaluate(api)
        self.assertFalse(result.eligible)
        self.assertIn("no exact explicitly dispatched Build integrity run", result.reason)

    def test_latest_failed_job_is_rejected(self) -> None:
        api = FixtureApi()
        failed = api.workflow_run("build.yml", "Build integrity", 101)
        failed["conclusion"] = "failure"
        api.workflow_runs["build.yml"].append(failed)
        api.jobs[101] = [api.job(name) for name in sorted(merge_upstream.EXPECTED_WORKFLOWS["build.yml"][1])]
        result = evaluate(api)
        self.assertFalse(result.eligible)
        self.assertIn("latest exact Build integrity run", result.reason)

    def test_changes_requested_and_fuse_labels_are_rejected(self) -> None:
        api = FixtureApi()
        api.reviews = [
            {
                "id": 1,
                "submitted_at": "2026-10-01T00:00:00Z",
                "state": "CHANGES_REQUESTED",
                "user": {"login": "maintainer"},
            },
        ]
        result = evaluate(api)
        self.assertFalse(result.eligible)
        self.assertIn("maintainer", result.reason)

        api = FixtureApi()
        api.pull["labels"] = [{"name": "do-not-merge"}]
        result = evaluate(api)
        self.assertFalse(result.eligible)
        self.assertIn("fuse labels", result.reason)

    def test_resource_growth_and_license_drift_are_rejected(self) -> None:
        oversized = {**HEAD_LOCK, "OPENCC_RESOURCE_SIZE": str(int(BASE_LOCK["OPENCC_RESOURCE_SIZE"]) * 2)}
        with self.assertRaisesRegex(merge_upstream.GateRejected, "unattended limit|more than"):
            merge_upstream.verify_resource_growth(BASE_LOCK, oversized)

        api = FixtureApi()
        api.license_changed = True
        result = evaluate(api)
        self.assertFalse(result.eligible)
        self.assertIn("license evidence changed", result.reason)

    def test_merge_binds_head_sha_and_deletes_only_unchanged_branch(self) -> None:
        api = FixtureApi()
        eligible = evaluate(api, mode="merge")
        merged = merge_upstream.merge_candidate(api, eligible)  # type: ignore[arg-type]
        self.assertTrue(merged.merged)
        self.assertEqual(MERGE_SHA, merged.merge_sha)
        self.assertEqual(HEAD_SHA, api.merge_body["sha"] if api.merge_body else None)
        encoded_branch = urllib.parse.quote(BRANCH, safe="/")
        self.assertEqual(f"/repos/{REPOSITORY}/git/refs/heads/{encoded_branch}", api.deleted_path)

    def test_paused_is_no_side_effect_and_release_fails_closed(self) -> None:
        api = FixtureApi()
        paused = evaluate(api, mode="paused")
        self.assertFalse(paused.eligible)
        self.assertIn("paused", paused.reason)
        self.assertEqual([], api.calls)

        with self.assertRaisesRegex(merge_upstream.AutomationError, "M4-D-4"):
            evaluate(FixtureApi(), mode="release")

    def test_github_service_failure_propagates_instead_of_becoming_eligible(self) -> None:
        class FailingApi(FixtureApi):
            def get_paginated(
                self,
                path: str,
                *,
                key: str | None = None,
                query: dict[str, str | int] | None = None,
            ) -> list[dict[str, Any]]:
                raise merge_upstream.AutomationError("simulated GitHub outage")

        with self.assertRaisesRegex(merge_upstream.AutomationError, "simulated GitHub outage"):
            evaluate(FailingApi())


if __name__ == "__main__":
    unittest.main()
