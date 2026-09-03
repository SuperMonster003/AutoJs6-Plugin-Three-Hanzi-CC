from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github" / "workflows" / "opencc-release.yml"


class ReleaseEnvironmentWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")
        preflight_start = cls.text.index("  verify-release-environment:")
        candidate_start = cls.text.index("  build-signed-candidate:")
        cls.preflight = cls.text[preflight_start:candidate_start]
        cls.candidate = cls.text[candidate_start:]

    def test_controller_has_only_manual_typed_operations(self) -> None:
        self.assertIn("  workflow_dispatch:\n", self.text)
        self.assertIn("      operation:\n", self.text)
        self.assertIn("          - preflight\n", self.text)
        self.assertIn("          - candidate\n", self.text)
        self.assertIn("      source_sha:\n", self.text)
        self.assertNotIn("  pull_request:", self.text)
        self.assertNotIn("  pull_request_target:", self.text)
        self.assertNotIn("  push:", self.text)
        self.assertNotIn("  schedule:", self.text)

    def test_signing_secrets_are_scoped_to_the_release_environment(self) -> None:
        self.assertEqual(2, self.text.count("      name: opencc-release"))
        self.assertNotIn("      url:", self.text)
        for name in (
            "OPENCC_RELEASE_KEYSTORE_BASE64",
            "OPENCC_RELEASE_STORE_PASSWORD",
            "OPENCC_RELEASE_KEY_ALIAS",
            "OPENCC_RELEASE_KEY_PASSWORD",
            "OPENCC_RELEASE_EXPECTED_KEYSTORE_SHA256",
            "OPENCC_RELEASE_EXPECTED_CERT_SHA256",
        ):
            self.assertIn(name, self.text)
        self.assertNotIn("cache:", self.text)
        self.assertIn('jarsigner -verify "${signed_jar}"', self.preflight)
        self.assertNotIn("jarsigner -verify -strict", self.text)

    def test_index_token_remains_preflight_only_and_least_privilege(self) -> None:
        self.assertIn(
            "uses: actions/create-github-app-token@bcd2ba49218906704ab6c1aa796996da409d3eb1 # v3.2.0",
            self.preflight,
        )
        self.assertIn("client-id: ${{ vars.OPENCC_INDEX_APP_CLIENT_ID }}", self.preflight)
        self.assertIn("private-key: ${{ secrets.OPENCC_INDEX_APP_PRIVATE_KEY }}", self.preflight)
        self.assertIn("repositories: AutoJs6-Official-Plugins-Index", self.preflight)
        self.assertIn("permission-actions: write", self.preflight)
        self.assertNotIn("app-id:", self.text)
        self.assertNotIn("OPENCC_INDEX_APP_PRIVATE_KEY", self.candidate)
        self.assertNotIn("create-github-app-token", self.candidate)

    def test_candidate_is_bound_to_exact_current_master_sha_and_pr_only_mode(self) -> None:
        for evidence in (
            'test "${AUTOMATION_MODE}" = pr-only',
            '[[ "${SOURCE_SHA}" =~ ^[0-9a-f]{40}$ ]]',
            'test "${SOURCE_SHA}" = "${GITHUB_SHA}"',
            'test "${remote_master_sha}" = "${SOURCE_SHA}"',
            'test "$(git rev-parse HEAD)" = "${SOURCE_SHA}"',
            'ref: ${{ inputs.source_sha }}',
            "persist-credentials: false",
            "fetch-depth: 0",
            "submodules: recursive",
        ):
            self.assertIn(evidence, self.candidate)

    def test_candidate_actions_are_commit_pinned(self) -> None:
        for action in (
            "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7",
            "actions/setup-java@dd06d9cba3e5552c54d9f8ea23572deb30010f7c # v6",
            "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7",
            "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7",
        ):
            self.assertIn(action, self.candidate)

    def test_candidate_rebuilds_and_runs_content_signing_and_size_gates(self) -> None:
        for evidence in (
            "python scripts/opencc/verify_upstream.py --root .",
            "bash ./gradlew :app:assembleRelease --no-daemon --stacktrace",
            "python scripts/ci/verify_apk_variants.py",
            '"${zipalign}" -c -P 16 -v 4 "${apk}"',
            "python scripts/release/prepare_release.py",
            "python scripts/release/prepare_candidate.py",
            '--expected-signer-sha256 "${EXPECTED_CERT_SHA256}"',
        ):
            self.assertIn(evidence, self.candidate)
        self.assertTrue((ROOT / "scripts" / "release" / "candidate-baseline.json").is_file())

    def test_candidate_signing_material_is_ephemeral_and_not_uploaded(self) -> None:
        self.assertIn('signing_directory="${RUNNER_TEMP}/opencc-candidate-signing"', self.candidate)
        self.assertIn('signing_properties="${GITHUB_WORKSPACE}/sign.properties"', self.candidate)
        self.assertIn("trap cleanup_signing_material EXIT HUP INT TERM", self.candidate)
        self.assertIn('rm -f -- "${signing_properties}"', self.candidate)
        self.assertIn('rm -rf -- "${signing_directory}"', self.candidate)
        self.assertIn("set +x", self.candidate)
        self.assertIn("unset KEYSTORE_BASE64 STORE_PASSWORD KEY_ALIAS KEY_PASSWORD", self.candidate)
        self.assertIn("path: ${{ steps.candidate.outputs.bundle_path }}", self.candidate)
        self.assertNotIn("path: .\n", self.candidate)
        self.assertNotIn("path: app/build", self.candidate)
        self.assertIn("include-hidden-files: false", self.candidate)

    def test_candidate_artifact_is_public_bundle_only(self) -> None:
        self.assertIn('test -f "${bundle_path}/CANDIDATE.json"', self.candidate)
        self.assertIn("-eq 8", self.candidate)
        self.assertIn("opencc-signed-candidate-v", self.candidate)
        self.assertIn("retention-days: 14", self.candidate)
        self.assertIn("compression-level: 0", self.candidate)

    def test_controller_cannot_publish_or_modify_repository_state(self) -> None:
        self.assertIn("permissions:\n  contents: read\n", self.text)
        for forbidden in (
            "gh release create",
            "gh release upload",
            "gh workflow run",
            "git push",
            "pull-requests: write",
            "contents: write",
            "\n  actions: write",
            "skip-token-revoke",
        ):
            self.assertNotIn(forbidden, self.text)


if __name__ == "__main__":
    unittest.main()
