<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>Offline OpenCC Chinese converter for standalone use and AutoJs6</p>

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

OpenCC is one install with two entry points for [OpenCC](https://github.com/BYVoid/OpenCC)-based Chinese text conversion. Launch it directly as a fully offline Android App, or let AutoJs6 discover the same APK as a plugin and use the global `opencc` script object. Both paths cover Simplified Chinese, Traditional Chinese, Hong Kong Traditional, Taiwan Traditional, and Japanese Shinjitai.

The standalone editor and the permission-protected AutoJs6 Binder service share one official OpenCC engine, the same pinned dictionaries, cache, conversion types, and error model. The App does not require AutoJs6, while plugin mode keeps the existing script API and allows the conversion engine to be updated independently of the host.

******

### Features

******

- One APK, two uses: open the launcher icon for visual text conversion without AutoJs6, or use the same installation through the AutoJs6 `opencc` script API.
- 14 standard conversions: covers OpenCC Simplified-Traditional conversion, Hong Kong and Taiwan variants, and Japanese Shinjitai, including Taiwan idiom conversion (such as swapping `软件` and `軟體`).
- 33 script methods: besides the general `opencc.convert(text, type)`, every conversion type has a shortcut method of the same name, plus 18 alias and composed methods such as `s2jp` and `tw2hk`.
- Text conversion uses local dictionaries and never uploads the text. The app has Internet permission for GitHub update checks. Automatic checks are enabled by default, at most once every 12 hours, including metered connections; disable them in Settings when needed.
- Right-sized packages: 4 single-ABI packages and a `universal` package containing all ABIs, so each device installs only what it needs.
- Multilingual: the standalone UI, plugin metadata, usage instructions, README, and changelog cover 10 languages.
- One shared backend: the editor and lightweight plugin service reuse the same verified resources and native engine; idle plugin connections are released automatically.
- Choose adaptive light, adaptive dark, automatic (default) or transparent launcher icons in Settings. Automatic colors and transparency depend on launcher support.
- Consistent language, dark mode, theme color and launcher settings with neutral surfaces, themed controls and confirmation dialogs. Preview preset or HEX/RGB colors before applying; Cancel leaves the saved settings unchanged.

******

### Interface Screenshot

******

These are unedited Android runtime captures of the standalone editor in day mode, the Arabic RTL layout at 170% font size in night mode, and the existing AutoJs6 plugin-center entry.

<table>
  <tr>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/standalone-phone-light.png?raw=true"
           alt="Standalone offline conversion in the day theme" width="280" />
      <br />
      <sub>Standalone offline conversion in the day theme</sub>
    </td>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/standalone-rtl-large-dark.png?raw=true"
           alt="Arabic RTL layout at 170% font size in the night theme" width="280" />
      <br />
      <sub>Arabic RTL layout at 170% font size in the night theme</sub>
    </td>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/plugin-center-enabled.png?raw=true"
           alt="OpenCC 1.0.2 recognized and enabled in the plugin center" width="280" />
      <br />
      <sub>OpenCC 1.0.2 recognized and enabled in the plugin center</sub>
    </td>
  </tr>
</table>

******

### Usage

******

1. Download and install one APK from [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) or the AutoJs6 plugin center. Choose the package matching your device ABI; when unsure, choose `universal` or see `How to Choose a Package` below.
2. For standalone use, open `OpenCC` from the launcher, type or explicitly paste text, choose one of the 14 conversion types, and tap `Convert`. AutoJs6 and a plugin-permission grant are not required.
3. For plugin use, update AutoJs6 to internal build 3923 (6.7.1 Alpha4) or later; release 6.8.0 and newer satisfy this requirement.
4. Open the AutoJs6 plugin center and confirm `OpenCC` is recognized and enabled. Official release packages pass signature verification automatically, with no manual authorization required.
5. Use the global `opencc` object directly in scripts, for example `opencc.s2t("汉字")`; no require, import, or host restart is needed.

> Both modes support Android 7.0 (API 24) or later. The minimum AutoJs6 build applies only to plugin scripts; the standalone App has no host dependency. If a script reports a missing plugin or an outdated host, see `FAQ` below.

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

#### Can I use OpenCC without installing AutoJs6?

Yes. Open the `OpenCC` launcher icon and convert text in the offline editor. AutoJs6 is needed only when a script calls the plugin through the global `opencc` object; both modes come from the same APK.

#### A script reports `Missing required plugin for "OpenCC plugin"`. What should I do?

This means AutoJs6 could not find the plugin on the device. Install the plugin and run the script again; no AutoJs6 restart is needed. If the message persists after installation, make sure the plugin has not been uninstalled by the system or a security app, and check its enabled and authorization status in the plugin center.

#### What is the difference between `s2tw` and `s2twp` (`s2twi`)?

`s2tw` converts character forms only (for example `软` becomes `軟`) and leaves the wording untouched; `s2twp` additionally replaces Mainland vocabulary with Taiwan idioms (for example `软件` becomes `軟體` and `鼠标` becomes `滑鼠`), and `s2twi` is its alias. Prefer `s2twp` for text aimed at Taiwanese readers and `s2tw` when only character forms need unifying.

#### Why is `opencc` unavailable in scripts running on the Node.js engine?

`opencc` is currently exclusive to Rhino, the default JavaScript engine of AutoJs6; the Node.js runtime does not provide an implementation yet. See [ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md) for related plans.

#### Does conversion require a network connection? Is long text slow?

No network is needed; all conversion runs locally on the OpenCC dictionaries bundled with the plugin. Each method call is one cross-process round trip, and even long texts usually convert in a single trip; in hot loops, prefer core types to avoid the extra round trips of composed methods.

#### Which permissions does the plugin request? Is my data safe?

Text conversion uses local dictionaries and never uploads the text. The app has Internet permission for GitHub update checks. Automatic checks are enabled by default, at most once every 12 hours, including metered connections; disable them in Settings when needed.

******

### Permissions and Security

******

The standalone App and AutoJs6 plugin entry have separate, explicit boundaries:

- Text conversion uses local dictionaries and never uploads the text. The app has Internet permission for GitHub update checks. Automatic checks are enabled by default, at most once every 12 hours, including metered connections; disable them in Settings when needed.
- Explicit editor actions: the Launcher accepts no shared text or URI, reads the clipboard only after `Paste`, and opens the system share sheet only after `Share`.
- Protected plugin service: only hosts holding the plugin permission, such as AutoJs6, can bind and call it. AutoJs6 also verifies the package signature; unrelated apps cannot invoke the service.
- Local processing: both entry points use bundled dictionaries completely offline. Input and output are not logged, persisted, backed up, uploaded, or collected.

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
aidl contract version: 2
aidl methods: getInfo(), convert(text, conversionType), getSupportedConversionTypes(), convertBatch(texts, conversionType), convertChain(text, conversionTypes)
batch/chain limits: 1024 texts / 32 stages
minimum host build: 3923 (6.7.1 Alpha4)
conversion backend: OpenCC 1.4.2 (ver.1.4.2)
OpenCC source commit: 025f371dc76b598d77384fbdab90c937471844d8
OpenCC resources SHA-256: 9ea0d303219b34d014d5c116677b5d325043beafb2c8a62ee889ca67f4d054a5
```

`OpenccPluginService` responds to the `org.autojs.plugin.OPENCC` action (category `opencc`), using `org.autojs.plugin.opencc.api.IOpenccPlugin` from opencc-api. Contract version 2 appends type discovery, batch conversion, and chained conversion after the original `getInfo()` and `convert(text, conversionType)` methods, and advertises its version and supported types through `PluginInfo.capabilities`; older hosts keep using the original methods and transaction numbers. A `WakeActivity` is also provided so the host can wake the plugin process.

The plugin builds official OpenCC `ver.1.4.2` directly at commit `025f371dc76b598d77384fbdab90c937471844d8` with the matching release resources. Each ABI contains one statically linked, 16 KB-aligned `libopencc_jni.so`, and conversion remains fully offline.

******

### Roadmap

******

The plugin's plans and progress are maintained as a checkable list in ROADMAP.md, organized by milestone with acceptance criteria, covering documentation and release experience, engineering and continuous integration, conversion capability enhancements, and runtime evolution. Unchecked items express intent rather than current capabilities; discussion via Issues is welcome.

- [View ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md)

******

### Release History

******

#### v1.5.0

_2026/09/30_

- `Feature` Choose adaptive light, adaptive dark, automatic (default) or transparent launcher icons in Settings. Automatic colors and transparency depend on launcher support.
- `Fix` App updates keep one launcher entry and preserve an explicitly chosen earlier icon. Host appearance is read in the background without replacing an active settings draft.
- `Improvement` Consistent language, dark mode, theme color and launcher settings with neutral surfaces, themed controls and confirmation dialogs. Preview preset or HEX/RGB colors before applying; Cancel leaves the saved settings unchanged.
- `Improvement` Consistent visual sizing for launcher and Plugin Center icons, with transparent backgrounds and neutral black, white or grayscale artwork

#### v1.4.2

_2026/09/19_

- `Fix` SDK XML v4 parsing warnings with AGP 9.1 and APK native alignment checks incorrectly triggered by JVM unit-test assembly tasks, using shared build plugins 1.8.3
- `Improvement` Raise targetSdk to 37 (Android 17) after compileSdk; the plugin's behavior does not depend on the new target

#### v1.4.1

_2026/09/15_

- `Improvement` Raise compileSdk to 37 (Android 17); targetSdk stays at 36 until the behavior that depends on the target is verified

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

Building requires JDK 17 or later and Android SDK 37; Gradle and plugin versions are managed centrally by `version.properties` and `io.github.supermonster003.autojs6-platform-versions`.

******

### Localization and Docs Generation

******

```text
.readme/common.json
.readme/android_strings.json
.readme/lang_*.json
.readme/template_readme.md
.readme/template_plugin_instruction.md
.changelog/lang_*.json
.changelog/template_changelog.md
.python/generate_markdown.py
docs/images/screenshots/README.md
docs/images/screenshots/plugin-center-enabled.png
docs/images/screenshots/standalone-phone-light.png
docs/images/screenshots/standalone-rtl-large-dark.png
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

`.readme/android_strings.json` is the single source for the standalone UI and service error strings, while the language JSON files provide README and plugin-center copy. Always edit the JSON sources under `.readme/` and `.changelog/` and rerun `py .python/generate_markdown.py`; generated `strings.xml`, `plugin_instruction.md`, README, and changelog artifacts are never edited by hand. Run `py .python/generate_markdown.py --check` to verify all 47 generated artifacts.

******

### License

******

The project code is licensed under the [Mozilla Public License 2.0](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE). Chinese conversion is powered directly by [OpenCC](https://github.com/BYVoid/OpenCC) (Apache License 2.0); bundled OpenCC, Marisa Trie, Darts Clone, and RapidJSON sources and licenses are listed in [Third-Party Notices](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/THIRD_PARTY_NOTICES.md).

******

### Links

******

- AutoJs6 OpenCC documentation: https://docs.autojs6.com/#/opencc
- AutoJs6 project: https://github.com/SuperMonster003/AutoJs6
- OpenCC official project: https://github.com/BYVoid/OpenCC
- Third-party notices: https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/THIRD_PARTY_NOTICES.md


[16 KB page alignment and build verification](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/16kb.md)
