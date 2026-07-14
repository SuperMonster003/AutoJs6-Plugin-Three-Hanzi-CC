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
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/commit/ac15c8492f78b0bb9c06f2b1e9b70d7ba87be81f"><img alt="Created" src="https://img.shields.io/date/1784032100?color=2e7d32&label=Created"/></a>
    <br>
    <a href="https://developer.android.com/studio/archive"><img alt="Android Studio" src="https://img.shields.io/badge/Android%20Studio-2023.3+-B64FC8"/></a>
    <a href="https://www.jetbrains.com/idea/download/other.html"><img alt="IntelliJ IDEA" src="https://img.shields.io/badge/IntelliJ%20IDEA-2023.3+-EE4677"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/SuperMonster003/AutoJs6-Plugin-OpenCC?color=534BAE&label=License"/></a>
  </p>
</div>

******

### Languages

******

The current README.md supports the following languages:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/README.md)
- English [en] # current

******

### Introduction

******

The AutoJs6 OpenCC Plugin provides OpenCC-powered Chinese text conversion for AutoJs6. It supports conversions between Simplified Chinese, Traditional Chinese, Hong Kong Traditional Chinese, Taiwan Traditional Chinese, and Japanese Shinjitai related forms.

******

### Features

******

- Provides the `opencc` plugin service with plugin ID `opencc`.
- Supports AutoJs6 APIs such as `opencc.convert(text, type)` and shortcuts like `opencc.s2t(text)` / `opencc.t2s(text)`.
- Plugin metadata and usage instructions are localized for Spanish, French, Russian, Arabic, Japanese, Korean, English, Simplified Chinese, Hong Kong Traditional Chinese, and Taiwan Traditional Chinese.
- Built on `com.github.brooklet:android-opencc`.

******

### Usage

******

```js
let text = "汉字转换";
let converted = opencc.convert(text, "S2T");
console.log(converted);
```

Shortcut methods are also available:

```js
console.log(opencc.s2t("汉字转换"));
console.log(opencc.t2s("漢字轉換"));
```

******

### Conversion Types

******

Common OpenCC conversion types include:

```text
S2T, S2TW, S2TWP, S2HK,
T2S, T2TW, T2HK, T2JP,
TW2S, TW2T, TW2SP,
HK2S, HK2T,
JP2T
```

AutoJs6 also provides composed shortcut methods such as `s2jp`, `hk2tw`, `tw2hk`, and `jp2s`.

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

******

### Build

******

```powershell
.\gradlew.bat :app:assembleDebug
```

Release build:

```powershell
.\gradlew.bat :app:assembleRelease
```

Build parameters come from `version.properties`. The current minimum SDK is 24 and target SDK is 36.

******

### Resource Layout

******

```text
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

`strings.xml` contains localized plugin descriptions and error messages. `plugin_instruction.md` contains usage instructions displayed by the host.

******

### Links

******

- AutoJs6 OpenCC documentation: https://docs.autojs6.com/#/opencc
- OpenCC official project: https://github.com/BYVoid/OpenCC
- Android OpenCC project: https://github.com/qichuan/android-opencc
