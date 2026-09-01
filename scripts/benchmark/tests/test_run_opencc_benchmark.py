from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "run_opencc_benchmark.py"
SPEC = importlib.util.spec_from_file_location("run_opencc_benchmark", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
benchmark = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(benchmark)


class ExtractBenchmarkResultTest(unittest.TestCase):
    def test_extracts_the_single_matching_result(self) -> None:
        payload = {
            "schema_version": 1,
            "engine": "official",
            "phase": "first-load",
            "pid": 42,
        }
        output = (
            "INSTRUMENTATION_STATUS: stream="
            f"{benchmark.RESULT_PREFIX}{json.dumps(payload)}\n"
            "Time: 0.1\n\nOK (1 test)\n"
        )

        self.assertEqual(
            payload,
            benchmark.extract_benchmark_result(
                output,
                expected_engine="official",
                expected_phase="first-load",
            ),
        )

    def test_rejects_instrumentation_failure(self) -> None:
        with self.assertRaisesRegex(benchmark.BenchmarkError, "did not pass"):
            benchmark.extract_benchmark_result(
                "FAILURES!!!",
                expected_engine="official",
                expected_phase="first-load",
            )

    def test_rejects_identity_mismatch(self) -> None:
        payload = {
            "schema_version": 1,
            "engine": "legacy",
            "phase": "first-load",
        }
        output = f"{benchmark.RESULT_PREFIX}{json.dumps(payload)}\nOK (1 test)\n"
        with self.assertRaisesRegex(benchmark.BenchmarkError, "identity mismatch"):
            benchmark.extract_benchmark_result(
                output,
                expected_engine="official",
                expected_phase="first-load",
            )


class VerifyEnginePairTest(unittest.TestCase):
    def make_result(self, pid: int, page_size: int = 16384) -> dict[str, object]:
        return {
            "engine": "official",
            "pid": pid,
            "sdk_int": 37,
            "android_release": "17",
            "model": "sdk_gphone16k_x86_64",
            "fingerprint": "example/fingerprint",
            "process_is_64_bit": True,
            "page_size_bytes": page_size,
            "input_utf16_units": 1376,
            "input_code_points": 1312,
        }

    def test_accepts_distinct_processes_with_expected_page_size(self) -> None:
        benchmark.verify_engine_pair(
            self.make_result(100),
            self.make_result(200),
            abi="x86_64",
            expected_page_size=16384,
        )

    def test_rejects_reused_process(self) -> None:
        with self.assertRaisesRegex(benchmark.BenchmarkError, "same process"):
            benchmark.verify_engine_pair(
                self.make_result(100),
                self.make_result(100),
                abi="x86_64",
                expected_page_size=16384,
            )

    def test_rejects_wrong_page_size(self) -> None:
        with self.assertRaisesRegex(benchmark.BenchmarkError, "PAGE_SIZE"):
            benchmark.verify_engine_pair(
                self.make_result(100, 4096),
                self.make_result(200, 4096),
                abi="x86_64",
                expected_page_size=16384,
            )


class ApkSizeCollectionTest(unittest.TestCase):
    def test_collects_exact_current_and_baseline_sets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            current = root / "app" / "build" / "outputs" / "apk" / "release"
            baseline = root / "app" / "releases"
            current.mkdir(parents=True)
            baseline.mkdir(parents=True)
            for index, abi in enumerate(benchmark.RELEASE_ABIS, start=1):
                (current / f"app-{abi}-release.apk").write_bytes(b"x" * index)
                (baseline / f"autojs6-plugin-opencc-v1.0.2-{abi}-deadbeef.apk").write_bytes(
                    b"y" * (index + 10)
                )

            sizes = benchmark.collect_apk_sizes(root, "1.0.2")

            self.assertEqual(set(benchmark.RELEASE_ABIS), set(sizes["current"]))
            self.assertEqual(1, sizes["current"]["arm64-v8a"])
            self.assertEqual(15, sizes["baseline"]["universal"])


if __name__ == "__main__":
    unittest.main()
