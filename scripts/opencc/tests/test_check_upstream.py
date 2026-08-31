from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIRECTORY))

import check_upstream  # noqa: E402


LOCKED = {
    "OPENCC_VERSION": "1.4.2",
    "OPENCC_TAG": "ver.1.4.2",
    "OPENCC_COMMIT": "025f371dc76b598d77384fbdab90c937471844d8",
    "OPENCC_SOURCE_URL": "https://github.com/BYVoid/OpenCC.git",
    "OPENCC_RESOURCE_ASSET": "opencc-v1.4.2-resources.zip",
    "OPENCC_RESOURCE_SHA256": "9ea0d303219b34d014d5c116677b5d325043beafb2c8a62ee889ca67f4d054a5",
    "OPENCC_RESOURCE_SIZE": "1237703",
    "OPENCC_RESOURCE_MANIFEST_VERSION": "1",
}


class UpstreamCheckTest(unittest.TestCase):
    def write_lock(self, root: Path, values: dict[str, str] = LOCKED) -> None:
        lines = [f"{name}={value}" for name, value in values.items()]
        (root / "opencc-upstream.properties").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_current_release_is_accepted_without_case_sensitive_hash_drift(self) -> None:
        latest = dict(LOCKED)
        latest["OPENCC_RESOURCE_SHA256"] = latest["OPENCC_RESOURCE_SHA256"].upper()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_lock(root)
            with mock.patch.object(check_upstream, "validate_release", return_value=latest):
                update, message = check_upstream.compare(root, check_upstream.DEFAULT_API_BASE)
        self.assertFalse(update)
        self.assertIn("OPENCC_UPSTREAM_CURRENT", message)
        self.assertIn("version=1.4.2", message)

    def test_newer_validated_release_is_reported(self) -> None:
        latest = dict(LOCKED)
        latest.update(
            OPENCC_VERSION="1.5.0",
            OPENCC_TAG="ver.1.5.0",
            OPENCC_COMMIT="1" * 40,
            OPENCC_RESOURCE_ASSET="opencc-v1.5.0-resources.zip",
            OPENCC_RESOURCE_SHA256="2" * 64,
            OPENCC_RESOURCE_SIZE="1300000",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_lock(root)
            with mock.patch.object(check_upstream, "validate_release", return_value=latest):
                update, message = check_upstream.compare(root, check_upstream.DEFAULT_API_BASE)
        self.assertTrue(update)
        self.assertIn("locked=1.4.2 latest=1.5.0", message)

    def test_same_version_metadata_drift_is_rejected(self) -> None:
        latest = dict(LOCKED)
        latest["OPENCC_COMMIT"] = "3" * 40
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_lock(root)
            with mock.patch.object(check_upstream, "validate_release", return_value=latest):
                with self.assertRaisesRegex(check_upstream.UpstreamCheckError, "metadata drifted"):
                    check_upstream.compare(root, check_upstream.DEFAULT_API_BASE)

    def test_latest_release_older_than_lock_is_rejected(self) -> None:
        latest = dict(LOCKED)
        latest["OPENCC_VERSION"] = "1.4.1"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_lock(root)
            with mock.patch.object(check_upstream, "validate_release", return_value=latest):
                with self.assertRaisesRegex(check_upstream.UpstreamCheckError, "older than locked"):
                    check_upstream.compare(root, check_upstream.DEFAULT_API_BASE)

    def test_non_semantic_release_version_is_rejected(self) -> None:
        with self.assertRaisesRegex(check_upstream.UpstreamCheckError, "version format"):
            check_upstream.version_tuple("1.4")


if __name__ == "__main__":
    unittest.main()
