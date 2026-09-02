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

expected_version_name="${EXPECTED_VERSION_NAME:?Set EXPECTED_VERSION_NAME}"
expected_version_code="${EXPECTED_VERSION_CODE:?Set EXPECTED_VERSION_CODE}"
target_package="io.github.supermonster003.autojs6.plugin.opencc"
test_package="${target_package}.test"
probe_runner="${target_package}.OpenccReleaseProbeInstrumentation"
unsigned_target_apk="ci-apks/release/app-${abi}-release-unsigned.apk"
unsigned_probe_apk="ci-apks/releaseProbe/app-release-probe-androidTest.apk"

test -f "$unsigned_target_apk"
test -f "$unsigned_probe_apk"

android_home="${ANDROID_HOME:?ANDROID_HOME is unavailable}"
apksigner="$(
  find "$android_home/build-tools" -type f \( -name apksigner -o -name apksigner.bat \) \
    | sort -V \
    | tail -n 1
)"
if [ -z "$apksigner" ] || [ ! -f "$apksigner" ]; then
  printf 'Could not locate apksigner below %s/build-tools\n' "$android_home" >&2
  exit 1
fi

signing_directory="$(mktemp -d)"
ci_keystore="${signing_directory}/ci-runtime.p12"
target_apk="${signing_directory}/app-${abi}-release-ci-signed.apk"
probe_apk="${signing_directory}/app-release-probe-ci-signed.apk"

cleanup() {
  adb uninstall "$test_package" >/dev/null 2>&1 || true
  adb uninstall "$target_package" >/dev/null 2>&1 || true
  rm -f "$ci_keystore" "$target_apk" "$probe_apk"
  rmdir "$signing_directory" >/dev/null 2>&1 || true
}
trap cleanup 0

# The checked release output is intentionally unsigned in public CI. Generate an ephemeral,
# non-production key and re-sign both APKs so Android can instrument the non-debuggable target.
keytool -genkeypair \
  -keystore "$ci_keystore" \
  -storetype PKCS12 \
  -storepass android \
  -keypass android \
  -alias androiddebugkey \
  -dname "CN=OpenCC CI Runtime,O=AutoJs6,C=US" \
  -keyalg RSA \
  -keysize 2048 \
  -validity 1 \
  -noprompt >/dev/null

sign_apk() {
  input="$1"
  output="$2"
  "$apksigner" sign \
    --ks "$ci_keystore" \
    --ks-key-alias androiddebugkey \
    --ks-pass pass:android \
    --key-pass pass:android \
    --out "$output" \
    "$input"
  "$apksigner" verify --verbose "$output" >/dev/null
}

sign_apk "$unsigned_target_apk" "$target_apk"
sign_apk "$unsigned_probe_apk" "$probe_apk"

certificate_digest() {
  "$apksigner" verify --print-certs "$1" \
    | sed -n \
      -e 's/^Signer #[0-9][0-9]* certificate SHA-256 digest: //p' \
      -e 's/^.*Signer: certificate SHA-256 digest: //p' \
    | head -n 1
}

target_certificate="$(certificate_digest "$target_apk")"
probe_certificate="$(certificate_digest "$probe_apk")"
if [ -z "$target_certificate" ] || [ "$target_certificate" != "$probe_certificate" ]; then
  printf 'CI target/probe signer mismatch: target=%s probe=%s\n' \
    "$target_certificate" "$probe_certificate" >&2
  exit 1
fi

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
printf 'Minified release runtime: API=%s device_abi=%s apk_abi=%s PAGE_SIZE=%s\n' \
  "$sdk_level" "$device_abi" "$abi" "$page_size"

adb uninstall "$test_package" >/dev/null 2>&1 || true
adb uninstall "$target_package" >/dev/null 2>&1 || true
adb install "$target_apk"
adb install -r -t "$probe_apk"
adb logcat -c || true

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
  printf 'Minified release instrumentation failed (shell status %s)\n' \
    "$instrumentation_status" >&2
  printf '%s\n' '--- Android crash buffer ---' >&2
  adb logcat -b crash -d -v threadtime >&2 || true
  printf '%s\n' '--- Relevant recent Android logs ---' >&2
  adb logcat -d -v threadtime -t 600 2>/dev/null \
    | grep -E "${target_package}|AndroidRuntime|DEBUG|FATAL|Fatal|libc|linker|tombstoned|crash_dump" \
    >&2 || true
  exit 1
fi

printf 'MINIFIED_RELEASE_RUNTIME_OK version=%s versionCode=%s PAGE_SIZE=%s abi=%s\n' \
  "$expected_version_name" "$expected_version_code" "$page_size" "$abi"
