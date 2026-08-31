#!/bin/sh

set -eu

if [ "$#" -ne 1 ]; then
  printf 'Usage: %s <arm64-v8a|x86_64>\n' "$0" >&2
  exit 2
fi

abi="$1"
case "$abi" in
  arm64-v8a|x86_64) ;;
  *)
    printf 'Unsupported ABI: %s\n' "$abi" >&2
    exit 2
    ;;
esac

target_package="io.github.supermonster003.autojs6.plugin.opencc"
test_package="${target_package}.test"
target_apk="ci-apks/debug/app-${abi}-debug.apk"
test_apk="ci-apks/androidTest/debug/app-debug-androidTest.apk"

cleanup() {
  adb uninstall "${test_package}" >/dev/null 2>&1 || true
  adb uninstall "${target_package}" >/dev/null 2>&1 || true
}
trap cleanup 0

test -f "${target_apk}"
test -f "${test_apk}"
adb install -r -t "${target_apk}"
adb install -r -t "${test_apk}"

run_instrumentation() {
  class_name="$1"
  shift
  output="$(adb shell am instrument -w -r \
    -e class "${class_name}" \
    "$@" \
    "${test_package}/androidx.test.runner.AndroidJUnitRunner")"
  printf '%s\n' "${output}"
  printf '%s\n' "${output}" | grep -F "OK (1 test)"
}

run_instrumentation \
  io.github.supermonster003.autojs6.plugin.opencc.OpenccPluginServiceTest
run_instrumentation \
  io.github.supermonster003.autojs6.plugin.opencc.OpenccResourceRestartTest \
  -e opencc_resource_restart_phase prepare
run_instrumentation \
  io.github.supermonster003.autojs6.plugin.opencc.OpenccResourceRestartTest \
  -e opencc_resource_restart_phase verify
