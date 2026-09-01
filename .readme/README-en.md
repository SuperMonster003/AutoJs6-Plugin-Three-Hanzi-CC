<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>OpenCC plugin for Chinese text conversion</p>

  <p>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/SuperMonster003/AutoJs6-Plugin-OpenCC?label=Release"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/SuperMonster003/AutoJs6-Plugin-OpenCC?color=A24232&label=Issues"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/SuperMonster003/AutoJs6-Plugin-OpenCC?color=534BAE&label=License"/></a>
  </p>
</div>

******

### Languages

******

The current README.md supports the following languages:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hans.md)
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-TW.md)
- English [en] # current
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-fr.md)
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-es.md)
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ja.md)
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ko.md)
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ru.md)
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ar.md)

******

### Introduction

******

The OpenCC Plugin brings [OpenCC](https://github.com/BYVoid/OpenCC)-based Chinese text conversion to AutoJs6. Once the plugin is installed, the global `opencc` object in AutoJs6 scripts just works: a single line of code converts text between Simplified Chinese, Traditional Chinese, Hong Kong Traditional, Taiwan Traditional, and Japanese Shinjitai, with no imports and no network access.

The plugin follows a host-plugin division of work: the AutoJs6 host provides the `opencc` API that scripts call directly, while the plugin ships the OpenCC conversion engine and dictionaries as a standalone app. Starting with AutoJs6 6.8.0 the host no longer bundles the OpenCC runtime and relies on this plugin instead; this keeps the host package slim and lets the conversion engine be updated independently of the host.

******

### Features

******

- Works out of the box: once installed, AutoJs6 discovers the plugin automatically; no host restart and no configuration are needed before scripts can call the global `opencc` object.
- 14 standard conversions: covers OpenCC Simplified-Traditional conversion, Hong Kong and Taiwan variants, and Japanese Shinjitai, including Taiwan idiom conversion (such as swapping `软件` and `軟體`).
- 33 script methods: besides the general `opencc.convert(text, type)`, every conversion type has a shortcut method of the same name, plus 18 alias and composed methods such as `s2jp` and `tw2hk`.
- Fully offline: conversion runs locally on the plugin's built-in dictionaries; the plugin requests no network permission and collects no data.
- Right-sized packages: 4 single-ABI packages and a `universal` package containing all ABIs, so each device installs only what it needs.
- Multilingual: plugin metadata, usage instructions, README, and changelog cover 10 languages.
- Lightweight background service: the plugin has no UI of its own; the host wakes and binds it on demand and idle connections are released automatically.

******

### Interface Screenshot

******

This is a real capture of the AutoJs6 plugin center. OpenCC 1.0.2 (17) is recognized by the host and the switch on the right is enabled. The original Android screenshot is preserved without cropping or color adjustment.

<table>
  <tr>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/plugin-center-enabled.png?raw=true"
           alt="OpenCC 1.0.2 recognized and enabled in the plugin center" width="360" />
      <br />
      <sub>OpenCC 1.0.2 recognized and enabled in the plugin center</sub>
    </td>
  </tr>
</table>

******

### Usage

******

1. Update AutoJs6 to internal build 3923 (6.7.1 Alpha4) or later; release 6.8.0 and newer all satisfy this requirement.
2. Download and install the plugin APK from the [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) page or from the AutoJs6 plugin center; when in doubt, pick the `universal` package or see `How to choose a package` below.
3. Open the AutoJs6 plugin center and confirm the `OpenCC` plugin is recognized and enabled; official release packages pass signature verification automatically, with no manual authorization required.
4. Use the global `opencc` object directly in scripts, for example `opencc.s2t("汉字")`; no require or import is needed, and AutoJs6 does not need to be restarted after installing the plugin.

> The plugin supports devices running Android 7.0 (API 24) or later. If a script reports a missing plugin or an outdated host, see `FAQ` below.

******

### Quick Start

******

After installation the following script runs as-is; the comments show the expected output:

```javascript
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.t2jp("圖書館"));      // => 図書館
```

Shortcut methods are equivalent to the general `opencc.convert(text, type)` method; the `opencc` object itself is also callable as a function, and conversion type names are case-insensitive:

```javascript
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
console.log(opencc("汉字转换", "s2t"));         // => 漢字轉換
```

All methods synchronously return the converted string; conversion happens on local dictionaries and never issues a network request.

******

### Conversion Types

******

The `convert` method and the same-named shortcuts support the following 14 standard OpenCC conversion types, where S stands for Simplified, T for Traditional (OpenCC standard), HK for Hong Kong Traditional, TW for Taiwan Traditional, and JP for Japanese Shinjitai:

| Type | Direction |
|---|---|
| `S2T` | Simplified to Traditional |
| `T2S` | Traditional to Simplified |
| `S2TW` | Simplified to Taiwan Traditional |
| `TW2S` | Taiwan Traditional to Simplified |
| `S2TWP` | Simplified to Taiwan Traditional with Taiwan idioms (for example `内存` becomes `記憶體`) |
| `TW2SP` | Taiwan Traditional to Simplified with Mainland idioms (for example `滑鼠` becomes `鼠标`) |
| `S2HK` | Simplified to Hong Kong Traditional |
| `HK2S` | Hong Kong Traditional to Simplified |
| `T2TW` | Traditional to Taiwan Traditional |
| `TW2T` | Taiwan Traditional to Traditional |
| `T2HK` | Traditional to Hong Kong Traditional |
| `HK2T` | Hong Kong Traditional to Traditional |
| `T2JP` | Traditional (Kyujitai) to Japanese Shinjitai |
| `JP2T` | Japanese Shinjitai to Traditional (Kyujitai) |

Types with a `P` suffix also perform vocabulary substitution on top of character conversion, so the result reads naturally to local readers; types without `P` convert character forms only and leave the wording untouched.

`T2JP` and `JP2T` convert between traditional Kyujitai character forms and Japanese Shinjitai, for example `圖書館` and `図書館`; they deal with character-form differences and are not a translation between Chinese and Japanese.

******

### Script Methods

******

The host-side `opencc` global object exposes 33 methods in total: the general `convert` method, 14 core shortcuts, and 18 alias and composed methods. The `type` argument of `convert(text, type)` accepts all 32 conversion names (core and composed alike) case-insensitively; passing an unknown type throws an `Unknown OpenCC conversion type` error.

The 14 core shortcuts map one-to-one to the conversion types in the table above; each call performs one plugin conversion:

```text
s2t   t2s   s2tw  tw2s  s2twp  tw2sp  s2hk
hk2s  t2tw  tw2t  t2hk  hk2t   t2jp   jp2t
```

`s2twi` and `twi2s` are aliases of `s2twp` and `tw2sp` respectively (`twi` stands for Taiwan idiom) and behave identically.

The remaining 16 composed methods chain several core conversions in order, covering directions that have no direct dictionary:

```text
s2jp   = s2t  + t2jp          jp2s   = jp2t + t2s
hk2tw  = hk2t + t2tw          tw2hk  = tw2t + t2hk
hk2jp  = hk2t + t2jp          tw2jp  = tw2t + t2jp
t2twi  = t2s  + s2twi         twi2t  = twi2s + s2t
hk2twi = hk2s + s2twi         twi2hk = twi2s + s2hk
tw2twi = tw2s + s2twi         twi2tw = twi2s + s2tw
jp2hk  = jp2t + t2hk          jp2tw  = jp2t + t2tw
twi2jp = twi2s + s2t + t2jp   jp2twi = jp2t + t2s + s2twi
```

A newer host that supports the extended contract sends an entire composed chain as one plugin call; the 3 conversion stages of `twi2jp`, for example, need only 1 Binder round trip. Older hosts keep calling each stage and remain compatible with this plugin.

******

### How to Choose a Package

******

Each release ships 5 APKs that differ only in which processor architectures (ABIs) of the OpenCC native library they bundle:

| Package | Intended for |
|---|---|
| `arm64-v8a` | The vast majority of modern Android phones and tablets (64-bit ARM); pick this first |
| `armeabi-v7a` | Older 32-bit ARM devices |
| `x86_64` | 64-bit x86 emulators and a small number of x86 devices |
| `x86` | 32-bit x86 emulators and a small number of x86 devices |
| `universal` | Bundles all 4 architectures and is the largest; works on any device and is the safe choice when unsure |

If a single-ABI package that does not match the device architecture was installed by mistake, the plugin cannot provide conversion; installing the `universal` package resolves this.

******

### Quick Self-Check

******

After confirming the plugin is installed and enabled in the plugin center, run this one-line script for an end-to-end verification:

```javascript
console.log(opencc.s2t("汉字转换"));
```

An output of `漢字轉換` means the whole plugin chain works. If the script fails, follow the error message: install this plugin when it reports a missing plugin, toggle the corresponding switch in the plugin center when it reports the plugin is disabled or unauthorized, and update AutoJs6 when it requires a newer host.

******

### FAQ

******

#### How do I confirm the plugin is active?

Open the AutoJs6 plugin center; seeing the `OpenCC` plugin listed and enabled means the host has recognized it. Then run the `Quick Self-Check` script above; an output of `漢字轉換` confirms it works.

#### Why is there no icon for the plugin in the app list?

This is expected. The plugin has no UI and creates no launcher icon; after installation AutoJs6 discovers and calls it in the background, and all interaction happens inside AutoJs6.

#### A script reports `Missing required plugin for "OpenCC plugin"`. What should I do?

This means AutoJs6 could not find the plugin on the device. Install the plugin and run the script again; no AutoJs6 restart is needed. If the message persists after installation, make sure the plugin has not been uninstalled by the system or a security app, and check its enabled and authorization status in the plugin center.

#### What is the difference between `s2tw` and `s2twp` (`s2twi`)?

`s2tw` converts character forms only (for example `软` becomes `軟`) and leaves the wording untouched; `s2twp` additionally replaces Mainland vocabulary with Taiwan idioms (for example `软件` becomes `軟體` and `鼠标` becomes `滑鼠`), and `s2twi` is its alias. Prefer `s2twp` for text aimed at Taiwanese readers and `s2tw` when only character forms need unifying.

#### Why is `opencc` unavailable in scripts running on the Node.js engine?

`opencc` is currently exclusive to Rhino, the default JavaScript engine of AutoJs6; the Node.js runtime does not provide an implementation yet. See [ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md) for related plans.

#### Does conversion require a network connection? Is long text slow?

No network is needed; all conversion runs locally on the OpenCC dictionaries bundled with the plugin. Each method call is one cross-process round trip, and even long texts usually convert in a single trip; in hot loops, prefer core types to avoid the extra round trips of composed methods.

#### Which permissions does the plugin request? Is my data safe?

The plugin only declares the plugin permission used to communicate with AutoJs6 and requests no sensitive system permissions such as network or storage; its service is protected by the same permission, so other apps cannot call it. Text being converted stays in device memory and is never stored or uploaded.

******

### Plugin Interface

******

The following information targets AutoJs6 host and plugin developers; the host uses these identifiers to discover the plugin and negotiate compatibility:

```text
application id: io.github.supermonster003.autojs6.plugin.opencc
plugin id: opencc
engine: opencc
variant: default
service action: org.autojs.plugin.OPENCC
service category: opencc
aidl interface: org.autojs.plugin.opencc.api.IOpenccPlugin
aidl contract version: 2
aidl methods: getInfo(), convert(text, conversionType), getSupportedConversionTypes(), convertBatch(texts, conversionType), convertChain(text, conversionTypes)
batch/chain limits: 1024 texts / 32 stages
minimum host build: 3923 (6.7.1 Alpha4)
conversion library: com.github.brooklet:android-opencc:1.2.2
```

`OpenccPluginService` responds to the `org.autojs.plugin.OPENCC` action (category `opencc`), using `org.autojs.plugin.opencc.api.IOpenccPlugin` from opencc-api. Contract version 2 appends type discovery, batch conversion, and chained conversion after the original `getInfo()` and `convert(text, conversionType)` methods, and advertises its version and supported types through `PluginInfo.capabilities`; older hosts keep using the original methods and transaction numbers. A `WakeActivity` is also provided so the host can wake the plugin process.

Conversion is powered by the OpenCC engine and dictionaries from `com.github.brooklet:android-opencc:1.2.2`.

******

### Roadmap

******

The plugin's plans and progress are maintained as a checkable list in ROADMAP.md, organized by milestone with acceptance criteria, covering documentation and release experience, engineering and continuous integration, conversion capability enhancements, and runtime evolution. Unchecked items express intent rather than current capabilities; discussion via Issues is welcome.

- [View ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md)

******

### Release History

******

#### v1.1.0

_2026/09/01_

- `Feature` Upgrade to OpenCC plugin contract version 2 with `getSupportedConversionTypes()`, allowing newer hosts to discover the 14 conversion types actually supported by the plugin
- `Feature` Add `convertBatch(texts, conversionType)` to convert up to 1024 text segments in one Binder round trip while retaining the per-item path for older hosts
- `Feature` Add `convertChain(text, conversionTypes)` to run up to 32 stages in one call, reducing composed methods on newer hosts from as many as 3 Binder round trips to 1
- `Improvement` Deliver localized plugin instructions through `PluginInfo.instruction` and report the contract version and supported conversion types through capabilities
- `Improvement` Preserve the original AIDL methods and transaction numbers, with unit and real Binder tests covering extended calls, legacy fallback, size limits, and error paths
- `Improvement` Standardize the README layout and Gradle platform version management

#### v1.0.2

_2026/08/31_

- `Hint` This release improves documentation and the build workflow only; OpenCC conversion behavior and all 14 core conversion types remain unchanged
- `Improvement` Restructure the README in all 10 languages with installation steps, package selection guidance, a quick self-check, the full list of 33 script methods, FAQ, and permission and security details
- `Improvement` Generate plugin-center instructions from the same localized JSON source as the README and CHANGELOG, keeping all Android documentation artifacts synchronized from one source
- `Improvement` Strengthen documentation validation and run it in GitHub Actions, automatically detecting cross-language shape mismatches, generated-file drift, orphan artifacts, version misalignment, and leftover placeholders
- `Improvement` Add ROADMAP.md with verifiable milestone checklists for documentation, engineering, conversion capabilities, and runtime evolution
- `Improvement` Migrate Gradle configuration to `org.autojs.build.platform-versions` 1.4.1 and use foojay for automatic JDK resolution, simplifying and standardizing the build environment

#### v1.0.1

_2026/07/14_

- `Improvement` Ship packages split by processor architecture (ABI): single-ABI packages for `arm64-v8a`, `armeabi-v7a`, `x86_64`, and `x86` plus a `universal` package with all architectures, so devices install only what they need and downloads stay small
- `Improvement` Report the supported ABI list in the plugin info so AutoJs6 and the plugin center can identify which plugin variants fit the current device
- `Improvement` Append the version, ABI, and CRC32 digest to release APK file names, making it easy to verify the integrity of downloaded files

##### For more release history

* [CHANGELOG.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/assets/doc/CHANGELOG-en.md)

******

### Build and Verification

******

This section targets developers who want to build the plugin from source; regular users can simply install the prebuilt APKs from the Releases page.

Build a debug APK:

```powershell
.\gradlew.bat :app:assembleDebug
```

Run JVM unit tests and build the instrumentation test APK:

```powershell
.\gradlew.bat :app:testDebugUnitTest :app:assembleDebugAndroidTest
```

Build release APKs:

```powershell
.\gradlew.bat :app:assembleRelease
```

Collect release artifacts and append the version, ABI, and CRC32 digest to each file name:

```powershell
.\gradlew.bat :app:appendDigestToReleasedFiles
```

Build release APKs and prepare checksums and release notes:

```powershell
py scripts\release\prepare_release.py
```

Verify that the multilingual documentation sources and generated artifacts are in sync (also enforced by CI):

```powershell
py .python\generate_markdown.py --check
```

Building requires JDK 17 or later and Android SDK 36; Gradle and plugin versions are managed centrally by `version.properties` and `io.github.supermonster003.autojs6-platform-versions`.

******

### Localization and Docs Generation

******

```text
.readme/common.json
.readme/lang_*.json
.readme/template_readme.md
.readme/template_plugin_instruction.md
.changelog/lang_*.json
.changelog/template_changelog.md
.python/generate_markdown.py
docs/images/screenshots/README.md
docs/images/screenshots/plugin-center-enabled.png
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

`strings.xml` holds the localized plugin description and error messages, and `plugin_instruction.md` holds the usage instructions shown inside the host plugin center. For README and changelog, always edit the JSON sources under `.readme/` and `.changelog/` and rerun `py .python/generate_markdown.py`; generated artifacts are never edited by hand. Run `py .python/generate_markdown.py --check` to verify sources and artifacts are in sync.

******

### License

******

The project code is licensed under the [Mozilla Public License 2.0](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE). Chinese conversion is powered by [OpenCC](https://github.com/BYVoid/OpenCC) (Apache License 2.0) and its Android wrapper [android-opencc](https://github.com/brooklet/android-opencc).

******

### Links

******

- AutoJs6 OpenCC documentation: https://docs.autojs6.com/#/opencc
- AutoJs6 project: https://github.com/SuperMonster003/AutoJs6
- OpenCC official project: https://github.com/BYVoid/OpenCC
- Android OpenCC project: https://github.com/brooklet/android-opencc
