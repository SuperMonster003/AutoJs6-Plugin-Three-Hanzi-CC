# Release tooling

`prepare_release.py` builds and prepares the five signed OpenCC APK variants as one verified release bundle.

## Normal release

Configure the untracked `sign.properties`, make sure the Android SDK provides `apksigner`, and run:

```text
py scripts/release/prepare_release.py
```

The command performs these steps:

1. Runs `:app:assembleRelease`.
2. Requires exactly the `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86`, and `universal` APKs.
3. Verifies that each APK contains exactly the native ABI set advertised by its variant.
4. Verifies every APK signature and requires one signer certificate across all variants.
5. Adds the version, ABI, and computed CRC32 to each output filename.
6. Copies the packages atomically to `build/release/v<version>`.
7. Generates `SHA256SUMS.txt` and an English `RELEASE_NOTES.md` from `.changelog/lang_en.json`.

The command refuses missing variants, duplicate current-version variants, malformed current-version names, filename/content CRC mismatches, native ABI mismatches, unsigned APKs, and signer mismatches.

To validate an existing directory without rebuilding, use `--skip-build --input <directory>`. Other versions are explicitly excluded from the current bundle and reported. Use `--overwrite` only to replace an existing bundle under the project `build/release` directory.

## Tests

```text
py -m unittest discover -s scripts/release/tests -p "test_*.py"
```

The fixture suite covers the complete five-package path, missing-package rejection, duplicate/mixed-package rejection, native ABI mismatch rejection, CRC mismatch rejection, version isolation, checksums, and release-note generation.

## Signed in-place upgrade and minified runtime probe

`OpenccReleaseProbeInstrumentation` extends the platform `android.app.Instrumentation` directly and
avoids AndroidX, JUnit, and Kotlin at runtime. This lets the separately signed debug instrumentation
APK drive an installed minified release without forcing the production APK to retain test-only
runner dependencies or Kotlin helpers.

After preparing a signed candidate, run the following on each selected device (set `ANDROID_SERIAL`
when more than one device is connected):

```text
./gradlew :app:assembleDebugAndroidTest -PopenccReleaseProbe=true

EXPECTED_VERSION_NAME=1.3.0 \
EXPECTED_VERSION_CODE=20 \
EXPECTED_PAGE_SIZE=4096 \
sh scripts/release/verify_release_upgrade.sh \
  path/to/v1.2.0-abi.apk \
  build/release/v1.3.0/autojs6-plugin-opencc-v1.3.0-abi-xxxxxxxx.apk \
  app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk \
  abi
```

The Gradle property changes only the generated test APK's single instrumentation runner. Omitting it
keeps `AndroidJUnitRunner` for the normal debug device suite; setting it to any value other than
`true` or `false` fails configuration.

The script starts from an uninstalled state, installs v1.2.0, requires that it has no Launcher, and
performs an actual `adb install -r` upgrade. It then requires the same package UID and
`firstInstallTime`, the expected version name/code, and exactly one `OpenccActivity` Launcher. Finally,
the platform-only Java probe converts Unicode text through both the visible editor and legacy raw
Binder transaction 2 against the signed minified target. Its exit trap removes the target and
instrumentation packages.

Public CI also builds this platform-only probe, re-signs it and the otherwise unsigned minified
release APK with one ephemeral non-production key, and runs both UI and Binder conversions on the
API 24 minimum-SDK emulator. This release-target gate exists in addition to the full debug suite so
resource or code optimizations that only fail on older Android releases cannot pass unnoticed.

## Isolated release-environment preflight

`.github/workflows/opencc-release.yml` is the fail-closed entry point for M4-D-4. Its initial
`workflow_dispatch` path has no publication side effects: it may run only from `master` through the
`opencc-release` Environment, reconstructs the Android keystore in an ephemeral runner directory,
checks the pinned keystore and signer-certificate SHA-256 values, and signs a disposable JAR to prove
that the alias and both passwords are usable. The temporary keystore, certificate, and probe JAR are
deleted before the job exits and are never cached or uploaded as artifacts.

The same preflight pins `actions/create-github-app-token` v3.2.0 by commit and uses its recommended
Client ID input. It requests only `Actions: write`, scopes the installation token to
`SuperMonster003/AutoJs6-Official-Plugins-Index`, confirms that `plugin-index.yml` is active, performs
no dispatch, and lets the action revoke the short-lived token in its post-step.

The `opencc-release` Environment contains these encrypted secrets:

- `OPENCC_RELEASE_KEYSTORE_BASE64`
- `OPENCC_RELEASE_STORE_PASSWORD`
- `OPENCC_RELEASE_KEY_ALIAS`
- `OPENCC_RELEASE_KEY_PASSWORD`
- `OPENCC_INDEX_APP_PRIVATE_KEY`

It also contains these non-secret variables:

- `OPENCC_RELEASE_EXPECTED_KEYSTORE_SHA256`
- `OPENCC_RELEASE_EXPECTED_CERT_SHA256`
- `OPENCC_INDEX_APP_CLIENT_ID`

This preflight deliberately cannot create a tag, GitHub Release, pull request, index dispatch, or
commit. Candidate construction and publication are enabled only after the M4-D-2/M4-D-3 online
upgrade-PR exercises have passed and the repository automation policy is explicitly promoted beyond
`pr-only`.
