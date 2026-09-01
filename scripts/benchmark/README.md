# OpenCC M4-B device benchmark

`run_opencc_benchmark.py` runs the migration-only `android-opencc:1.2.2` baseline and the
official OpenCC backend in isolated app installs. Each engine uses two instrumentation
processes:

1. `first-load` removes that engine's installed resources and measures the first conversion.
2. `steady-state` starts in a different PID with resources already installed, then measures a
   cold conversion, 200 hot conversions, a 1,024-segment batch workload, and peak process
   memory.

The benchmark is informational. It records raw nanoseconds and memory snapshots but deliberately
does not impose timing thresholds on CI, because Android emulator and shared-runner performance is
not stable enough for a release gate. Correctness remains enforced by
`OpenccPluginServiceTest`.

Build the required APKs first:

```shell
./gradlew :app:assembleDebug :app:assembleDebugAndroidTest :app:assembleRelease
```

Then run on a disposable device or emulator:

```shell
python scripts/benchmark/run_opencc_benchmark.py \
  --serial emulator-5554 \
  --abi x86_64 \
  --expected-page-size 16384
```

By default the raw JSON and a Markdown rendering are written beneath
`build/reports/opencc-benchmark/`. The runner refuses to continue if either plugin package is
already installed, because its isolation procedure uses uninstall/reinstall and therefore erases
package data. Use `--allow-package-reset` only when that destructive reset is intentional.

Run the host-side tests with:

```shell
python -m unittest discover -s scripts/benchmark/tests -p "test_*.py"
```
