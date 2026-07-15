<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>Complemento OpenCC para la conversión de texto chino</p>

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

### Idiomas (Languages)

******

El README.md actual admite los siguientes idiomas:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hans.md)
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-en.md)
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-fr.md)
- Español [es] # actual
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ja.md)
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ko.md)
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ru.md)
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ar.md)

******

### Introducción

******

El complemento AutoJs6 OpenCC proporciona conversión de texto chino basada en OpenCC para AutoJs6. Admite conversiones entre chino simplificado, chino tradicional, chino tradicional de Hong Kong, chino tradicional de Taiwán y formas relacionadas con el shinjitai japonés.

******

### Funciones

******

- Proporciona el servicio de complemento `opencc` con el ID de complemento `opencc`.
- Admite API de AutoJs6 como `opencc.convert(text, type)` y accesos directos como `opencc.s2t(text)` / `opencc.t2s(text)`.
- Los metadatos del complemento, las instrucciones de uso, el README y el CHANGELOG están localizados en español, francés, ruso, árabe, japonés, coreano, inglés, chino simplificado, chino tradicional de Hong Kong y chino tradicional de Taiwán.
- Basado en `com.github.brooklet:android-opencc`.

******

### Uso

******

```js
let text = "汉字转换";
let converted = opencc.convert(text, "S2T");
console.log(converted);
```

También hay métodos abreviados disponibles:

```js
console.log(opencc.s2t("汉字转换"));
console.log(opencc.t2s("漢字轉換"));
```

******

### Tipos de conversión

******

Los tipos de conversión OpenCC comunes incluyen:

```text
S2T, S2TW, S2TWP, S2HK,
T2S, T2TW, T2HK, T2JP,
TW2S, TW2T, TW2SP,
HK2S, HK2T,
JP2T
```

AutoJs6 también proporciona métodos abreviados compuestos como `s2jp`, `hk2tw`, `tw2hk` y `jp2s`.

******

### Historial de versiones

******

# v1.0.1

###### 2026/07/14

* `Mejora` Se añadieron compilaciones APK divididas por ABI para `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86` y un APK `universal`
* `Mejora` Se añadieron metadatos de ABI compatibles a la información de ejecución del complemento para que el host pueda identificar variantes compatibles
* `Mejora` Los nombres de los APK publicados ahora incluyen la versión, la variante ABI y el resumen CRC32

# v1.0.0

###### 2026/07/14

* `Función` Se añadió el servicio del complemento OpenCC con ID `opencc` y motor `opencc`
* `Función` Se añadió descubrimiento e invocación desde el host mediante `org.autojs.plugin.OPENCC`
* `Función` Se admitieron tipos de conversión OpenCC comunes: `S2T`, `S2TW`, `S2TWP`, `S2HK`, `T2S`, `T2TW`, `T2HK`, `T2JP`, `TW2S`, `TW2T`, `TW2SP`, `HK2S`, `HK2T` y `JP2T`
* `Función` Se añadieron metadatos e instrucciones de uso localizados para español, francés, ruso, árabe, japonés, coreano, inglés, chino simplificado, chino tradicional de Hong Kong y chino tradicional de Taiwán
* `Función` Se añadió un README bilingüe chino/inglés con ejemplos de uso, instrucciones de compilación y enlaces relacionados

##### Para ver más historial de versiones

* [CHANGELOG.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.changelog/CHANGELOG-es.md)

******

### Compilación

******

```powershell
.\gradlew.bat :app:assembleDebug
```

Compilación Release:

```powershell
.\gradlew.bat :app:assembleRelease
```

Los parámetros de compilación provienen de `version.properties`; el SDK mínimo actual es 24 y el SDK de destino es 36.

******

### Estructura de recursos

******

```text
.readme/lang_*.json
.changelog/lang_*.json
.python/generate_markdown.py
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

`strings.xml` contiene descripciones localizadas del complemento y mensajes de error; `plugin_instruction.md` contiene las instrucciones de uso que muestra el host. README y CHANGELOG se generan desde fuentes JSON mediante `.python/generate_markdown.py`.

******

### Enlaces

******

- Documentación de AutoJs6 OpenCC: https://docs.autojs6.com/#/opencc
- Proyecto oficial OpenCC: https://github.com/BYVoid/OpenCC
- Proyecto Android OpenCC: https://github.com/qichuan/android-opencc
