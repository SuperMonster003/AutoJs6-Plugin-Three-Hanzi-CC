from __future__ import annotations

import sys
import unittest
from copy import deepcopy
from pathlib import Path


SCRIPT_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIRECTORY))

import verify_apk_variants  # noqa: E402


class VerifyApkVariantsTest(unittest.TestCase):
    def expected_manifest(self) -> verify_apk_variants.ManifestElement:
        element = verify_apk_variants.ManifestElement
        permission = verify_apk_variants.PLUGIN_PERMISSION
        package_name = verify_apk_variants.APPLICATION_ID
        launcher = element(
            "activity",
            {"name": f"{package_name}.OpenccActivity", "exported": True},
            [
                element(
                    "intent-filter",
                    {},
                    [
                        element("action", {"name": "android.intent.action.MAIN"}),
                        element("category", {"name": "android.intent.category.LAUNCHER"}),
                    ],
                ),
            ],
        )
        wake = element(
            "activity",
            {
                "name": f"{package_name}.WakeActivity",
                "exported": True,
                "permission": permission,
                "excludeFromRecents": True,
                "finishOnTaskLaunch": True,
            },
            [
                element(
                    "intent-filter",
                    {},
                    [
                        element("action", {"name": "org.autojs.plugin.action.WAKE"}),
                        element("category", {"name": "android.intent.category.DEFAULT"}),
                    ],
                ),
            ],
        )
        service = element(
            "service",
            {
                "name": f"{package_name}.OpenccPluginService",
                "exported": True,
                "permission": permission,
            },
            [
                element(
                    "intent-filter",
                    {},
                    [
                        element("action", {"name": "org.autojs.plugin.OPENCC"}),
                        element("category", {"name": "opencc"}),
                    ],
                ),
            ],
        )
        return element(
            "manifest",
            {"package": package_name},
            [
                element("uses-permission", {"name": permission}),
                element(
                    "application",
                    {"allowBackup": False, "usesCleartextTraffic": False},
                    [launcher, wake, service],
                ),
            ],
        )

    def test_standalone_entry_is_required_in_every_target_apk(self) -> None:
        marker = b"Lio/github/supermonster003/autojs6/plugin/opencc/OpenccActivity;"
        self.assertIn(marker, verify_apk_variants.REQUIRED_DEX_MARKERS)

    def test_opencc_api_compatibility_artifact_is_pinned(self) -> None:
        self.assertEqual(
            "5f3001e28fb4c4967b0a4faeb4547a41a679b35cbd209d272a6a79f7ba00ab45",
            verify_apk_variants.OPENCC_API_SHA256,
        )
        verify_apk_variants.verify_api_artifact()

    def test_signed_release_uses_public_artifact_names(self) -> None:
        names = set(verify_apk_variants.expected_apks("release"))
        self.assertIn("app-arm64-v8a-release.apk", names)
        self.assertNotIn("app-arm64-v8a-release-unsigned.apk", names)
        self.assertEqual(5, len(names))

    def test_expected_manifest_surface_passes(self) -> None:
        verify_apk_variants.verify_manifest_tree(self.expected_manifest(), "fixture.apk")

    def test_internet_permission_is_rejected(self) -> None:
        manifest = self.expected_manifest()
        manifest.children.insert(
            0,
            verify_apk_variants.ManifestElement(
                "uses-permission",
                {"name": "android.permission.INTERNET"},
            ),
        )
        with self.assertRaisesRegex(verify_apk_variants.VerificationError, "permissions mismatch"):
            verify_apk_variants.verify_manifest_tree(manifest, "fixture.apk")

    def test_manifest_receiver_is_rejected(self) -> None:
        manifest = deepcopy(self.expected_manifest())
        application = next(child for child in manifest.children if child.name == "application")
        application.children.append(
            verify_apk_variants.ManifestElement(
                "receiver",
                {"name": f"{verify_apk_variants.APPLICATION_ID}.UnexpectedReceiver"},
            ),
        )
        with self.assertRaisesRegex(verify_apk_variants.VerificationError, "unexpected exported-surface"):
            verify_apk_variants.verify_manifest_tree(manifest, "fixture.apk")

    def test_share_receiver_filter_is_rejected(self) -> None:
        manifest = deepcopy(self.expected_manifest())
        application = next(child for child in manifest.children if child.name == "application")
        launcher = next(
            child
            for child in application.children
            if child.attributes.get("name", "").endswith(".OpenccActivity")
        )
        launcher.children[0].children[0].attributes["name"] = "android.intent.action.SEND"
        with self.assertRaisesRegex(verify_apk_variants.VerificationError, "only MAIN/LAUNCHER"):
            verify_apk_variants.verify_manifest_tree(manifest, "fixture.apk")

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
