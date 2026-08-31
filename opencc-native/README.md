# Official OpenCC Android backend

This internal Android Library builds the pinned official OpenCC source directly instead of
shipping the unmaintained `android-opencc` wrapper. It is not a standalone public API module;
the plugin Binder contract remains the compatibility boundary.

## Reproducible inputs

The single source of upstream identity is [`../opencc-upstream.properties`](../opencc-upstream.properties).
It locks the official version, release tag, exact Git commit, resource asset, size, SHA-256 and
resource-manifest version as one unit. The source is a Git submodule at
`src/main/cpp/third_party/OpenCC`; the official resource bundle is kept as one stored-entry ZIP
under `src/main/assets/opencc`.

Initialize a fresh checkout before building:

```shell
git submodule update --init --recursive
```

No local OpenCC clone, Maven Local artifact or absolute developer-machine path is required.

## Build and verification

```shell
python scripts/opencc/verify_upstream.py --root .
./gradlew :opencc-native:assembleDebug
./gradlew :app:testDebugUnitTest :app:assembleDebug :app:assembleDebugAndroidTest
python scripts/ci/verify_apk_variants.py app/build/outputs/apk/debug
```

The native build uses NDK 28.2, CMake, C++17 and the bundled Marisa implementation. OpenCC and
the C++ runtime are linked statically into one `libopencc_jni.so` per ABI. The final JNI library
uses 16 KB ELF LOAD alignment, RELRO/NOW and hidden symbols; the application APK must not contain
`libopencc.so`, `libChineseConverter.so` or `libc++_shared.so`.

At runtime, the resource ZIP is copied atomically into a versioned no-backup directory and is
accepted only after size and SHA-256 verification. A file fingerprint avoids hashing the
unchanged 1.2 MB archive for every conversion; if the file changes, it is re-hashed and restored
from the verified APK asset before a converter is created.

## Upstream policy

Only published `ver.*` releases are eligible. Run the read-only watcher locally with:

```shell
python scripts/opencc/check_upstream.py --root . --fail-on-update
```

The scheduled workflow performs the same GitHub release, tag, asset-digest and ZIP-manifest
validation weekly. A newer version is an alert for human review, never an automatic merge or
release. See [`../ROADMAP.md`](../ROADMAP.md) for the staged upgrade and acceptance gates.

## Licenses

The repository and resulting native library include OpenCC, Marisa, Darts Clone and RapidJSON.
Their provenance and license choices are recorded in
[`../THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).
