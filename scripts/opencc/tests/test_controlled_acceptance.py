from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock


SCRIPT_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIRECTORY))

import check_upstream  # noqa: E402
import controlled_acceptance  # noqa: E402
import update_upstream  # noqa: E402
import verify_upstream  # noqa: E402


def miniature_archive(commit: str, dictionary: bytes = b"one\tone\ntwo\ttwo\n") -> bytes:
    manifest = {
        "commit_id": commit,
        "entries": {
            "dictionary.txt": {
                "sha256": hashlib.sha256(dictionary).hexdigest(),
                "size": len(dictionary),
            },
            "s2t.json": {
                "sha256": hashlib.sha256(b"{}").hexdigest(),
                "size": 2,
            },
        },
        "hash_algorithm": "sha256",
        "manifest_version": 1,
        "source_dirty": False,
        "source_url": "https://github.com/BYVoid/OpenCC",
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("dictionary.txt", dictionary)
        archive.writestr("s2t.json", b"{}")
        archive.writestr(
            verify_upstream.RESOURCE_MANIFEST,
            (json.dumps(manifest, indent=2) + "\n").encode("utf-8"),
        )
    return output.getvalue()


def acceptance_result() -> controlled_acceptance.AcceptanceResult:
    return controlled_acceptance.AcceptanceResult(
        "fixture available",
        dict(controlled_acceptance.BASE_PROPERTIES),
        dict(controlled_acceptance.FIXTURE_PROPERTIES),
        controlled_acceptance.FIXTURE_BRANCH,
        controlled_acceptance.FIXTURE_TITLE,
        controlled_acceptance.render_pull_request_body(),
    )


class ControlledAcceptanceTest(unittest.TestCase):
    def test_fixture_has_independent_non_release_barriers(self) -> None:
        self.assertGreaterEqual(int(controlled_acceptance.FIXTURE_VERSION.split(".", 1)[0]), 999)
        self.assertFalse(controlled_acceptance.FIXTURE_TAG.startswith("ver."))
        self.assertTrue(controlled_acceptance.FIXTURE_TAG.startswith("controlled-ver."))
        self.assertEqual(
            f"automation/opencc-{controlled_acceptance.FIXTURE_VERSION}",
            controlled_acceptance.FIXTURE_BRANCH,
        )
        self.assertNotEqual(
            f"chore(deps): upgrade OpenCC to {controlled_acceptance.FIXTURE_VERSION}",
            controlled_acceptance.FIXTURE_TITLE,
        )

    def test_manifest_rewrite_is_deterministic_and_marks_fixture(self) -> None:
        base_commit = "1" * 40
        fixture_commit = "2" * 40
        base = miniature_archive(base_commit)
        first = controlled_acceptance.rewrite_archive_manifest(
            base,
            base_commit,
            fixture_commit,
            controlled_acceptance.FIXTURE_MARKER,
        )
        second = controlled_acceptance.rewrite_archive_manifest(
            base,
            base_commit,
            fixture_commit,
            controlled_acceptance.FIXTURE_MARKER,
        )
        self.assertEqual(first, second)
        with zipfile.ZipFile(io.BytesIO(first)) as archive:
            manifest = json.loads(archive.read(verify_upstream.RESOURCE_MANIFEST))
            dictionary = archive.read("dictionary.txt")
            self.assertEqual(fixture_commit, manifest["commit_id"])
            self.assertEqual(controlled_acceptance.FIXTURE_MARKER, manifest["controlled_acceptance"])
            self.assertEqual(b"one\tone\r\ntwo\ttwo\r\n", dictionary)
            self.assertEqual(len(dictionary), manifest["entries"]["dictionary.txt"]["size"])
            self.assertEqual(
                hashlib.sha256(dictionary).hexdigest(),
                manifest["entries"]["dictionary.txt"]["sha256"],
            )
            self.assertTrue(all(info.compress_type == zipfile.ZIP_STORED for info in archive.infolist()))

    def test_manifest_rewrite_rejects_wrong_base_or_existing_marker(self) -> None:
        base = miniature_archive("1" * 40)
        with self.assertRaisesRegex(controlled_acceptance.ControlledAcceptanceError, "commit drifted"):
            controlled_acceptance.rewrite_archive_manifest(base, "0" * 40, "2" * 40, {})

        once = controlled_acceptance.rewrite_archive_manifest(base, "1" * 40, "2" * 40, {})
        with self.assertRaisesRegex(controlled_acceptance.ControlledAcceptanceError, "already contains"):
            controlled_acceptance.rewrite_archive_manifest(once, "2" * 40, "3" * 40, {})

        with self.assertRaisesRegex(controlled_acceptance.ControlledAcceptanceError, "unexpected CR bytes"):
            controlled_acceptance.rewrite_archive_manifest(
                miniature_archive("1" * 40, b"one\tone\r\n"),
                "1" * 40,
                "2" * 40,
                {},
            )

    def test_repository_asset_reproduces_locked_fixture_when_available(self) -> None:
        root = Path(__file__).resolve().parents[3]
        path = (
            root
            / verify_upstream.ASSET_DIRECTORY
            / controlled_acceptance.BASE_PROPERTIES["OPENCC_RESOURCE_ASSET"]
        )
        if not path.is_file():
            self.skipTest("the controlled branch intentionally removes the base resource")
        archive = controlled_acceptance.build_fixture_archive(path.read_bytes())
        self.assertEqual(controlled_acceptance.FIXTURE_ARCHIVE_SIZE, len(archive))
        self.assertEqual(controlled_acceptance.FIXTURE_ARCHIVE_SHA256, hashlib.sha256(archive).hexdigest())

    def test_remote_fixture_must_be_direct_child_at_exact_url(self) -> None:
        response = {
            "sha": controlled_acceptance.FIXTURE_COMMIT,
            "parents": [{"sha": controlled_acceptance.BASE_PROPERTIES["OPENCC_COMMIT"]}],
            "html_url": f"https://github.com/BYVoid/OpenCC/commit/{controlled_acceptance.FIXTURE_COMMIT}",
        }
        with mock.patch.object(check_upstream, "read_json", return_value=response):
            controlled_acceptance.validate_fixture_commit(check_upstream.DEFAULT_API_BASE)

        response["parents"] = [{"sha": "0" * 40}]
        with (
            mock.patch.object(check_upstream, "read_json", return_value=response),
            self.assertRaisesRegex(controlled_acceptance.ControlledAcceptanceError, "direct child"),
        ):
            controlled_acceptance.validate_fixture_commit(check_upstream.DEFAULT_API_BASE)

    def test_verify_requires_exact_fixture_lock_and_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / verify_upstream.LOCK_FILE).write_bytes(
                update_upstream.render_lock(controlled_acceptance.FIXTURE_PROPERTIES),
            )
            with (
                mock.patch.object(controlled_acceptance, "verify_source") as verify_source,
                mock.patch.object(verify_upstream, "verify_resource_archive", return_value=(39, 16)),
                mock.patch.object(controlled_acceptance, "inspect_archive_marker") as inspect_marker,
            ):
                controlled_acceptance.verify(root)
            verify_source.assert_called_once_with(root)
            inspect_marker.assert_called_once()

            changed = {**controlled_acceptance.FIXTURE_PROPERTIES, "OPENCC_TAG": "ver.999.4.2"}
            (root / verify_upstream.LOCK_FILE).write_bytes(update_upstream.render_lock(changed))
            with self.assertRaisesRegex(controlled_acceptance.ControlledAcceptanceError, "lock.*drifted"):
                controlled_acceptance.verify(root)

    def test_inspect_revalidates_formal_release_and_fixture_commit(self) -> None:
        formal = check_upstream.ValidatedRelease(
            dict(controlled_acceptance.BASE_PROPERTIES),
            b"formal archive",
            "https://github.com/BYVoid/OpenCC/releases/tag/ver.1.4.2",
            "OpenCC 1.4.2",
            "",
            "2026-08-22T00:00:00Z",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            asset = root / verify_upstream.ASSET_DIRECTORY / controlled_acceptance.BASE_PROPERTIES["OPENCC_RESOURCE_ASSET"]
            asset.parent.mkdir(parents=True)
            asset.write_bytes(formal.archive_data)
            (root / verify_upstream.LOCK_FILE).write_bytes(
                update_upstream.render_lock(controlled_acceptance.BASE_PROPERTIES),
            )
            with (
                mock.patch.object(verify_upstream, "verify_resource_archive", return_value=(39, 16)),
                mock.patch.object(controlled_acceptance, "official_release", return_value=formal),
                mock.patch.object(controlled_acceptance, "build_fixture_archive", return_value=b"fixture"),
                mock.patch.object(controlled_acceptance, "validate_fixture_commit") as validate_commit,
            ):
                result = controlled_acceptance.inspect(root, check_upstream.DEFAULT_API_BASE)
        self.assertEqual(controlled_acceptance.FIXTURE_BRANCH, result.branch_name)
        self.assertEqual("controlled", self.output_values(result)["candidate_kind"])
        validate_commit.assert_called_once()

    def output_values(self, result: controlled_acceptance.AcceptanceResult) -> dict[str, str]:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "github-output.txt"
            with mock.patch.dict(os.environ, {"GITHUB_OUTPUT": str(output)}):
                controlled_acceptance.append_workflow_outputs(result)
            return dict(line.split("=", 1) for line in output.read_text(encoding="utf-8").splitlines())

    def test_prepare_rolls_back_lock_and_resources_after_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / verify_upstream.SOURCE_DIRECTORY
            source.mkdir(parents=True)
            old_resource = root / verify_upstream.ASSET_DIRECTORY / controlled_acceptance.BASE_PROPERTIES["OPENCC_RESOURCE_ASSET"]
            old_resource.parent.mkdir(parents=True)
            old_resource.write_bytes(b"base archive")
            old_lock = update_upstream.render_lock(controlled_acceptance.BASE_PROPERTIES)
            (root / verify_upstream.LOCK_FILE).write_bytes(old_lock)
            with (
                mock.patch.object(update_upstream, "ensure_clean_worktree"),
                mock.patch.object(verify_upstream, "verify"),
                mock.patch.object(controlled_acceptance, "inspect", return_value=acceptance_result()),
                mock.patch.object(controlled_acceptance, "build_fixture_archive", return_value=b"fixture archive"),
                mock.patch.object(controlled_acceptance, "fetch_fixture_source"),
                mock.patch.object(controlled_acceptance, "verify", side_effect=controlled_acceptance.ControlledAcceptanceError("simulated drift")),
                mock.patch.object(update_upstream, "git", return_value=controlled_acceptance.BASE_PROPERTIES["OPENCC_COMMIT"]),
            ):
                with self.assertRaisesRegex(controlled_acceptance.ControlledAcceptanceError, "simulated drift"):
                    controlled_acceptance.prepare(root, check_upstream.DEFAULT_API_BASE)

            new_resource = root / verify_upstream.ASSET_DIRECTORY / controlled_acceptance.FIXTURE_ASSET
            self.assertEqual(old_lock, (root / verify_upstream.LOCK_FILE).read_bytes())
            self.assertEqual(b"base archive", old_resource.read_bytes())
            self.assertFalse(new_resource.exists())

    def test_pull_request_body_is_unambiguously_non_publishable(self) -> None:
        body = controlled_acceptance.render_pull_request_body()
        self.assertIn("deliberately non-release **draft**", body)
        self.assertIn("must never be merged, tagged, released", body)
        self.assertIn("`pr-only`", body)
        self.assertIn("`merge`, `release`, and `--execute` remain hard-disabled", body)
        self.assertIn(controlled_acceptance.FIXTURE_COMMIT, body)


if __name__ == "__main__":
    unittest.main()
