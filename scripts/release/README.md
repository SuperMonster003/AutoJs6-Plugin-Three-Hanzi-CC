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
