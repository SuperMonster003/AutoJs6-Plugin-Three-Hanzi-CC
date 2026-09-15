# Optional instrumentation phases

Three fixtures need arguments or separate app processes and therefore do not execute as ordinary
single-process tests. Missing arguments now produce assumption skips; explicitly invalid phase
values and invalid screenshot names still fail. The existing benchmark remains separately
opt-in through its own arguments.

## Automated execution

Build and install the appropriate debug APK and `app-debug-androidTest.apk` for a test device,
then run from the repository root:

```powershell
.\gradlew.bat --no-daemon --max-workers=2 :app:assembleDebug :app:assembleDebugAndroidTest
# Install app/build/outputs/apk/debug/app-<abi>-debug.apk and the matching instrumentation APK.
python scripts/ci/run_phased_device_tests.py --serial <adb-serial>
```

The runner force-stops the test app before each invocation and executes these steps in order:

| Fixture | Argument | Values, in order |
| --- | --- | --- |
| `OpenccEntryResourceTest` | `opencc_entry_resource_phase` | `standalone`, `binder` |
| `OpenccResourceRestartTest` | `opencc_resource_restart_phase` | `prepare`, `verify` |
| `OpenccDocumentationScreenshotTest` | `opencc_screenshot_file` | `device-test.png` |

Every invocation must pass exactly one test without a skip. An adb exit code alone is not
sufficient. The runner saves logs, a JSON result list, and the actual PNG under
`build/verification/phased-tests/`, or the directory supplied with `--output`. It does not uninstall
the app or clear its data. Resource-corruption and restart fixtures deliberately manipulate the
test app's cached OpenCC resource and editor-state evidence; use a test installation.

## Additional test corrections

- The standalone entry, keyboard and screenshot fixtures explicitly select S2T and wait for the Spinner
  layout, independently of the conversion type remembered by earlier launches or UI tests.
  Its delayed selection callback cancels active conversions, so clicking Convert in the same
  main-thread action could leave the screenshot waiting forever for a canceled result.
- Clipboard actions now convert visible local button bounds to display coordinates with
  `getLocationOnScreen` before `input tap`. Root-window coordinates can omit window/decor
  offsets and send the tap to the wrong control.

These corrections do not change the production converter or its public API.

## Evidence, 2026-09-16

- API 37 x86_64 / 16 KB emulator: all five explicit invocations passed, including the real
  process-restart verification and screenshot capture.
- Two consecutive default suites on the same emulator: each had 5 passes, 4 expected opt-in
  skips and no failures, followed by another successful five-phase run. Those skips
  are the three fixtures listed above and the performance benchmark; the first three were also
  executed explicitly as described above.
- Sony XQ-AT72 / API 31: the previously failing standalone clipboard/UI test passed after the
  coordinate correction.
- JVM tests: 18/18 passed. Debug/instrumentation assembly, lintDebug, signed release collection,
  native 16 KB alignment checks and Markdown check passed.
- Host runner result tests passed, including rejected skip/crash/failure outputs.

Local logs are under `build/verification/plugin-test-repair/` and remain ignored.
