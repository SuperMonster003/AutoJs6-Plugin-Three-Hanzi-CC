<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>中国語テキスト変換用 OpenCC プラグイン</p>

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

### 言語 (Languages)

******

現在の README.md は次の言語に対応しています:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hans.md)
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-en.md)
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-fr.md)
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-es.md)
- 日本語 [ja] # 現在
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ko.md)
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ru.md)
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ar.md)

******

### 概要

******

AutoJs6 OpenCC プラグインは、AutoJs6 に OpenCC ベースの中国語テキスト変換機能を提供します。簡体字、繁体字、香港繁体字、台湾繁体字、日本語新字体に関連する変換に対応しています。

******

### 機能

******

- プラグイン ID `opencc` の `opencc` プラグインサービスを提供します。
- `opencc.convert(text, type)` や `opencc.s2t(text)` / `opencc.t2s(text)` などの AutoJs6 API に対応します。
- プラグインメタデータ、使用説明、README、CHANGELOG はスペイン語、フランス語、ロシア語、アラビア語、日本語、韓国語、英語、簡体字中国語、香港繁体字、台湾繁体字にローカライズされています。
- `com.github.brooklet:android-opencc` を基盤にしています。

******

### 使用例

******

```js
let text = "汉字转换";
let converted = opencc.convert(text, "S2T");
console.log(converted);
```

ショートカットメソッドも使用できます:

```js
console.log(opencc.s2t("汉字转换"));
console.log(opencc.t2s("漢字轉換"));
```

******

### 変換タイプ

******

よく使う OpenCC 変換タイプには次のものがあります:

```text
S2T, S2TW, S2TWP, S2HK,
T2S, T2TW, T2HK, T2JP,
TW2S, TW2T, TW2SP,
HK2S, HK2T,
JP2T
```

AutoJs6 には `s2jp`、`hk2tw`、`tw2hk`、`jp2s` などの組み合わせショートカットも用意されています.

******

### リリース履歴

******

# v1.0.1

###### 2026/07/14

* `改善` `arm64-v8a`、`armeabi-v7a`、`x86_64`、`x86`、および `universal` APK 向けの ABI 分割 APK ビルドを追加
* `改善` ホストが互換性のあるバリアントを識別できるように、プラグイン実行時情報へ対応 ABI メタデータを追加
* `改善` 公開 APK のファイル名にバージョン、ABI バリアント、CRC32 ダイジェストを含めるように変更

# v1.0.0

###### 2026/07/14

* `機能` プラグイン ID `opencc`、エンジン `opencc` の OpenCC プラグインサービスを追加
* `機能` `org.autojs.plugin.OPENCC` によるホスト側の検出と呼び出しを追加
* `機能` 一般的な OpenCC 変換タイプ `S2T`、`S2TW`、`S2TWP`、`S2HK`、`T2S`、`T2TW`、`T2HK`、`T2JP`、`TW2S`、`TW2T`、`TW2SP`、`HK2S`、`HK2T`、`JP2T` に対応
* `機能` スペイン語、フランス語、ロシア語、アラビア語、日本語、韓国語、英語、簡体字中国語、香港繁体字、台湾繁体字のプラグインメタデータと使用説明を追加
* `機能` 使用例、ビルド説明、関連リンクを含む中国語/英語の二言語 README を追加

##### その他のリリース履歴

* [CHANGELOG.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.changelog/CHANGELOG-ja.md)

******

### ビルド

******

```powershell
.\gradlew.bat :app:assembleDebug
```

Release ビルド:

```powershell
.\gradlew.bat :app:assembleRelease
```

ビルドパラメータは `version.properties` から取得されます。現在の最小 SDK は 24、ターゲット SDK は 36 です.

******

### リソース構成

******

```text
.readme/lang_*.json
.changelog/lang_*.json
.python/generate_markdown.py
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

`strings.xml` にはローカライズされたプラグイン説明とエラーメッセージが含まれます。`plugin_instruction.md` にはホスト側で表示される使用説明が含まれます。README と CHANGELOG は `.python/generate_markdown.py` により JSON ソースから生成されます.

******

### リンク

******

- AutoJs6 OpenCC ドキュメント: https://docs.autojs6.com/#/opencc
- OpenCC 公式プロジェクト: https://github.com/BYVoid/OpenCC
- Android OpenCC プロジェクト: https://github.com/qichuan/android-opencc
