#!/usr/bin/env python3
"""Verify the opencc_convert plugin tool (AutoJs6 plugin tool contract v1) on one device.

Installs the given APKs (never uninstalls or clears data), then runs the plugin's ThreeHanziCcToolServiceTest and, when
the AutoJs6 host test APK is given, the host's OpenccPluginToolRoundTripTest (script API and plugin_tools bridge against
this plugin). Prints one line per step with its result and test counts; full instrumentation logs go to --output.
"""

import argparse
from pathlib import Path
import re
import shlex
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "io.github.supermonster003.autojs6.plugin.three.hanzi.cc"
HOST_PACKAGE = "org.autojs.autojs6"
PLUGIN_TEST = (PACKAGE + ".ThreeHanziCcToolServiceTest", PACKAGE + ".test/androidx.test.runner.AndroidJUnitRunner")
HOST_TEST = ("org.autojs.autojs.core.plugin.tool.OpenccPluginToolRoundTripTest", HOST_PACKAGE + ".test/androidx.test.runner.AndroidJUnitRunner")


def summarize(output):
    """Returns (passed, counts) for an `am instrument -r` log; adb exits zero for failed and skipped tests too."""
    finished = len(re.findall(r"^INSTRUMENTATION_STATUS_CODE: 0\s*$", output, re.MULTILINE))
    failed = len(re.findall(r"^INSTRUMENTATION_STATUS_CODE: -2\s*$", output, re.MULTILINE))
    skipped = len(re.findall(r"^INSTRUMENTATION_STATUS_CODE: -3\s*$", output, re.MULTILINE))
    ok = re.search(r"^OK \((\d+) tests?\)\s*$", output, re.MULTILINE)
    broken = re.search(r"FAILURES!!!|INSTRUMENTATION_FAILED|Process crashed", output)
    passed = bool(ok) and not broken and failed == 0 and skipped == 0 and finished > 0
    return passed, f"{finished} passed, {failed} failed, {skipped} skipped"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True)
    parser.add_argument("--adb", default="adb")
    parser.add_argument("--plugin-apk", type=Path, required=True, help="the plugin debug APK for the device ABI")
    parser.add_argument("--plugin-test-apk", type=Path, default=ROOT / "app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk")
    parser.add_argument("--host-apk", type=Path, help="optional AutoJs6 host APK to install first")
    parser.add_argument("--host-test-apk", type=Path, help="optional AutoJs6 host androidTest APK; enables the host round trip")
    parser.add_argument("--output", type=Path, default=ROOT / "build/verification/plugin-tool-pilot")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    def adb(*command, timeout=300):
        return subprocess.run(
            [args.adb, "-s", args.serial, *map(str, command)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout,
        ).stdout.decode("utf-8", errors="replace")

    results = []

    def step(name, ok, detail=""):
        results.append(ok)
        print(f"{'PASS' if ok else 'FAIL'} {name}{': ' + detail if detail else ''}", flush=True)

    for label, apk in (("host", args.host_apk), ("host test", args.host_test_apk), ("plugin", args.plugin_apk), ("plugin test", args.plugin_test_apk)):
        if apk is None:
            continue
        output = adb("install", "-r", "-t", apk)
        step(f"install {label}", "Success" in output, apk.name)

    runs = [("plugin ThreeHanziCcToolServiceTest", PLUGIN_TEST, PACKAGE)]
    if args.host_test_apk is not None:
        runs.append(("host OpenccPluginToolRoundTripTest", HOST_TEST, HOST_PACKAGE))
    for name, (test_class, runner), package in runs:
        adb("shell", "am", "force-stop", package)
        output = adb("shell", "-T", shlex.join(["am", "instrument", "-w", "-r", "-e", "class", test_class, runner]), timeout=600)
        (args.output / (name.split()[-1] + ".txt")).write_text(output, encoding="utf-8")
        passed, counts = summarize(output)
        step(name, passed, counts)

    print(f"{sum(results)}/{len(results)} steps passed", flush=True)
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
