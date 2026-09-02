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
accessibility_environment_modified=0
original_font_scale=""
original_night_mode=""

restore_accessibility_environment() {
  if [ "${accessibility_environment_modified}" -ne 1 ]; then
    return
  fi
  adb shell cmd locale set-app-locales "${target_package}" >/dev/null 2>&1 || true
  if [ -n "${original_font_scale}" ] && [ "${original_font_scale}" != "null" ]; then
    adb shell settings put system font_scale "${original_font_scale}" >/dev/null 2>&1 || true
  fi
  case "${original_night_mode}" in
    yes|no|auto|custom_schedule|custom_bedtime)
      adb shell cmd uimode night "${original_night_mode}" >/dev/null 2>&1 || true
      ;;
  esac
  adb shell am force-stop "${target_package}" >/dev/null 2>&1 || true
  accessibility_environment_modified=0
}

cleanup() {
  restore_accessibility_environment
  adb uninstall "${test_package}" >/dev/null 2>&1 || true
  adb uninstall "${target_package}" >/dev/null 2>&1 || true
}
trap cleanup 0

test -f "${target_apk}"
test -f "${test_apk}"

page_size="$(
  adb shell "if command -v getconf >/dev/null 2>&1; then \
    getconf PAGE_SIZE; \
  elif command -v awk >/dev/null 2>&1; then \
    awk '/KernelPageSize:/ { print \$2 * 1024; exit }' /proc/self/smaps; \
  else \
    while read -r label size unit remainder; do \
      if [ \"\${label}\" = \"KernelPageSize:\" ]; then \
        echo \$((size * 1024)); \
        break; \
      fi; \
    done < /proc/self/smaps; \
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
  io.github.supermonster003.autojs6.plugin.opencc.OpenccAccessibilityLayoutTest
if [ "${sdk_level}" -ge 33 ]; then
  original_font_scale="$(adb shell settings get system font_scale | tr -d '\r')"
  original_night_mode="$(adb shell cmd uimode night | tr -d '\r' | sed -n 's/^Night mode: //p')"
  accessibility_environment_modified=1
  adb shell settings put system font_scale 1.7
  adb shell cmd uimode night yes
  adb shell cmd locale set-app-locales "${target_package}" --locales ar
  adb shell am force-stop "${target_package}"
  sleep 1
  run_instrumentation \
    io.github.supermonster003.autojs6.plugin.opencc.OpenccAccessibilityLayoutTest \
    -e opencc_expect_rtl true \
    -e opencc_expect_large_font true \
    -e opencc_expect_night true
  restore_accessibility_environment
fi
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
