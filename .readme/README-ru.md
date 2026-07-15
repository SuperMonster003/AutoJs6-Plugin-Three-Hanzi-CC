<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>Плагин OpenCC для преобразования китайского текста</p>

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

### Языки (Languages)

******

Текущий README.md поддерживает следующие языки:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hans.md)
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-en.md)
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-fr.md)
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-es.md)
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ja.md)
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ko.md)
- Русский [ru] # текущий
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ar.md)

******

### Введение

******

Плагин AutoJs6 OpenCC предоставляет AutoJs6 преобразование китайского текста на основе OpenCC. Он поддерживает преобразования между упрощенным китайским, традиционным китайским, гонконгским традиционным китайским, тайваньским традиционным китайским и формами, связанными с японским синдзитай.

******

### Функции

******

- Предоставляет службу плагина `opencc` с идентификатором плагина `opencc`.
- Поддерживает API AutoJs6, такие как `opencc.convert(text, type)`, и сокращения вроде `opencc.s2t(text)` / `opencc.t2s(text)`.
- Метаданные плагина, инструкции, README и CHANGELOG локализованы на испанский, французский, русский, арабский, японский, корейский, английский, упрощенный китайский, гонконгский традиционный китайский и тайваньский традиционный китайский.
- Основан на `com.github.brooklet:android-opencc`.

******

### Использование

******

```js
let text = "汉字转换";
let converted = opencc.convert(text, "S2T");
console.log(converted);
```

Также доступны сокращенные методы:

```js
console.log(opencc.s2t("汉字转换"));
console.log(opencc.t2s("漢字轉換"));
```

******

### Типы преобразования

******

Распространенные типы преобразования OpenCC включают:

```text
S2T, S2TW, S2TWP, S2HK,
T2S, T2TW, T2HK, T2JP,
TW2S, TW2T, TW2SP,
HK2S, HK2T,
JP2T
```

AutoJs6 также предоставляет составные сокращенные методы, например `s2jp`, `hk2tw`, `tw2hk` и `jp2s`.

******

### История выпусков

******

# v1.0.1

###### 2026/07/14

* `Улучшение` Добавлены APK-сборки с разделением по ABI для `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86` и универсальный APK `universal`
* `Улучшение` В сведения о плагине во время выполнения добавлены метаданные поддерживаемых ABI, чтобы хост мог определять совместимые варианты
* `Улучшение` Имена публикуемых APK теперь включают версию, вариант ABI и дайджест CRC32

# v1.0.0

###### 2026/07/14

* `Функция` Добавлена служба плагина OpenCC с идентификатором `opencc` и движком `opencc`
* `Функция` Добавлены обнаружение и вызов со стороны хоста через `org.autojs.plugin.OPENCC`
* `Функция` Поддержаны распространенные типы преобразования OpenCC: `S2T`, `S2TW`, `S2TWP`, `S2HK`, `T2S`, `T2TW`, `T2HK`, `T2JP`, `TW2S`, `TW2T`, `TW2SP`, `HK2S`, `HK2T` и `JP2T`
* `Функция` Добавлены локализованные метаданные плагина и инструкции для испанского, французского, русского, арабского, японского, корейского, английского, упрощенного китайского, гонконгского традиционного китайского и тайваньского традиционного китайского
* `Функция` Добавлен двуязычный китайско-английский README с примерами использования, инструкциями по сборке и связанными ссылками

##### Больше истории выпусков

* [CHANGELOG.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.changelog/CHANGELOG-ru.md)

******

### Сборка

******

```powershell
.\gradlew.bat :app:assembleDebug
```

Release-сборка:

```powershell
.\gradlew.bat :app:assembleRelease
```

Параметры сборки берутся из `version.properties`; текущий минимальный SDK равен 24, целевой SDK равен 36.

******

### Структура ресурсов

******

```text
.readme/lang_*.json
.changelog/lang_*.json
.python/generate_markdown.py
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

`strings.xml` содержит локализованные описания плагина и сообщения об ошибках; `plugin_instruction.md` содержит инструкции, отображаемые хостом. README и CHANGELOG генерируются из JSON-источников с помощью `.python/generate_markdown.py`.

******

### Ссылки

******

- Документация AutoJs6 OpenCC: https://docs.autojs6.com/#/opencc
- Официальный проект OpenCC: https://github.com/BYVoid/OpenCC
- Проект Android OpenCC: https://github.com/qichuan/android-opencc
