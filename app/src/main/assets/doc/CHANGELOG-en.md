******

### Release History

******

# v1.0.1

###### 2026/07/14

* `Improvement` Added ABI split APK builds for `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86`, and a `universal` APK
* `Improvement` Added supported ABI metadata to plugin runtime info so the host can identify compatible variants
* `Improvement` Release APK filenames now include the version, ABI variant, and CRC32 digest

# v1.0.0

###### 2026/07/14

* `Feature` Added the OpenCC plugin service with plugin ID `opencc` and engine `opencc`
* `Feature` Added host discovery and invocation through `org.autojs.plugin.OPENCC`
* `Feature` Supported common OpenCC conversion types: `S2T`, `S2TW`, `S2TWP`, `S2HK`, `T2S`, `T2TW`, `T2HK`, `T2JP`, `TW2S`, `TW2T`, `TW2SP`, `HK2S`, `HK2T`, and `JP2T`
* `Feature` Added localized plugin metadata and usage instructions for Spanish, French, Russian, Arabic, Japanese, Korean, English, Simplified Chinese, Hong Kong Traditional Chinese, and Taiwan Traditional Chinese
* `Feature` Added a bilingual Chinese/English README with usage examples, build instructions, and related links
