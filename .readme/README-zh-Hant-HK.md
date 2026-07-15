<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>用於中文文本轉換的 OpenCC 插件</p>

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

### 語言 (Languages)

******

目前 README.md 支援以下語言:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hans.md)
- 繁體中文 (香港) [zh-Hant-HK] # 目前
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-en.md)
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-fr.md)
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-es.md)
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ja.md)
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ko.md)
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ru.md)
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ar.md)

******

### 簡介

******

AutoJs6 OpenCC 插件為 AutoJs6 提供基於 OpenCC 的中文文本轉換能力, 支援簡體/繁體/香港繁體/台灣繁體和日文新字體相關轉換.

******

### 功能

******

- 提供 `opencc` 插件服務, 插件 ID 為 `opencc`.
- 支援 AutoJs6 中的 `opencc.convert(text, type)` 和 `opencc.s2t(text)` / `opencc.t2s(text)` 等快捷方法.
- 插件資訊、使用說明、README 與 CHANGELOG 均支援西班牙語/法語/俄語/阿拉伯語/日語/韓語/英語/簡體中文/香港繁體/台灣繁體.
- 基於 `com.github.brooklet:android-opencc`.

******

### 使用示例

******

```js
let text = "汉字转换";
let converted = opencc.convert(text, "S2T");
console.log(converted);
```

亦可以使用快捷方法:

```js
console.log(opencc.s2t("汉字转换"));
console.log(opencc.t2s("漢字轉換"));
```

******

### 轉換類型

******

常用 OpenCC 轉換類型包括:

```text
S2T, S2TW, S2TWP, S2HK,
T2S, T2TW, T2HK, T2JP,
TW2S, TW2T, TW2SP,
HK2S, HK2T,
JP2T
```

AutoJs6 亦提供若干組合快捷方法, 例如 `s2jp`/`hk2tw`/`tw2hk`/`jp2s` 等.

******

### 發行歷史

******

# v1.0.1

###### 2026/07/14

* `優化` 支援按 ABI 構建 APK, 包括 `arm64-v8a`/`armeabi-v7a`/`x86_64`/`x86` 以及 `universal` 通用包
* `優化` 插件運行時資訊上報支援的 ABI 列表, 便於宿主識別可用變體
* `優化` 發佈 APK 文件名包含版本號/ABI 變體和 CRC32 摘要

# v1.0.0

###### 2026/07/14

* `新增` OpenCC 插件服務, 插件 ID 為 `opencc`, 引擎為 `opencc`
* `新增` 支援通過 `org.autojs.plugin.OPENCC` 發現並調用插件
* `新增` 支援 OpenCC 常用轉換類型: `S2T`/`S2TW`/`S2TWP`/`S2HK`/`T2S`/`T2TW`/`T2HK`/`T2JP`/`TW2S`/`TW2T`/`TW2SP`/`HK2S`/`HK2T`/`JP2T`
* `新增` 插件資訊和使用說明的多語言資源: 西班牙語/法語/俄語/阿拉伯語/日語/韓語/英語/簡體中文/香港繁體/台灣繁體
* `新增` 中英雙語 README, 包含用法示例/構建說明和相關連結

##### 更多發行歷史可參閱

* [CHANGELOG.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.changelog/CHANGELOG-zh-Hant-HK.md)

******

### 構建

******

```powershell
.\gradlew.bat :app:assembleDebug
```

Release 構建:

```powershell
.\gradlew.bat :app:assembleRelease
```

構建參數來自 `version.properties`, 目前最低 SDK 為 24, 目標 SDK 為 36.

******

### 資源結構

******

```text
.readme/lang_*.json
.changelog/lang_*.json
.python/generate_markdown.py
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

`strings.xml` 提供插件描述和錯誤資訊本地化; `plugin_instruction.md` 提供宿主側展示的插件使用說明. README 與 CHANGELOG 由 `.python/generate_markdown.py` 根據 JSON 源文件生成.

******

### 相關連結

******

- AutoJs6 OpenCC 文件: https://docs.autojs6.com/#/opencc
- OpenCC 官方項目: https://github.com/BYVoid/OpenCC
- Android OpenCC 項目: https://github.com/qichuan/android-opencc
