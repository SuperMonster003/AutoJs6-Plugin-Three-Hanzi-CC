#!/usr/bin/env python3
"""Run the opt-in official OpenCC device benchmark and persist reproducible results."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence


TARGET_PACKAGE = "io.github.supermonster003.autojs6.plugin.opencc"
TEST_PACKAGE = f"{TARGET_PACKAGE}.test"
RUNNER = f"{TEST_PACKAGE}/androidx.test.runner.AndroidJUnitRunner"
BENCHMARK_CLASS = (
    "io.github.supermonster003.autojs6.plugin.opencc."
    "OpenccPerformanceBenchmarkTest"
)
RESULT_PREFIX = "OPENCC_BENCHMARK_JSON="
ENGINES = ("official",)
PHASES = ("first-load", "steady-state")
ABIS = ("arm64-v8a", "armeabi-v7a", "x86_64", "x86")
RELEASE_ABIS = (*ABIS, "universal")
CURRENT_APK_PATTERN = re.compile(
    r"^app-(arm64-v8a|armeabi-v7a|x86_64|x86|universal)-release\.apk$"
)
BASELINE_APK_PATTERN = re.compile(
    r"^autojs6-plugin-opencc-v(?P<version>[^-]+)-"
    r"(?P<abi>arm64-v8a|armeabi-v7a|x86_64|x86|universal)-[0-9a-fA-F]+\.apk$"
)


class BenchmarkError(RuntimeError):
    """Raised when the device benchmark cannot produce trustworthy evidence."""


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=root, help="Repository root")
    parser.add_argument("--serial", required=True, help="ADB device serial")
    parser.add_argument("--abi", required=True, choices=ABIS, help="Target APK ABI")
    parser.add_argument(
        "--engines",
        nargs="+",
        choices=ENGINES,
        default=list(ENGINES),
        help="Engines to measure in isolated installs",
    )
    parser.add_argument("--adb", default="adb", help="ADB executable")
    parser.add_argument("--target-apk", type=Path, help="Debug target APK override")
    parser.add_argument("--test-apk", type=Path, help="Debug instrumentation APK override")
    parser.add_argument(
        "--baseline-version",
        default="1.0.2",
        help="Version in app/releases used for the APK size comparison",
    )
    parser.add_argument(
        "--expected-page-size",
        type=int,
        choices=(4096, 16384),
        help="Fail unless the benchmark process reports this page size",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=300,
        help="Timeout for each instrumentation phase",
    )
    parser.add_argument(
        "--allow-package-reset",
        action="store_true",
        help=(
            "Allow uninstalling an already installed target/test package. This erases "
            "that package's app data."
        ),
    )
    parser.add_argument(
        "--keep-installed",
        action="store_true",
        help="Leave the benchmark APKs installed after completion",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        help="Raw JSON output path (default: build/reports/opencc-benchmark/...)",
    )
    parser.add_argument(
        "--output-markdown",
        type=Path,
        help="Markdown output path (default: next to JSON)",
    )
    return parser.parse_args(argv)


def run_command(
    command: Sequence[str | os.PathLike[str]],
    *,
    cwd: Path,
    timeout: int | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    rendered = [os.fspath(part) for part in command]
    completed = subprocess.run(
        rendered,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )
    if check and completed.returncode != 0:
        raise BenchmarkError(
            f"Command failed ({completed.returncode}): {' '.join(rendered)}\n"
            f"{completed.stdout}"
        )
    return completed


def adb_command(
    adb: str,
    serial: str,
    arguments: Sequence[str | os.PathLike[str]],
    *,
    root: Path,
    timeout: int | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return run_command(
        [adb, "-s", serial, *arguments],
        cwd=root,
        timeout=timeout,
        check=check,
    )


def package_path(adb: str, serial: str, package: str, root: Path) -> str | None:
    completed = adb_command(
        adb,
        serial,
        ["shell", "pm", "path", package],
        root=root,
        check=False,
    )
    paths = [line.removeprefix("package:").strip() for line in completed.stdout.splitlines()]
    paths = [path for path in paths if path]
    return paths[0] if paths else None


def uninstall_packages(adb: str, serial: str, root: Path) -> None:
    for package in (TEST_PACKAGE, TARGET_PACKAGE):
        adb_command(adb, serial, ["uninstall", package], root=root, check=False)


def install_apks(
    adb: str,
    serial: str,
    target_apk: Path,
    test_apk: Path,
    root: Path,
) -> None:
    for apk in (target_apk, test_apk):
        completed = adb_command(
            adb,
            serial,
            ["install", "-r", "-t", apk],
            root=root,
            timeout=120,
        )
        if "Success" not in completed.stdout:
            raise BenchmarkError(f"ADB did not confirm installation of {apk}:\n{completed.stdout}")


def force_stop_packages(adb: str, serial: str, root: Path) -> None:
    for package in (TEST_PACKAGE, TARGET_PACKAGE):
        adb_command(
            adb,
            serial,
            ["shell", "am", "force-stop", package],
            root=root,
            check=False,
        )


def extract_benchmark_result(
    output: str,
    *,
    expected_engine: str,
    expected_phase: str,
) -> dict[str, Any]:
    if "OK (1 test)" not in output or "FAILURES!!!" in output:
        raise BenchmarkError(f"Instrumentation did not pass:\n{output}")

    results: list[dict[str, Any]] = []
    for line in output.splitlines():
        marker = line.find(RESULT_PREFIX)
        if marker < 0:
            continue
        payload = line[marker + len(RESULT_PREFIX) :].strip()
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as error:
            raise BenchmarkError(f"Invalid benchmark JSON: {payload}") from error
        if not isinstance(parsed, dict):
            raise BenchmarkError("Benchmark result must be a JSON object")
        results.append(parsed)

    if len(results) != 1:
        raise BenchmarkError(f"Expected one benchmark result, found {len(results)}")
    result = results[0]
    if result.get("schema_version") != 1:
        raise BenchmarkError(f"Unsupported benchmark schema: {result.get('schema_version')}")
    if result.get("engine") != expected_engine or result.get("phase") != expected_phase:
        raise BenchmarkError(
            "Benchmark result identity mismatch: "
            f"expected {expected_engine}/{expected_phase}, found "
            f"{result.get('engine')}/{result.get('phase')}"
        )
    return result


def run_phase(
    *,
    adb: str,
    serial: str,
    engine: str,
    phase: str,
    root: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    completed = adb_command(
        adb,
        serial,
        [
            "shell",
            "am",
            "instrument",
            "-w",
            "-r",
            "-e",
            "class",
            BENCHMARK_CLASS,
            "-e",
            "opencc_benchmark_engine",
            engine,
            "-e",
            "opencc_benchmark_phase",
            phase,
            RUNNER,
        ],
        root=root,
        timeout=timeout_seconds,
    )
    result = extract_benchmark_result(
        completed.stdout,
        expected_engine=engine,
        expected_phase=phase,
    )
    print(
        f"OPENCC_BENCHMARK_OK engine={engine} phase={phase} "
        f"pid={result['pid']}",
        flush=True,
    )
    return result


def verify_engine_pair(
    first_load: dict[str, Any],
    steady_state: dict[str, Any],
    *,
    abi: str,
    expected_page_size: int | None,
) -> None:
    if first_load["pid"] == steady_state["pid"]:
        raise BenchmarkError("First-load and steady-state phases reused the same process")
    stable_fields = (
        "engine",
        "sdk_int",
        "android_release",
        "model",
        "fingerprint",
        "process_is_64_bit",
        "page_size_bytes",
        "input_utf16_units",
        "input_code_points",
    )
    for field in stable_fields:
        if first_load.get(field) != steady_state.get(field):
            raise BenchmarkError(
                f"Benchmark environment changed between phases for {field}: "
                f"{first_load.get(field)!r} != {steady_state.get(field)!r}"
            )
    expected_64_bit = abi in {"arm64-v8a", "x86_64"}
    if first_load.get("process_is_64_bit") is not expected_64_bit:
        raise BenchmarkError(
            f"APK ABI {abi} expected process_is_64_bit={expected_64_bit}, "
            f"found {first_load.get('process_is_64_bit')}"
        )
    if expected_page_size is not None and first_load.get("page_size_bytes") != expected_page_size:
        raise BenchmarkError(
            f"Expected PAGE_SIZE={expected_page_size}, "
            f"found {first_load.get('page_size_bytes')}"
        )


def file_identity(path: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return {
        "path": path.as_posix(),
        "size_bytes": path.stat().st_size,
        "sha256": digest.hexdigest(),
    }


def collect_apk_sizes(root: Path, baseline_version: str) -> dict[str, dict[str, int]]:
    current_directory = root / "app" / "build" / "outputs" / "apk" / "release"
    baseline_directory = root / "app" / "releases"
    current: dict[str, int] = {}
    baseline: dict[str, int] = {}

    for path in current_directory.glob("*.apk"):
        match = CURRENT_APK_PATTERN.fullmatch(path.name)
        if match:
            current[match.group(1)] = path.stat().st_size
    for path in baseline_directory.glob("*.apk"):
        match = BASELINE_APK_PATTERN.fullmatch(path.name)
        if match and match.group("version") == baseline_version:
            baseline[match.group("abi")] = path.stat().st_size

    expected = set(RELEASE_ABIS)
    if set(current) != expected:
        raise BenchmarkError(
            f"Expected current release APK sizes for {sorted(expected)}, found {sorted(current)}"
        )
    if set(baseline) != expected:
        raise BenchmarkError(
            f"Expected v{baseline_version} APK sizes for {sorted(expected)}, "
            f"found {sorted(baseline)}"
        )
    return {"baseline": baseline, "current": current}


def git_state(root: Path) -> dict[str, Any]:
    commit = run_command(["git", "rev-parse", "HEAD"], cwd=root).stdout.strip()
    status = run_command(["git", "status", "--porcelain"], cwd=root).stdout
    return {"commit": commit, "dirty": bool(status.strip())}


def build_report(
    *,
    root: Path,
    serial: str,
    abi: str,
    target_apk: Path,
    test_apk: Path,
    baseline_version: str,
    results: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    first_result = next(iter(results.values()))["first-load"]
    return {
        "schema_version": 1,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "repository": git_state(root),
        "device": {
            "serial": serial,
            "model": first_result["model"],
            "fingerprint": first_result["fingerprint"],
            "sdk_int": first_result["sdk_int"],
            "android_release": first_result["android_release"],
            "apk_abi": abi,
            "process_is_64_bit": first_result["process_is_64_bit"],
            "page_size_bytes": first_result["page_size_bytes"],
        },
        "artifacts": {
            "target_apk": file_identity(target_apk),
            "test_apk": file_identity(test_apk),
        },
        "workload": {
            "conversion_type": "S2T",
            "input_utf16_units": first_result["input_utf16_units"],
            "input_code_points": first_result["input_code_points"],
            "warm_iterations": next(iter(results.values()))["steady-state"]["warm_iterations"],
            "batch_size": next(iter(results.values()))["steady-state"]["batch_size"],
        },
        "engines": results,
        "release_apk_sizes": {
            "baseline_version": baseline_version,
            **collect_apk_sizes(root, baseline_version),
        },
    }


def format_milliseconds(nanoseconds: int) -> str:
    return f"{nanoseconds / 1_000_000:.3f} ms"


def format_kibibytes(kibibytes: int) -> str:
    return f"{kibibytes / 1024:.2f} MiB"


def format_bytes(value: int) -> str:
    return f"{value:,} B"


def render_markdown(report: dict[str, Any]) -> str:
    device = report["device"]
    workload = report["workload"]
    engines = report["engines"]
    lines = [
        "# OpenCC M4-B 设备基准原始报告",
        "",
        f"生成时间 (UTC): `{report['generated_at_utc']}`",
        "",
        "该报告是一次设备实测快照，不是跨设备的绝对性能承诺。首次加载阶段从清空对应引擎资源",
        "开始；随后强制停止应用，并在新的 PID 中测量已安装资源的冷转换、热转换和批量负载。",
        "官方引擎在隔离的全新安装中运行。历史迁移基线保存在工程文档中，不再打包进测试 APK。",
        "",
        "## 环境",
        "",
        "| 项目 | 值 |",
        "|---|---|",
        f"| 设备 | `{device['model']}` |",
        f"| Android | `{device['android_release']}` / API `{device['sdk_int']}` |",
        f"| 指纹 | `{device['fingerprint']}` |",
        f"| APK ABI | `{device['apk_abi']}` |",
        f"| 进程位数 | `{'64' if device['process_is_64_bit'] else '32'}-bit` |",
        f"| PAGE_SIZE | `{device['page_size_bytes']}` bytes |",
        f"| 仓库提交 | `{report['repository']['commit']}` |",
        f"| 工作区 | `{'dirty' if report['repository']['dirty'] else 'clean'}` |",
        "",
        "## 工作负载",
        "",
        f"- 转换类型: `{workload['conversion_type']}`。",
        f"- 单次输入: {workload['input_utf16_units']:,} UTF-16 code units / "
        f"{workload['input_code_points']:,} Unicode code points。",
        f"- 热转换: {workload['warm_iterations']} 次；表中记录中位数与 p95。",
        f"- 批量负载: {workload['batch_size']} 段顺序转换。",
        "- 峰值内存为测试进程自采样 PSS；时间与内存采集不设置发布阈值，升级时用于人工比较。",
        "",
        "## 时间",
        "",
        "| 引擎 | 首次安装后首转 | 新进程冷转 | 热转中位数 | 热转 p95 | 批量总耗时 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for engine in ENGINES:
        if engine not in engines:
            continue
        first = engines[engine]["first-load"]
        steady = engines[engine]["steady-state"]
        lines.append(
            f"| `{engine}` | {format_milliseconds(first['first_load_ns'])} | "
            f"{format_milliseconds(steady['cold_conversion_ns'])} | "
            f"{format_milliseconds(steady['warm_median_ns'])} | "
            f"{format_milliseconds(steady['warm_p95_ns'])} | "
            f"{format_milliseconds(steady['batch_total_ns'])} |"
        )

    lines.extend(
        [
            "",
            "## 内存与资源",
            "",
            "| 引擎 | 首次加载 PSS 增量 | 稳态负载峰值 PSS | 相对进程基线增量 | 安装后资源 |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for engine in ENGINES:
        if engine not in engines:
            continue
        first = engines[engine]["first-load"]
        steady = engines[engine]["steady-state"]
        lines.append(
            f"| `{engine}` | {format_kibibytes(first['pss_delta_kb'])} | "
            f"{format_kibibytes(steady['memory_peak']['total_pss_kb'])} | "
            f"{format_kibibytes(steady['peak_pss_delta_kb'])} | "
            f"{format_bytes(first['resource_bytes'])} |"
        )

    sizes = report["release_apk_sizes"]
    lines.extend(
        [
            "",
            "## Minified release APK 体积",
            "",
            f"基线版本: `v{sizes['baseline_version']}`。",
            "",
            "| ABI | 基线 | 当前 | 增量 |",
            "|---|---:|---:|---:|",
        ]
    )
    for abi in RELEASE_ABIS:
        baseline = sizes["baseline"][abi]
        current = sizes["current"][abi]
        delta = current - baseline
        percent = delta * 100 / baseline
        lines.append(
            f"| `{abi}` | {format_bytes(baseline)} | {format_bytes(current)} | "
            f"{delta:+,} B ({percent:+.1f}%) |"
        )
    lines.append("")
    return "\n".join(lines)


def resolve_adb(candidate: str) -> str:
    resolved = shutil.which(candidate)
    if resolved:
        return resolved
    path = Path(candidate)
    if path.is_file():
        return os.fspath(path.resolve())
    raise BenchmarkError(f"ADB executable not found: {candidate}")


def require_file(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not resolved.is_file():
        raise BenchmarkError(f"{label} is missing: {resolved}")
    return resolved


def default_output_paths(
    root: Path,
    serial: str,
    abi: str,
    output_json: Path | None,
    output_markdown: Path | None,
) -> tuple[Path, Path]:
    safe_serial = re.sub(r"[^A-Za-z0-9_.-]+", "_", serial)
    json_path = output_json or (
        root / "build" / "reports" / "opencc-benchmark" / f"{safe_serial}-{abi}.json"
    )
    markdown_path = output_markdown or json_path.with_suffix(".md")
    return json_path.resolve(), markdown_path.resolve()


def run_benchmark(args: argparse.Namespace) -> tuple[dict[str, Any], Path, Path]:
    root = args.root.resolve()
    if not (root / "settings.gradle.kts").is_file():
        raise BenchmarkError(f"Not an OpenCC plugin repository root: {root}")
    adb = resolve_adb(args.adb)
    target_apk = require_file(
        args.target_apk or root / "app" / "build" / "outputs" / "apk" / "debug" / f"app-{args.abi}-debug.apk",
        "Target APK",
    )
    test_apk = require_file(
        args.test_apk
        or root / "app" / "build" / "outputs" / "apk" / "androidTest" / "debug" / "app-debug-androidTest.apk",
        "Instrumentation APK",
    )
    json_path, markdown_path = default_output_paths(
        root,
        args.serial,
        args.abi,
        args.output_json,
        args.output_markdown,
    )

    state = adb_command(adb, args.serial, ["get-state"], root=root).stdout.strip()
    if state != "device":
        raise BenchmarkError(f"ADB device is not ready: {args.serial} ({state!r})")
    preinstalled = {
        package: package_path(adb, args.serial, package, root)
        for package in (TARGET_PACKAGE, TEST_PACKAGE)
    }
    existing = {package: path for package, path in preinstalled.items() if path}
    if existing and not args.allow_package_reset:
        details = ", ".join(f"{package}={path}" for package, path in existing.items())
        raise BenchmarkError(
            "Benchmarking requires isolated uninstall/reinstall cycles and would erase app data. "
            f"Packages already installed: {details}. Use --allow-package-reset only on a disposable "
            "test device or after explicitly accepting that reset."
        )

    results: dict[str, dict[str, dict[str, Any]]] = {}
    try:
        for engine in dict.fromkeys(args.engines):
            print(f"Preparing isolated {engine} benchmark on {args.serial}...", flush=True)
            uninstall_packages(adb, args.serial, root)
            install_apks(adb, args.serial, target_apk, test_apk, root)
            first_load = run_phase(
                adb=adb,
                serial=args.serial,
                engine=engine,
                phase="first-load",
                root=root,
                timeout_seconds=args.timeout_seconds,
            )
            force_stop_packages(adb, args.serial, root)
            steady_state = run_phase(
                adb=adb,
                serial=args.serial,
                engine=engine,
                phase="steady-state",
                root=root,
                timeout_seconds=args.timeout_seconds,
            )
            verify_engine_pair(
                first_load,
                steady_state,
                abi=args.abi,
                expected_page_size=args.expected_page_size,
            )
            results[engine] = {
                "first-load": first_load,
                "steady-state": steady_state,
            }
    finally:
        if not args.keep_installed:
            uninstall_packages(adb, args.serial, root)

    report = build_report(
        root=root,
        serial=args.serial,
        abi=args.abi,
        target_apk=target_apk,
        test_apk=test_apk,
        baseline_version=args.baseline_version,
        results=results,
    )
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return report, json_path, markdown_path


def main(argv: Sequence[str] | None = None) -> int:
    try:
        report, json_path, markdown_path = run_benchmark(parse_args(argv))
    except (BenchmarkError, subprocess.TimeoutExpired) as error:
        print(f"OPENCC_BENCHMARK_FAILED: {error}", file=sys.stderr)
        return 1
    device = report["device"]
    print(
        "OPENCC_BENCHMARK_COMPLETE "
        f"model={device['model']} api={device['sdk_int']} abi={device['apk_abi']} "
        f"page_size={device['page_size_bytes']}"
    )
    print(f"JSON: {json_path}")
    print(f"Markdown: {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
