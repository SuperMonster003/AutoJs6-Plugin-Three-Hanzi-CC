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

## Trusted release controller

`.github/workflows/opencc-release.yml` is the fail-closed entry point for M4-D-4. It exposes three
manual-only operations: `preflight` (the default), `candidate`, and `draft`. All trusted work is bound
to `master`. `preflight` and `candidate` have no tag, GitHub Release, index-dispatch, pull-request, or
repository-write capability. `draft` remains policy-locked while `OPENCC_AUTOMATION_MODE` is anything
other than `release`; its locked path has read-only permissions, does not enter the release Environment,
and does not start signing or gate-dispatch jobs.

The `preflight` operation reconstructs the Android keystore in an ephemeral runner directory, checks
the pinned keystore and signer-certificate SHA-256 values, and signs a disposable JAR to prove that the
alias and both passwords are usable. The temporary keystore, certificate, and probe JAR are deleted
before the job exits and are never cached or uploaded as artifacts.

The same `preflight` operation pins `actions/create-github-app-token` v3.2.0 by commit and uses its
recommended Client ID input. It requests only `Actions: write`, scopes the installation token to
`SuperMonster003/AutoJs6-Official-Plugins-Index`, confirms that `plugin-index.yml` is active, performs
no dispatch, and lets the action revoke the short-lived token in its post-step.

The `candidate` operation requires an explicit 40-character source SHA. Before any secret is exposed,
the controller requires that SHA to equal the workflow event SHA, the checked-out commit, and a fresh
GitHub API read of `master`; it also requires `OPENCC_AUTOMATION_MODE=pr-only` (or `release` for a
future release-mode rehearsal), a clean recursive
submodule checkout, and the pinned OpenCC source/resource verification. Its checkout, Java, Python,
and artifact actions are pinned to exact commits and checkout credentials are not persisted.

The signing step reconstructs the keystore outside the workspace, writes an ignored temporary
`sign.properties` with mode `0600`, checks the keystore and exported-certificate digests, and performs
a minified five-APK build without a Gradle daemon or Actions cache. A trap removes both signing files
before the content-verification step starts; an unconditional final cleanup remains as a second line
of defense. The later steps have no signing secrets and enforce:

1. The exact four single-ABI packages plus one universal package.
2. The reviewed application ID, sole plugin permission, component/export surface, and locale config.
3. The pinned API AAR, required R8/JNI markers, sole `libopencc_jni.so`, and absence of the retired backend.
4. The exact OpenCC resource size/SHA-256, uncompressed native libraries, GNU RELRO, 16 KB ELF load
   alignment, and `zipalign -P 16` verification.
5. One signer certificate across all packages, equal to the Environment value and the last published
   release baseline.
6. Per-ABI size growth no greater than either 512 KiB or 25% over the checked-in v1.3.0 baseline.
7. Exact generated checksums/release notes and absence of keystore/private-key material in every APK
   and in the final bundle.

`prepare_candidate.py` then emits deterministic provenance in `CANDIDATE.json`: the exact source SHA,
version/build, OpenCC lock, signer certificate digest, package names/sizes/CRC32/SHA-256 values, and
the enforced size baseline. The only uploaded path is the exact eight-file public bundle (five APKs,
`SHA256SUMS.txt`, `RELEASE_NOTES.md`, and `CANDIDATE.json`), retained for 14 days. The GitHub App private
key is deliberately unavailable to this operation.

Run the candidate operation only against the current remote `master` SHA, for example:

```text
gh workflow run opencc-release.yml \
  --ref master \
  -f operation=candidate \
  -f source_sha=<exact-40-character-origin-master-SHA>
```

### Online candidate acceptance

[Run 33722685481](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/actions/runs/33722685481)
completed the first production-Environment candidate exercise from source
`42e6fde7fdae5fdd9dbb76e37c09488e0bacbb2a`. Every candidate step and cleanup/post-step succeeded,
the mutually exclusive preflight/index-token job was skipped, and the run produced no annotation.

The run uploaded exactly one artifact named
`opencc-signed-candidate-v1.3.0-build20-42e6fde7fdae` (artifact ID `9880889042`, archive SHA-256
`6db5af151a19e9d4083fd67de77b45b8ae4c4343975d3627e471e30b1fad775e`). An independent download
contained exactly the following five APKs plus `SHA256SUMS.txt`, `RELEASE_NOTES.md`, and
`CANDIDATE.json`:

| ABI | Size (bytes) | SHA-256 |
|---|---:|---|
| `arm64-v8a` | 1,555,356 | `01ae8d63a14cc041308071d1ece21f62a385fcb7defbd46d4a92e70936de0645` |
| `armeabi-v7a` | 1,216,354 | `3f22fa6f87517122252a0c3759fb838ba424ed958175be47b3d40322679f01ff` |
| `x86_64` | 1,563,529 | `aa5ed1660abbe272b88b3482c47c91e375f664c55f524df520a1e893472b21bf` |
| `x86` | 1,517,234 | `ccd93914a4e111ddccb0ba4ffd72e881aaa03d0da6ef2f0c85dad97550b7b05c` |
| `universal` | 3,890,281 | `dc22ecb5d943c21b52e0e4d33e666c627cee49e8ff50a7a76d6b253464a834f4` |

The downloaded manifest SHA-256 was
`9827de8d882b5394c4997c7e3b48304778b44745ce30b38cab52ce776b0f1d1a`. Its source, version/build,
OpenCC 1.4.2 lock and resource digest, signer certificate, per-package metadata, and size limits all
matched independent recalculation; a second local `apksigner` pass returned the expected release
certificate. Before/after GitHub API snapshots also proved that the five existing tags, v1.3.0
Release ID `381556777` and its seven assets, official index `main` commit and workflow history, and
the `pr-only` policy did not change. The same source commit's
[Build integrity run 33722663942](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/actions/runs/33722663942)
also passed all five jobs: build/APK inventory, API 24 minSdk, arm64 Binder, x86_64 4 KB Binder, and
x86_64 16 KB Binder.

After the draft controller landed, [run 33738494609](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/actions/runs/33738494609)
repeated the complete candidate path from exact source `b41d0286b071ba6160ea83c5dba5c2da11a5b474`.
It uploaded exactly one `opencc-signed-candidate-v1.3.0-build20-b41d0286b071` artifact (ID
`9886881929`, 9,749,717 bytes, server archive SHA-256
`d54e4bef6d114ab30185dd9f33640c9b49cedd601d15f3f4b8048c16b96b5707`); every candidate,
cleanup, and post-step succeeded and all five jobs had zero annotations. The same source's
[Build integrity run 33737709352](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/actions/runs/33737709352)
passed the exact five-job inventory. Its Android 10+ clipboard test uses the observable Paste UI
result and `ClipboardManager` readback as the gate after restoring the task to the foreground,
because headless emulators can report `Activity.hasWindowFocus()` as false while the task itself is
focused. The exact test also passed locally on API 35 and API 28 devices before the rerun.

Later clean-emulator repetitions showed that one programmatic Paste click could still race the
Android clipboard overlay. Commit `315f4825277d5a7c50cad7ff9ead76972344dd85` therefore keeps the
pre-Android-10 path unchanged but performs Android 10+ Paste as a bounded sequence of real foreground
input taps, accepting only the final visible source/status result; Copy remains an explicit write and
is followed by a foreground `ClipboardManager` readback. The exact UI test passed six consecutive
API 35 device runs plus an API 28 run locally. Its
[Build integrity run 33741159918](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/actions/runs/33741159918)
passed all five jobs on attempt 2 with zero annotations. Attempt 1's only failed job was the 16 KB
emulator failing to connect through `adb` with exit code 20 before tests started; rerunning that job
against the same SHA passed the complete 16 KB device script.

[Candidate run 33742434419](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/actions/runs/33742434419)
then revalidated that exact final code SHA. It produced exactly one
`opencc-signed-candidate-v1.3.0-build20-315f4825277d` artifact (ID `9888406464`, 9,749,717 bytes,
server archive SHA-256 `fdf19dc67c55d82156dc0bee0ae50e952495cf80088ad537768e7aa3e0a7bc93`),
with every candidate/cleanup/post-step successful and zero annotations.

### Draft Release promotion

The `draft` operation is implemented but deliberately unavailable under the current `pr-only` policy.
Once the M4-D-2/M4-D-3 online upgrade-PR exercises permit the repository mode to become `release`, the
operation first runs the same isolated signed-candidate build. The upload step exposes its immutable
artifact ID and SHA-256 digest to later jobs; signing secrets never enter either promotion job.

An `actions: write`, `contents: read` job then explicitly dispatches fresh Build integrity and Markdown
integrity runs on `master`. `draft_release.py` binds both runs to the candidate source SHA, trusted
repository, workflow name/path, `workflow_dispatch` event, and exact job inventory. It requires all five
Build jobs—including the API 24 minSdk release probe—and the Markdown job to complete successfully.
It rechecks that remote `master` did not move before dispatch, after dispatch, or after both runs finish.
This explicit dispatch is required because a merge performed with `GITHUB_TOKEN` does not produce the
ordinary recursive `push` workflow runs used by human pushes.

Only the final job receives `contents: write`, and it still checks out the exact source without persisted
credentials. It downloads only the artifact ID produced earlier in the same release-controller run and
revalidates its API metadata, workflow-run ownership, digest, `CANDIDATE.json`, five APK hashes, signer,
ABI/Manifest/API/R8/OpenCC/ELF/ZIP gates, and size limits. Draft promotion additionally requires both the
semantic version and `VERSION_BUILD` to be strictly newer than the checked-in published baseline, proves
that the baseline still matches the current Latest Release and tag, and refuses any existing candidate
tag or Release—including another draft.

The write transaction creates a GitHub Release with `draft=true`, `prerelease=false`, and
`make_latest=false`, targeting the exact 40-character source SHA. It uploads exactly the five APKs,
`SHA256SUMS.txt`, and `RELEASE_NOTES.md`, then reads back all seven assets by name, byte size, content
type, uploader, and GitHub-computed SHA-256. It also requires Latest to remain unchanged and requires
that the future version tag has not yet been created; GitHub will create that tag only when a later,
separately gated operation publishes the draft. If upload or readback fails, the controller deletes only
the draft ID created by that invocation and verifies that neither the draft nor a tag remains. It never
updates an existing Release and never dispatches the plugin index.

### Online draft policy-lock acceptance

[Run 33739003669](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/actions/runs/33739003669)
exercised `operation=draft` at the same exact source while the repository variable was still
`OPENCC_AUTOMATION_MODE=pr-only`. Only `Report the draft policy lock without release writes` ran and
succeeded; the credential, candidate, exact-SHA gate-dispatch, and draft-write jobs were all skipped.
The run produced zero artifacts and zero annotations. It did not enter `opencc-release`: the deployment
list remained the single entry created by the preceding candidate run (deployment ID `6240871530`).
Before/after API snapshots had the same five published Releases and tags, v1.3.0 remained Latest, the
official index remained at `3b9b47cf4acd306ab2de63638e1aa761c82c28ad` with no new workflow run,
and the repository policy remained `pr-only`. This accepts the online locked path only; the actual
draft-write transaction still requires the D2/D3 online exercises, a genuinely newer version/build,
and an explicit temporary transition to `release`.

[Run 33742904676](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/actions/runs/33742904676)
repeated the same lock acceptance at final controller/test source
`315f4825277d5a7c50cad7ff9ead76972344dd85`: one read-only report succeeded, the other four jobs were
skipped, and artifact/annotation counts remained zero. The only `opencc-release` deployment at that
SHA was deployment `6241563946` from the immediately preceding candidate; the draft invocation added
none. Releases, tags, Latest, index commit/history, and `pr-only` mode again remained unchanged.

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

The current `pr-only` mode cannot create a draft or publish anything. A signed candidate is an auditable
workflow artifact, not a Release asset and not permission to promote it. The draft write path can become
reachable only after the M4-D-2/M4-D-3 online upgrade-PR exercises and an explicit transition to
`release`; final publication, tag creation, Latest promotion, and index dispatch remain unimplemented.
