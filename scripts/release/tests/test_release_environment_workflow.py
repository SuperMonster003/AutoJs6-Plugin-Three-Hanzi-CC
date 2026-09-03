from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github" / "workflows" / "opencc-release.yml"


class ReleaseEnvironmentWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_preflight_has_no_automatic_or_untrusted_trigger(self) -> None:
        self.assertIn("  workflow_dispatch:\n", self.text)
        self.assertNotIn("  pull_request:", self.text)
        self.assertNotIn("  pull_request_target:", self.text)
        self.assertNotIn("  push:", self.text)
        self.assertNotIn("  schedule:", self.text)

    def test_signing_secrets_are_scoped_to_the_release_environment(self) -> None:
        self.assertIn("name: opencc-release", self.text)
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
        self.assertNotIn("upload-artifact", self.text)
        self.assertNotIn("cache:", self.text)
        self.assertIn('jarsigner -verify "${signed_jar}"', self.text)
        self.assertNotIn("jarsigner -verify -strict", self.text)

    def test_index_token_uses_the_client_id_and_exact_repository_scope(self) -> None:
        self.assertIn(
            "uses: actions/create-github-app-token@bcd2ba49218906704ab6c1aa796996da409d3eb1 # v3.2.0",
            self.text,
        )
        self.assertIn("client-id: ${{ vars.OPENCC_INDEX_APP_CLIENT_ID }}", self.text)
        self.assertIn("private-key: ${{ secrets.OPENCC_INDEX_APP_PRIVATE_KEY }}", self.text)
        self.assertIn("repositories: AutoJs6-Official-Plugins-Index", self.text)
        self.assertIn("permission-actions: write", self.text)
        self.assertNotIn("app-id:", self.text)

    def test_preflight_cannot_publish(self) -> None:
        for forbidden in (
            "gh release create",
            "gh release upload",
            "gh workflow run",
            "git push",
            "pull-requests: write",
            "contents: write",
        ):
            self.assertNotIn(forbidden, self.text)


if __name__ == "__main__":
    unittest.main()
