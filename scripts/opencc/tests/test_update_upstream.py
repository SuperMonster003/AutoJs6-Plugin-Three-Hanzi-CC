from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIRECTORY))

import check_upstream  # noqa: E402
import update_upstream  # noqa: E402
import verify_upstream  # noqa: E402


LOCKED = {
    "OPENCC_VERSION": "1.4.2",
    "OPENCC_TAG": "ver.1.4.2",
    "OPENCC_COMMIT": "0" * 40,
    "OPENCC_SOURCE_URL": "https://github.com/BYVoid/OpenCC.git",
    "OPENCC_RESOURCE_ASSET": "opencc-v1.4.2-resources.zip",
    "OPENCC_RESOURCE_SHA256": "1" * 64,
    "OPENCC_RESOURCE_SIZE": "3",
    "OPENCC_RESOURCE_MANIFEST_VERSION": "1",
}

LATEST = {
    **LOCKED,
    "OPENCC_VERSION": "1.5.0",
    "OPENCC_TAG": "ver.1.5.0",
    "OPENCC_COMMIT": "2" * 40,
    "OPENCC_RESOURCE_ASSET": "opencc-v1.5.0-resources.zip",
    "OPENCC_RESOURCE_SHA256": "3" * 64,
    "OPENCC_RESOURCE_SIZE": "7",
}


def validated_release(properties: dict[str, str] = LATEST) -> check_upstream.ValidatedRelease:
    return check_upstream.ValidatedRelease(
        properties=dict(properties),
        archive_data=b"new zip",
        release_url="https://github.com/BYVoid/OpenCC/releases/tag/ver.1.5.0",
        release_name="OpenCC 1.5.0",
        release_body="Fix dictionaries and thank @maintainer.",
        published_at="2026-10-01T00:00:00Z",
    )


class UpstreamUpdateTest(unittest.TestCase):
    def make_root(self, directory: str) -> Path:
        root = Path(directory)
        (root / verify_upstream.ASSET_DIRECTORY).mkdir(parents=True)
        (root / verify_upstream.SOURCE_DIRECTORY).mkdir(parents=True)
        (root / verify_upstream.LOCK_FILE).write_bytes(update_upstream.render_lock(LOCKED))
        (root / verify_upstream.ASSET_DIRECTORY / LOCKED["OPENCC_RESOURCE_ASSET"]).write_bytes(b"old")
        return root

    def test_render_lock_has_stable_schema_order(self) -> None:
        text = update_upstream.render_lock(dict(reversed(tuple(LOCKED.items())))).decode("utf-8")
        positions = [text.index(f"{name}=") for name in update_upstream.LOCK_PROPERTY_ORDER]
        self.assertEqual(sorted(positions), positions)
        with self.assertRaisesRegex(update_upstream.UpstreamUpdateError, "lock schema"):
            update_upstream.render_lock({**LOCKED, "UNEXPECTED": "value"})

    def test_resource_path_rejects_traversal_and_wrong_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(update_upstream.UpstreamUpdateError, "Unsafe"):
                update_upstream.safe_resource_path(root, "../opencc-v1.5.0-resources.zip")
            with self.assertRaisesRegex(update_upstream.UpstreamUpdateError, "Unsafe"):
                update_upstream.safe_resource_path(root, "resources.zip")

    def test_current_release_is_a_no_change_result(self) -> None:
        current = validated_release(LOCKED)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with (
                mock.patch.object(update_upstream, "ensure_clean_worktree"),
                mock.patch.object(verify_upstream, "verify"),
                mock.patch.object(verify_upstream, "parse_properties", return_value=dict(LOCKED)),
                mock.patch.object(check_upstream, "download_validated_release", return_value=current),
                mock.patch.object(update_upstream, "apply_validated_release") as apply_release,
            ):
                result = update_upstream.prepare_update(root, check_upstream.DEFAULT_API_BASE)
        self.assertFalse(result.update_available)
        self.assertEqual("", result.branch_name)
        apply_release.assert_not_called()

    def test_new_release_prepares_branch_title_and_review_body(self) -> None:
        release = validated_release()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with (
                mock.patch.object(update_upstream, "ensure_clean_worktree"),
                mock.patch.object(verify_upstream, "verify"),
                mock.patch.object(verify_upstream, "parse_properties", return_value=dict(LOCKED)),
                mock.patch.object(check_upstream, "download_validated_release", return_value=release),
                mock.patch.object(update_upstream, "apply_validated_release") as apply_release,
            ):
                result = update_upstream.prepare_update(root, check_upstream.DEFAULT_API_BASE)
        self.assertTrue(result.update_available)
        self.assertEqual("automation/opencc-1.5.0", result.branch_name)
        self.assertEqual("chore(deps): upgrade OpenCC to 1.5.0", result.commit_title)
        self.assertIn("ver.1.4.2", result.pull_request_body)
        self.assertIn("ver.1.5.0", result.pull_request_body)
        self.assertIn("Never blanket-accept", result.pull_request_body)
        self.assertIn("never enables auto-merge", result.pull_request_body)
        self.assertIn("@<!-- -->maintainer", result.pull_request_body)
        apply_release.assert_called_once_with(root, LOCKED, release)

    def test_apply_updates_only_exact_lock_submodule_and_resources(self) -> None:
        release = validated_release()
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            expected_paths = update_upstream.expected_update_paths(LOCKED, LATEST)
            with (
                mock.patch.object(update_upstream, "ensure_clean_worktree"),
                mock.patch.object(verify_upstream, "verify"),
                mock.patch.object(update_upstream, "update_submodule") as update_submodule,
                mock.patch.object(update_upstream, "git", return_value=LOCKED["OPENCC_COMMIT"]),
                mock.patch.object(update_upstream, "changed_paths", return_value=expected_paths),
            ):
                update_upstream.apply_validated_release(root, LOCKED, release)

            old_resource = root / verify_upstream.ASSET_DIRECTORY / LOCKED["OPENCC_RESOURCE_ASSET"]
            new_resource = root / verify_upstream.ASSET_DIRECTORY / LATEST["OPENCC_RESOURCE_ASSET"]
            actual_lock = verify_upstream.parse_properties(root / verify_upstream.LOCK_FILE)
            self.assertFalse(old_resource.exists())
            self.assertEqual(b"new zip", new_resource.read_bytes())
            self.assertEqual(LATEST, actual_lock)
        update_submodule.assert_called_once_with(root, LATEST["OPENCC_TAG"], LATEST["OPENCC_COMMIT"])

    def test_failed_generated_verification_rolls_back_files(self) -> None:
        release = validated_release()
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            old_resource = root / verify_upstream.ASSET_DIRECTORY / LOCKED["OPENCC_RESOURCE_ASSET"]
            new_resource = root / verify_upstream.ASSET_DIRECTORY / LATEST["OPENCC_RESOURCE_ASSET"]
            with (
                mock.patch.object(update_upstream, "ensure_clean_worktree"),
                mock.patch.object(
                    verify_upstream,
                    "verify",
                    side_effect=[None, verify_upstream.VerificationError("simulated drift")],
                ),
                mock.patch.object(update_upstream, "update_submodule"),
                mock.patch.object(update_upstream, "git", return_value=LOCKED["OPENCC_COMMIT"]),
            ):
                with self.assertRaisesRegex(update_upstream.UpstreamUpdateError, "simulated drift"):
                    update_upstream.apply_validated_release(root, LOCKED, release)

            restored_lock = verify_upstream.parse_properties(root / verify_upstream.LOCK_FILE)
            self.assertEqual(LOCKED, restored_lock)
            self.assertEqual(b"old", old_resource.read_bytes())
            self.assertFalse(new_resource.exists())

    def test_change_inventory_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with mock.patch.object(update_upstream, "changed_paths", return_value={"unexpected.txt"}):
                with self.assertRaisesRegex(update_upstream.UpstreamUpdateError, "inventory"):
                    update_upstream.validate_change_inventory(root, LOCKED, LATEST)

    def test_workflow_outputs_do_not_embed_multiline_body(self) -> None:
        release = validated_release()
        result = update_upstream.UpdateResult(
            True,
            "update",
            dict(LOCKED),
            dict(LATEST),
            release,
            "automation/opencc-1.5.0",
            "chore(deps): upgrade OpenCC to 1.5.0",
            "multiline\nbody",
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "github-output.txt"
            with mock.patch.dict(os.environ, {"GITHUB_OUTPUT": str(output)}):
                update_upstream.append_workflow_outputs(result)
            values = dict(line.split("=", 1) for line in output.read_text(encoding="utf-8").splitlines())
        self.assertEqual("true", values["update_available"])
        self.assertEqual("automation/opencc-1.5.0", values["branch_name"])
        self.assertNotIn("pull_request_body", values)


if __name__ == "__main__":
    unittest.main()
