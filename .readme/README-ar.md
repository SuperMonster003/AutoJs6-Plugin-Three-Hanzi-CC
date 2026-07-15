<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>مكون OpenCC الإضافي لتحويل النص الصيني</p>

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

### اللغات (Languages)

******

يدعم README.md الحالي اللغات التالية:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hans.md)
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-en.md)
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-fr.md)
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-es.md)
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ja.md)
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ko.md)
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ru.md)
- العربية [ar] # الحالي

******

### مقدمة

******

يوفر مكون AutoJs6 OpenCC الإضافي تحويل النص الصيني في AutoJs6 بالاعتماد على OpenCC. وهو يدعم التحويل بين الصينية المبسطة والصينية التقليدية والصينية التقليدية في هونغ كونغ والصينية التقليدية في تايوان والأشكال المرتبطة بالشينجيتاي اليابانية.

******

### الميزات

******

- يوفر خدمة المكون الإضافي `opencc` بمعرف المكون `opencc`.
- يدعم واجهات AutoJs6 مثل `opencc.convert(text, type)` والاختصارات مثل `opencc.s2t(text)` / `opencc.t2s(text)`.
- تمت ترجمة بيانات المكون الإضافي وتعليمات الاستخدام وREADME وCHANGELOG إلى الإسبانية والفرنسية والروسية والعربية واليابانية والكورية والإنجليزية والصينية المبسطة والصينية التقليدية في هونغ كونغ والصينية التقليدية في تايوان.
- مبني على `com.github.brooklet:android-opencc`.

******

### الاستخدام

******

```js
let text = "汉字转换";
let converted = opencc.convert(text, "S2T");
console.log(converted);
```

تتوفر أيضا طرق مختصرة:

```js
console.log(opencc.s2t("汉字转换"));
console.log(opencc.t2s("漢字轉換"));
```

******

### أنواع التحويل

******

تشمل أنواع تحويل OpenCC الشائعة:

```text
S2T, S2TW, S2TWP, S2HK,
T2S, T2TW, T2HK, T2JP,
TW2S, TW2T, TW2SP,
HK2S, HK2T,
JP2T
```

يوفر AutoJs6 أيضا طرقا مختصرة مركبة مثل `s2jp` و`hk2tw` و`tw2hk` و`jp2s`.

******

### سجل الإصدارات

******

# v1.0.1

###### 2026/07/14

* `تحسين` تمت إضافة بناء APK مقسم حسب ABI لـ `arm64-v8a` و`armeabi-v7a` و`x86_64` و`x86` وحزمة `universal`
* `تحسين` تمت إضافة بيانات ABI المدعومة إلى معلومات تشغيل المكون الإضافي كي يتمكن المضيف من تحديد المتغيرات المتوافقة
* `تحسين` أصبحت أسماء ملفات APK المنشورة تتضمن الإصدار ومتغير ABI وملخص CRC32

# v1.0.0

###### 2026/07/14

* `ميزة` تمت إضافة خدمة مكون OpenCC الإضافي بمعرف `opencc` ومحرك `opencc`
* `ميزة` تمت إضافة الاكتشاف والاستدعاء من المضيف عبر `org.autojs.plugin.OPENCC`
* `ميزة` تم دعم أنواع تحويل OpenCC الشائعة: `S2T` و`S2TW` و`S2TWP` و`S2HK` و`T2S` و`T2TW` و`T2HK` و`T2JP` و`TW2S` و`TW2T` و`TW2SP` و`HK2S` و`HK2T` و`JP2T`
* `ميزة` تمت إضافة بيانات المكون الإضافي وتعليمات الاستخدام المترجمة للإسبانية والفرنسية والروسية والعربية واليابانية والكورية والإنجليزية والصينية المبسطة والصينية التقليدية في هونغ كونغ والصينية التقليدية في تايوان
* `ميزة` تمت إضافة README ثنائي اللغة بالصينية والإنجليزية مع أمثلة استخدام وتعليمات بناء وروابط ذات صلة

##### لمزيد من سجل الإصدارات

* [CHANGELOG.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.changelog/CHANGELOG-ar.md)

******

### البناء

******

```powershell
.\gradlew.bat :app:assembleDebug
```

بناء Release:

```powershell
.\gradlew.bat :app:assembleRelease
```

تأتي معلمات البناء من `version.properties`؛ الحد الأدنى الحالي لـ SDK هو 24 والـ SDK المستهدف هو 36.

******

### بنية الموارد

******

```text
.readme/lang_*.json
.changelog/lang_*.json
.python/generate_markdown.py
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

يحتوي `strings.xml` على أوصاف المكون الإضافي ورسائل الخطأ المترجمة؛ ويحتوي `plugin_instruction.md` على تعليمات الاستخدام التي يعرضها المضيف. يتم إنشاء README وCHANGELOG من مصادر JSON بواسطة `.python/generate_markdown.py`.

******

### الروابط

******

- وثائق AutoJs6 OpenCC: https://docs.autojs6.com/#/opencc
- مشروع OpenCC الرسمي: https://github.com/BYVoid/OpenCC
- مشروع Android OpenCC: https://github.com/qichuan/android-opencc
