from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPT_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIRECTORY))

import verify_apk_variants  # noqa: E402


class VerifyApkVariantsTest(unittest.TestCase):
    def test_standalone_entry_is_required_in_every_target_apk(self) -> None:
        marker = b"Lio/github/supermonster003/autojs6/plugin/opencc/OpenccActivity;"
        self.assertIn(marker, verify_apk_variants.REQUIRED_DEX_MARKERS)

    def test_signed_release_uses_public_artifact_names(self) -> None:
        names = set(verify_apk_variants.expected_apks("release"))
        self.assertIn("app-arm64-v8a-release.apk", names)
        self.assertNotIn("app-arm64-v8a-release-unsigned.apk", names)
        self.assertEqual(5, len(names))

    def test_unsigned_release_uses_clean_gradle_artifact_names(self) -> None:
        names = set(verify_apk_variants.expected_apks("release", unsigned=True))
        self.assertIn("app-arm64-v8a-release-unsigned.apk", names)
        self.assertNotIn("app-arm64-v8a-release.apk", names)
        self.assertEqual(5, len(names))

    def test_unsigned_debug_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            verify_apk_variants.VerificationError,
            "only for release builds",
        ):
            verify_apk_variants.expected_apks("debug", unsigned=True)


if __name__ == "__main__":
    unittest.main()
