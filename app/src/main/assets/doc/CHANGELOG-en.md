******

### Release History

******

# v1.1.0

###### 2026/08/31

* `Feature` Upgrade to OpenCC plugin contract version 2 with `getSupportedConversionTypes()`, allowing newer hosts to discover the 14 conversion types actually supported by the plugin
* `Feature` Add `convertBatch(texts, conversionType)` to convert up to 1024 text segments in one Binder round trip while retaining the per-item path for older hosts
* `Feature` Add `convertChain(text, conversionTypes)` to run up to 32 stages in one call, reducing composed methods on newer hosts from as many as 3 Binder round trips to 1
* `Improvement` Deliver localized plugin instructions through `PluginInfo.instruction` and report the contract version and supported conversion types through capabilities
* `Improvement` Preserve the original AIDL methods and transaction numbers, with unit and real Binder tests covering extended calls, legacy fallback, size limits, and error paths

# v1.0.2

###### 2026/08/31

* `Hint` This release improves documentation and the build workflow only; OpenCC conversion behavior and all 14 core conversion types remain unchanged
* `Improvement` Restructure the README in all 10 languages with installation steps, package selection guidance, a quick self-check, the full list of 33 script methods, FAQ, and permission and security details
* `Improvement` Generate plugin-center instructions from the same localized JSON source as the README and CHANGELOG, keeping all Android documentation artifacts synchronized from one source
* `Improvement` Strengthen documentation validation and run it in GitHub Actions, automatically detecting cross-language shape mismatches, generated-file drift, orphan artifacts, version misalignment, and leftover placeholders
* `Improvement` Add ROADMAP.md with verifiable milestone checklists for documentation, engineering, conversion capabilities, and runtime evolution
* `Improvement` Migrate Gradle configuration to `org.autojs.build.platform-versions` 1.4.1 and use foojay for automatic JDK resolution, simplifying and standardizing the build environment

# v1.0.1

###### 2026/07/14

* `Improvement` Ship packages split by processor architecture (ABI): single-ABI packages for `arm64-v8a`, `armeabi-v7a`, `x86_64`, and `x86` plus a `universal` package with all architectures, so devices install only what they need and downloads stay small
* `Improvement` Report the supported ABI list in the plugin info so AutoJs6 and the plugin center can identify which plugin variants fit the current device
* `Improvement` Append the version, ABI, and CRC32 digest to release APK file names, making it easy to verify the integrity of downloaded files

# v1.0.0

###### 2026/07/14

* `Feature` First stable release: provides OpenCC Chinese conversion for AutoJs6 as a standalone plugin, with both plugin ID and engine set to `opencc`
* `Feature` AutoJs6 discovers and calls the plugin automatically via `org.autojs.plugin.OPENCC`; it works right after installation with no configuration or restart
* `Feature` Support all 14 standard OpenCC conversion types, covering Simplified-Traditional conversion, Hong Kong and Taiwan variants, and Japanese Shinjitai: `S2T`/`S2TW`/`S2TWP`/`S2HK`/`T2S`/`T2TW`/`T2HK`/`T2JP`/`TW2S`/`TW2T`/`TW2SP`/`HK2S`/`HK2T`/`JP2T`
* `Feature` Localized plugin metadata and usage instructions in 10 languages: Simplified Chinese, Hong Kong Traditional, Taiwan Traditional, English, French, Spanish, Japanese, Korean, Russian, and Arabic
* `Feature` Multilingual README with usage examples, build instructions, and related links
