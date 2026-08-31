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

Every step of a composed method is a separate plugin call; `twi2jp`, for example, performs 3 conversions in sequence. For tight loops or very long texts, prefer core types to reduce the number of calls.

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

### Permissions and Security

******

The plugin and AutoJs6 establish trust through the Android permission and signature mechanisms:

- Minimal permissions: the manifest declares only the `org.autojs.permission.PLUGIN` plugin permission and no sensitive system permissions such as network, storage, or camera.
- Two-way protection: the plugin service is guarded by the same permission, so only hosts holding the plugin permission (such as AutoJs6) can bind and call it; other apps have no access.
- Signature authorization: AutoJs6 verifies the plugin signature; official release packages are authorized automatically, while builds with other signatures must be authorized manually in the plugin center before they are loaded.
- Local processing: conversion happens entirely on the device; the plugin never goes online, writes nothing to disk, and collects no user data.

Only obtain the plugin from the official [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) page or the AutoJs6 plugin center. Packages from unknown sources may fail host verification or carry risks even when the version number looks identical.

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
aidl methods: getInfo(), convert(text, conversionType)
minimum host build: 3923 (6.7.1 Alpha4)
conversion library: com.github.brooklet:android-opencc:1.2.2
```

`OpenccPluginService` responds to the `org.autojs.plugin.OPENCC` action (category `opencc`); the Binder interface is `org.autojs.plugin.opencc.api.IOpenccPlugin` from opencc-api, with exactly two methods, `getInfo()` and `convert(text, conversionType)`. A `WakeActivity` is also provided so the host can wake the plugin process.

`PluginInfo.supportedAbis` reports the four architectures `arm64-v8a`, `armeabi-v7a`, `x86_64`, and `x86` so the host and the plugin center can identify available variants; conversion is powered by the OpenCC engine and dictionaries from `com.github.brooklet:android-opencc:1.2.2`.

******

### Roadmap

******

The plugin's plans and progress are maintained as a checkable list in ROADMAP.md, organized by milestone with acceptance criteria, covering documentation and release experience, engineering and continuous integration, conversion capability enhancements, and runtime evolution. Unchecked items express intent rather than current capabilities; discussion via Issues is welcome.

- [View ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md)

******

### Release History

******

#### v1.0.1

_2026/07/14_

- `Improvement` Ship packages split by processor architecture (ABI): single-ABI packages for `arm64-v8a`, `armeabi-v7a`, `x86_64`, and `x86` plus a `universal` package with all architectures, so devices install only what they need and downloads stay small
- `Improvement` Report the supported ABI list in the plugin info so AutoJs6 and the plugin center can identify which plugin variants fit the current device
- `Improvement` Append the version, ABI, and CRC32 digest to release APK file names, making it easy to verify the integrity of downloaded files

#### v1.0.0

_2026/07/14_

- `Feature` First stable release: provides OpenCC Chinese conversion for AutoJs6 as a standalone plugin, with both plugin ID and engine set to `opencc`
- `Feature` AutoJs6 discovers and calls the plugin automatically via `org.autojs.plugin.OPENCC`; it works right after installation with no configuration or restart
- `Feature` Support all 14 standard OpenCC conversion types, covering Simplified-Traditional conversion, Hong Kong and Taiwan variants, and Japanese Shinjitai: `S2T`/`S2TW`/`S2TWP`/`S2HK`/`T2S`/`T2TW`/`T2HK`/`T2JP`/`TW2S`/`TW2T`/`TW2SP`/`HK2S`/`HK2T`/`JP2T`
- `Feature` Localized plugin metadata and usage instructions in 10 languages: Simplified Chinese, Hong Kong Traditional, Taiwan Traditional, English, French, Spanish, Japanese, Korean, Russian, and Arabic
- `Feature` Multilingual README with usage examples, build instructions, and related links

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

Build release APKs; they are signed automatically once a signing identity is configured in the untracked `sign.properties`, and unsigned artifacts must not be published:

```powershell
.\gradlew.bat :app:assembleRelease
```

Collect release artifacts and append the version, ABI, and CRC32 digest to each file name:

```powershell
.\gradlew.bat :app:appendDigestToReleasedFiles
```

Verify that the multilingual documentation sources and generated artifacts are in sync (also enforced by CI):

```powershell
py .python\generate_markdown.py --check
```

Building requires JDK 17 or later and Android SDK 36; Gradle and plugin versions are managed centrally by `version.properties` and `org.autojs.build.platform-versions`.

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
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

`strings.xml` holds the localized plugin description and error messages, and `plugin_instruction.md` holds the usage instructions shown inside the host plugin center. For README and changelog, always edit the JSON sources under `.readme/` and `.changelog/` and rerun `py .python/generate_markdown.py`; generated artifacts are never edited by hand. Run `py .python/generate_markdown.py --check` to verify sources and artifacts are in sync.

******

### License

******

The project code is licensed under the [Mozilla Public License 2.0](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE). Chinese conversion is powered by [OpenCC](https://github.com/BYVoid/OpenCC) (Apache License 2.0) and its Android wrapper [android-opencc](https://github.com/qichuan/android-opencc).

******

### Links

******

- AutoJs6 OpenCC documentation: https://docs.autojs6.com/#/opencc
- AutoJs6 project: https://github.com/SuperMonster003/AutoJs6
- OpenCC official project: https://github.com/BYVoid/OpenCC
- Android OpenCC project: https://github.com/qichuan/android-opencc
