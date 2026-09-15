import importlib.util
from pathlib import Path
import unittest


SPEC = importlib.util.spec_from_file_location("phased_tests", Path(__file__).resolve().parents[1] / "run_phased_device_tests.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class PhaseResultsTest(unittest.TestCase):
    def test_completed_phase_is_accepted(self):
        RUNNER.require_pass("INSTRUMENTATION_STATUS_CODE: 0\nOK (1 test)\nINSTRUMENTATION_CODE: -1\n")

    def test_failed_missing_and_skipped_phases_are_rejected(self):
        for output in (
            "INSTRUMENTATION_CODE: -1\n",
            "FAILURES!!!\nTests run: 1, Failures: 1\n",
            "INSTRUMENTATION_FAILED: runner unavailable\n",
            "INSTRUMENTATION_STATUS_CODE: -3\nOK (1 test)\n",
            "INSTRUMENTATION_STATUS_CODE: -4\nOK (1 test)\n",
            "OK (0 tests)\n",
        ):
            with self.subTest(output=output), self.assertRaises(RuntimeError):
                RUNNER.require_pass(output)


if __name__ == "__main__":
    unittest.main()
