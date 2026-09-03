from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class ControlledWorkflowContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.build = (ROOT / ".github/workflows/build.yml").read_text(encoding="utf-8")
        cls.upstream = (ROOT / ".github/workflows/opencc-upstream.yml").read_text(encoding="utf-8")
        cls.merge = (ROOT / ".github/workflows/opencc-auto-merge.yml").read_text(encoding="utf-8")
        cls.controller = (ROOT / "scripts/opencc/merge_upstream.py").read_text(encoding="utf-8")
        cls.native_build = (ROOT / "opencc-native/build.gradle.kts").read_text(encoding="utf-8")

    def test_build_fixture_is_explicit_manual_input(self) -> None:
        self.assertIn("controlled_opencc_acceptance:", self.build)
        self.assertIn("type: boolean", self.build)
        self.assertIn("default: false", self.build)
        self.assertIn("Verify pinned official OpenCC source and resources", self.build)
        self.assertIn("Verify controlled OpenCC acceptance fixture", self.build)
        self.assertIn(
            "if: github.event_name == 'workflow_dispatch' && inputs.controlled_opencc_acceptance == true",
            self.build,
        )
        self.assertIn(
            "if: github.event_name != 'workflow_dispatch' || inputs.controlled_opencc_acceptance != true",
            self.build,
        )
        self.assertIn("ORG_GRADLE_PROJECT_openccControlledAcceptance:", self.build)
        self.assertIn('gradleProperty("openccControlledAcceptance")', self.native_build)
        self.assertIn('"scripts/opencc/controlled_acceptance.py"', self.native_build)
        self.assertIn('else -> error("openccControlledAcceptance must be either true or false")', self.native_build)

    def test_upstream_fixture_is_draft_only_and_policy_locked(self) -> None:
        self.assertIn("controlled_acceptance:", self.upstream)
        self.assertEqual(2, self.upstream.count('test "${OPENCC_AUTOMATION_MODE}" = pr-only'))
        self.assertIn("controlled_acceptance.py inspect", self.upstream)
        self.assertIn("controlled_acceptance.py prepare", self.upstream)
        self.assertIn("controlled_acceptance.py verify", self.upstream)
        self.assertIn("-f controlled_opencc_acceptance=true", self.upstream)
        self.assertIn("pr_args+=(--draft)", self.upstream)
        self.assertNotIn("gh pr merge", self.upstream)
        self.assertNotIn("gh release", self.upstream)
        self.assertNotIn("git tag", self.upstream)

    def test_workflow_run_can_never_select_controlled_evaluation(self) -> None:
        expression = (
            "github.event_name == 'workflow_dispatch' && "
            "inputs.controlled_acceptance == true && 'controlled' || 'official'"
        )
        self.assertIn(expression, self.merge)
        self.assertIn('--candidate-kind "${CANDIDATE_KIND}"', self.merge)
        self.assertIn("needs.evaluate.outputs.candidate_kind == 'official'", self.merge)
        self.assertNotRegex(
            self.merge,
            re.compile(r"Repeat every gate[\s\S]*--candidate-kind", re.MULTILINE),
        )

    def test_controller_forbids_controlled_write_execution(self) -> None:
        self.assertIn('controlled acceptance is hard-limited to pr-only policy', self.controller)
        self.assertIn('--execute is never permitted for a controlled acceptance fixture', self.controller)
        self.assertIn('candidate_kind: str = "official"', self.controller)


if __name__ == "__main__":
    unittest.main()
