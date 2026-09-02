#!/bin/sh

set -eu

if [ "$#" -ne 1 ]; then
  printf 'Usage: %s <arm64-v8a|armeabi-v7a|x86_64|x86>\n' "$0" >&2
  exit 2
fi

abi="$1"
case "$abi" in
  arm64-v8a|armeabi-v7a|x86_64|x86) ;;
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

page_size="$(
  adb shell "if command -v getconf >/dev/null 2>&1; then \
    getconf PAGE_SIZE; \
  else \
    awk '/KernelPageSize:/ { print \$2 * 1024; exit }' /proc/self/smaps; \
  fi" | tr -d '\r'
)"
sdk_level="$(adb shell getprop ro.build.version.sdk | tr -d '\r')"
device_abi="$(adb shell getprop ro.product.cpu.abi | tr -d '\r')"
case "${page_size}" in
  4096|16384) ;;
  *)
    printf 'Unexpected or unavailable PAGE_SIZE: %s\n' "${page_size}" >&2
    exit 1
    ;;
esac
if [ -n "${EXPECTED_PAGE_SIZE:-}" ] && [ "${page_size}" != "${EXPECTED_PAGE_SIZE}" ]; then
  printf 'Expected PAGE_SIZE=%s, found %s\n' "${EXPECTED_PAGE_SIZE}" "${page_size}" >&2
  exit 1
fi
printf 'Runtime: API=%s device_abi=%s apk_abi=%s PAGE_SIZE=%s\n' \
  "${sdk_level}" "${device_abi}" "${abi}" "${page_size}"

adb install -r -t "${target_apk}"
adb install -r -t "${test_apk}"

run_instrumentation() {
  class_name="$1"
  shift

  adb logcat -c || true
  if output="$(adb shell am instrument -w -r \
      -e class "${class_name}" \
      "$@" \
      "${test_package}/androidx.test.runner.AndroidJUnitRunner" 2>&1)"; then
    instrumentation_status=0
  else
    instrumentation_status=$?
  fi
  printf '%s\n' "${output}"
  if [ "${instrumentation_status}" -eq 0 ] && printf '%s\n' "${output}" | grep -Fq "OK (1 test)"; then
    printf 'INSTRUMENTATION_OK class=%s\n' "${class_name}"
    return 0
  fi

  printf 'INSTRUMENTATION_FAILED class=%s exit_status=%s\n' \
    "${class_name}" "${instrumentation_status}" >&2
  printf '%s\n' '--- Android crash buffer ---' >&2
  adb logcat -b crash -d -v threadtime >&2 || true
  printf '%s\n' '--- Relevant recent Android logs ---' >&2
  adb logcat -d -v threadtime -t 600 2>/dev/null \
    | grep -E "${target_package}|AndroidRuntime|DEBUG|FATAL|Fatal|libc|linker|tombstoned|crash_dump" \
    >&2 || true
  printf '%s\n' '--- Package process state ---' >&2
  adb shell pidof "${target_package}" >&2 || true
  adb shell pidof "${test_package}" >&2 || true
  return 1
}

run_instrumentation \
  io.github.supermonster003.autojs6.plugin.opencc.OpenccEntryResourceTest \
  -e opencc_entry_resource_phase standalone
run_instrumentation \
  io.github.supermonster003.autojs6.plugin.opencc.OpenccEntryResourceTest \
  -e opencc_entry_resource_phase binder
run_instrumentation \
  io.github.supermonster003.autojs6.plugin.opencc.OpenccPluginServiceTest
run_instrumentation \
  io.github.supermonster003.autojs6.plugin.opencc.OpenccDualEntryTest
run_instrumentation \
  io.github.supermonster003.autojs6.plugin.opencc.OpenccDualEntryLifecycleTest
run_instrumentation \
  io.github.supermonster003.autojs6.plugin.opencc.OpenccStandaloneUiTest
run_instrumentation \
  io.github.supermonster003.autojs6.plugin.opencc.OpenccResourceRestartTest \
  -e opencc_resource_restart_phase prepare
run_instrumentation \
  io.github.supermonster003.autojs6.plugin.opencc.OpenccResourceRestartTest \
  -e opencc_resource_restart_phase verify
