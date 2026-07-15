<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>Plugin OpenCC pour la conversion de texte chinois</p>

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

### Langues (Languages)

******

Le README.md actuel prend en charge les langues suivantes:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hans.md)
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-en.md)
- Français [fr] # actuel
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-es.md)
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ja.md)
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ko.md)
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ru.md)
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ar.md)

******

### Introduction

******

Le plugin AutoJs6 OpenCC fournit à AutoJs6 une conversion de texte chinois basée sur OpenCC. Il prend en charge les conversions entre chinois simplifié, chinois traditionnel, chinois traditionnel de Hong Kong, chinois traditionnel de Taïwan et formes liées au shinjitai japonais.

******

### Fonctions

******

- Fournit le service de plugin `opencc` avec l'ID de plugin `opencc`.
- Prend en charge les API AutoJs6 telles que `opencc.convert(text, type)` et les raccourcis comme `opencc.s2t(text)` / `opencc.t2s(text)`.
- Les métadonnées du plugin, les instructions d'utilisation, le README et le CHANGELOG sont localisés en espagnol, français, russe, arabe, japonais, coréen, anglais, chinois simplifié, chinois traditionnel de Hong Kong et chinois traditionnel de Taïwan.
- Basé sur `com.github.brooklet:android-opencc`.

******

### Utilisation

******

```js
let text = "汉字转换";
let converted = opencc.convert(text, "S2T");
console.log(converted);
```

Des méthodes raccourcies sont aussi disponibles:

```js
console.log(opencc.s2t("汉字转换"));
console.log(opencc.t2s("漢字轉換"));
```

******

### Types de conversion

******

Les types de conversion OpenCC courants incluent:

```text
S2T, S2TW, S2TWP, S2HK,
T2S, T2TW, T2HK, T2JP,
TW2S, TW2T, TW2SP,
HK2S, HK2T,
JP2T
```

AutoJs6 fournit aussi des méthodes raccourcies composées comme `s2jp`, `hk2tw`, `tw2hk` et `jp2s`.

******

### Historique des versions

******

# v1.0.1

###### 2026/07/14

* `Amélioration` Ajout de builds APK divisés par ABI pour `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86` et un APK `universal`
* `Amélioration` Ajout des métadonnées ABI prises en charge aux informations d'exécution du plugin afin que l'hôte puisse identifier les variantes compatibles
* `Amélioration` Les noms des APK publiés incluent maintenant la version, la variante ABI et le résumé CRC32

# v1.0.0

###### 2026/07/14

* `Fonctionnalité` Ajout du service de plugin OpenCC avec l'ID `opencc` et le moteur `opencc`
* `Fonctionnalité` Ajout de la découverte et de l'appel par l'hôte via `org.autojs.plugin.OPENCC`
* `Fonctionnalité` Prise en charge des types de conversion OpenCC courants: `S2T`, `S2TW`, `S2TWP`, `S2HK`, `T2S`, `T2TW`, `T2HK`, `T2JP`, `TW2S`, `TW2T`, `TW2SP`, `HK2S`, `HK2T` et `JP2T`
* `Fonctionnalité` Ajout des métadonnées de plugin et des instructions d'utilisation localisées en espagnol, français, russe, arabe, japonais, coréen, anglais, chinois simplifié, chinois traditionnel de Hong Kong et chinois traditionnel de Taïwan
* `Fonctionnalité` Ajout d'un README bilingue chinois/anglais avec des exemples d'utilisation, des instructions de compilation et des liens associés

##### Pour plus d'historique des versions

* [CHANGELOG.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.changelog/CHANGELOG-fr.md)

******

### Compilation

******

```powershell
.\gradlew.bat :app:assembleDebug
```

Compilation Release:

```powershell
.\gradlew.bat :app:assembleRelease
```

Les paramètres de compilation proviennent de `version.properties`; le SDK minimal actuel est 24 et le SDK cible est 36.

******

### Structure des ressources

******

```text
.readme/lang_*.json
.changelog/lang_*.json
.python/generate_markdown.py
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

`strings.xml` contient les descriptions localisées du plugin et les messages d'erreur; `plugin_instruction.md` contient les instructions d'utilisation affichées par l'hôte. README et CHANGELOG sont générés depuis des sources JSON par `.python/generate_markdown.py`.

******

### Liens

******

- Documentation AutoJs6 OpenCC: https://docs.autojs6.com/#/opencc
- Projet officiel OpenCC: https://github.com/BYVoid/OpenCC
- Projet Android OpenCC: https://github.com/qichuan/android-opencc
