#!/usr/bin/env python3
"""Run OpenCC's optional resource/restart/screenshot fixtures in fresh Android processes."""

import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "io.github.supermonster003.autojs6.plugin.three.hanzi.cc"
PHASES = (
    ("entry-standalone", "OpenccEntryResourceTest", "opencc_entry_resource_phase", "standalone"),
    ("entry-binder", "OpenccEntryResourceTest", "opencc_entry_resource_phase", "binder"),
    ("restart-prepare", "OpenccResourceRestartTest", "opencc_resource_restart_phase", "prepare"),
    ("restart-verify", "OpenccResourceRestartTest", "opencc_resource_restart_phase", "verify"),
    ("screenshot", "OpenccDocumentationScreenshotTest", "opencc_screenshot_file", "device-test.png"),
)


def require_pass(output):
    # adb itself can exit zero for failed and skipped instrumentation tests.
    if not re.search(r"^OK \(1 test\)\s*$", output, re.MULTILINE) or re.search(
        r"INSTRUMENTATION_STATUS_CODE: -(?:1|2|3|4)\b|FAILURES!!!|INSTRUMENTATION_FAILED|Process crashed",
        output,
    ):
        raise RuntimeError("The phase failed or was skipped; inspect its instrumentation log")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True)
    parser.add_argument("--adb", default="adb")
    parser.add_argument("--output", type=Path, default=ROOT / "build/verification/phased-tests")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "results.json").unlink(missing_ok=True)

    def adb(*command):
        return subprocess.check_output(
            [args.adb, "-s", args.serial, *map(str, command)], stderr=subprocess.STDOUT, timeout=180,
        ).decode("utf-8", errors="replace")

    def shell(*command):
        return adb("shell", "-T", shlex.join(command))

    # The caller builds and installs the APKs first. Do not uninstall or clear application data.
    shell("pm", "path", PACKAGE)
    results = []
    for name, test_class, argument, value in PHASES:
        print(f"Running {name}...", flush=True)
        shell("am", "force-stop", PACKAGE)
        output = shell(
            "am", "instrument", "-w", "-r", "-e", "class", PACKAGE + "." + test_class,
            "-e", argument, value, PACKAGE + ".test/androidx.test.runner.AndroidJUnitRunner",
        )
        (args.output / (name + ".txt")).write_text(output, encoding="utf-8")
        require_pass(output)
        results.append({"phase": name, "passed": True})
    adb("pull", f"/sdcard/Android/data/{PACKAGE}/files/Pictures/opencc-docs/device-test.png", args.output / "device-test.png")
    (args.output / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print("All five invocations passed, including both real process-restart phases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
