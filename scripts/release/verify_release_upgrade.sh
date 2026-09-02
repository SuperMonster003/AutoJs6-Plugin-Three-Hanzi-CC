#!/bin/sh

set -eu

if [ "$#" -ne 4 ]; then
  printf 'Usage: %s <v1.2.0-apk> <candidate-apk> <signed-androidTest-apk> <arm64-v8a|armeabi-v7a|x86_64|x86>\n' "$0" >&2
  exit 2
fi

baseline_apk="$1"
candidate_apk="$2"
test_apk="$3"
abi="$4"
case "$abi" in
  arm64-v8a|armeabi-v7a|x86_64|x86) ;;
  *)
    printf 'Unsupported ABI: %s\n' "$abi" >&2
    exit 2
    ;;
esac

for apk in "$baseline_apk" "$candidate_apk" "$test_apk"; do
  if [ ! -f "$apk" ]; then
    printf 'Missing APK: %s\n' "$apk" >&2
    exit 1
  fi
done

expected_baseline_version="${EXPECTED_BASELINE_VERSION_NAME:-1.2.0}"
expected_version_name="${EXPECTED_VERSION_NAME:?Set EXPECTED_VERSION_NAME}"
expected_version_code="${EXPECTED_VERSION_CODE:?Set EXPECTED_VERSION_CODE}"
target_package="io.github.supermonster003.autojs6.plugin.opencc"
test_package="${target_package}.test"
probe_runner="${target_package}.OpenccReleaseProbeInstrumentation"

cleanup() {
  adb uninstall "$test_package" >/dev/null 2>&1 || true
  adb uninstall "$target_package" >/dev/null 2>&1 || true
}
trap cleanup 0

package_dump() {
  adb shell dumpsys package "$target_package" | tr -d '\r'
}

package_value() {
  key="$1"
  package_dump | sed -n "s/^[[:space:]]*${key}=//p" | head -n 1
}

package_version_code() {
  package_value versionCode | sed 's/[[:space:]].*$//'
}

package_uid() {
  package_dump | sed -n \
    -e 's/^[[:space:]]*userId=//p' \
    -e 's/^[[:space:]]*appId=//p' | head -n 1
}

resolved_activity() {
  adb shell cmd package resolve-activity --brief \
    -a android.intent.action.MAIN \
    -c android.intent.category.LAUNCHER \
    -p "$target_package" 2>&1 | tr -d '\r' | sed '/^[[:space:]]*$/d' | tail -n 1
}

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
case "$page_size" in
  4096|16384) ;;
  *)
    printf 'Unexpected or unavailable PAGE_SIZE: %s\n' "$page_size" >&2
    exit 1
    ;;
esac
if [ -n "${EXPECTED_PAGE_SIZE:-}" ] && [ "$page_size" != "$EXPECTED_PAGE_SIZE" ]; then
  printf 'Expected PAGE_SIZE=%s, found %s\n' "$EXPECTED_PAGE_SIZE" "$page_size" >&2
  exit 1
fi

sdk_level="$(adb shell getprop ro.build.version.sdk | tr -d '\r')"
device_abi="$(adb shell getprop ro.product.cpu.abi | tr -d '\r')"
printf 'Upgrade runtime: API=%s device_abi=%s apk_abi=%s PAGE_SIZE=%s\n' \
  "$sdk_level" "$device_abi" "$abi" "$page_size"

cleanup
adb install "$baseline_apk"

actual_baseline_version="$(package_value versionName)"
if [ "$actual_baseline_version" != "$expected_baseline_version" ]; then
  printf 'Expected baseline version %s, found %s\n' \
    "$expected_baseline_version" "$actual_baseline_version" >&2
  exit 1
fi
baseline_uid="$(package_uid)"
baseline_first_install="$(package_value firstInstallTime)"
if [ -z "$baseline_uid" ] || [ -z "$baseline_first_install" ]; then
  printf 'Could not read baseline UID or firstInstallTime\n' >&2
  exit 1
fi
baseline_launcher="$(
  resolved_activity || true
)"
case "$baseline_launcher" in
  ""|*"No activity found"*) ;;
  *)
    printf 'v%s unexpectedly exposes a Launcher: %s\n' \
      "$expected_baseline_version" "$baseline_launcher" >&2
    exit 1
    ;;
esac

adb install -r "$candidate_apk"

actual_version_name="$(package_value versionName)"
actual_version_code="$(package_version_code)"
candidate_uid="$(package_uid)"
candidate_first_install="$(package_value firstInstallTime)"
if [ "$actual_version_name" != "$expected_version_name" ]; then
  printf 'Expected candidate version %s, found %s\n' "$expected_version_name" "$actual_version_name" >&2
  exit 1
fi
if [ "$actual_version_code" != "$expected_version_code" ]; then
  printf 'Expected candidate versionCode %s, found %s\n' "$expected_version_code" "$actual_version_code" >&2
  exit 1
fi
if [ "$candidate_uid" != "$baseline_uid" ]; then
  printf 'Package UID changed across the in-place upgrade: %s -> %s\n' \
    "$baseline_uid" "$candidate_uid" >&2
  exit 1
fi
if [ "$candidate_first_install" != "$baseline_first_install" ]; then
  printf 'firstInstallTime changed across the in-place upgrade: %s -> %s\n' \
    "$baseline_first_install" "$candidate_first_install" >&2
  exit 1
fi

candidate_launcher="$(
  resolved_activity
)"
case "$candidate_launcher" in
  "${target_package}/${target_package}.OpenccActivity"|"${target_package}/.OpenccActivity") ;;
  *)
    printf 'Candidate Launcher did not resolve to OpenccActivity: %s\n' "$candidate_launcher" >&2
    exit 1
    ;;
esac

adb install -r -t "$test_apk"
if output="$(
  adb shell am instrument -w -r \
    -e opencc_expected_version_name "$expected_version_name" \
    -e opencc_expected_version_code "$expected_version_code" \
    "${test_package}/${probe_runner}" 2>&1
)"; then
  instrumentation_status=0
else
  instrumentation_status=$?
fi
printf '%s\n' "$output"
success_marker="RELEASE_RUNTIME_OK version=${expected_version_name} versionCode=${expected_version_code}"
if [ "$instrumentation_status" -ne 0 ] || \
    ! printf '%s\n' "$output" | grep -Fq "$success_marker" || \
    ! printf '%s\n' "$output" | grep -Fq 'INSTRUMENTATION_CODE: -1' || \
    printf '%s\n' "$output" | grep -Eq 'RELEASE_RUNTIME_FAILED|INSTRUMENTATION_STATUS_CODE: -2|Process crashed|INSTRUMENTATION_ABORTED'; then
  printf 'Release runtime instrumentation failed (shell status %s)\n' "$instrumentation_status" >&2
  exit 1
fi

printf 'RELEASE_UPGRADE_OK baseline=%s candidate=%s versionCode=%s uid=%s PAGE_SIZE=%s abi=%s\n' \
  "$expected_baseline_version" "$expected_version_name" "$expected_version_code" \
  "$candidate_uid" "$page_size" "$abi"
