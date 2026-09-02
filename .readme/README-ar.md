<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>محول OpenCC صيني محلي يعمل مستقلا ومع AutoJs6</p>

  <p>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/SuperMonster003/AutoJs6-Plugin-OpenCC?label=Release"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/SuperMonster003/AutoJs6-Plugin-OpenCC?color=A24232&label=Issues"/></a>
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

يوفر OpenCC في تثبيت واحد مدخلين لتحويل النص الصيني اعتمادا على [OpenCC](https://github.com/BYVoid/OpenCC). شغله مباشرة كتطبيق Android محلي بالكامل, أو دع AutoJs6 يتعرف على ملف APK نفسه كمكون إضافي واستخدم الكائن العام `opencc` في البرامج النصية. يغطي المساران الصينية المبسطة والتقليدية ومتغيرات هونغ كونغ وتايوان والشينجيتاي اليابانية.

يشترك المحرر المستقل وخدمة Binder المحمية بإذن AutoJs6 في محرك OpenCC رسمي واحد والقواميس المثبتة نفسها وذاكرة التخزين المؤقت وأنواع التحويل ونموذج الأخطاء. لا يحتاج التطبيق المستقل إلى AutoJs6, بينما يحافظ وضع المكون الإضافي على API البرامج النصية الحالي ويسمح بتحديث المحرك باستقلال عن المضيف.

******

### أبرز الميزات

******

- ملف APK واحد واستخدامان: افتح أيقونة التشغيل للتحويل المرئي من دون AutoJs6, أو استخدم التثبيت نفسه عبر API البرامج النصية `opencc` في AutoJs6.
- 14 تحويلا قياسيا: تغطي تحويل OpenCC بين المبسطة والتقليدية ومتغيرات هونغ كونغ وتايوان والشينجيتاي اليابانية, بما في ذلك تحويل المفردات الشائعة في تايوان (مثل التبديل بين `软件` و`軟體`).
- 33 طريقة للبرامج النصية: إلى جانب الطريقة العامة `opencc.convert(text, type)`, لكل نوع تحويل طريقة مختصرة بالاسم نفسه, إضافة إلى 18 طريقة من الأسماء البديلة والطرق المركبة مثل `s2jp` و`tw2hk`.
- دون اتصال بالكامل: يجري التحويل محليا على القواميس المدمجة في المكون الإضافي; ولا يطلب المكون الإضافي إذن الشبكة ولا يجمع أي بيانات.
- حزم بالمقاس المناسب: 4 حزم أحادية ABI وحزمة `universal` تضم كل معماريات ABI, بحيث لا يثبت كل جهاز إلا ما يحتاج إليه.
- تعدد اللغات: تغطي الواجهة المستقلة وبيانات المكون الإضافي والتعليمات وREADME وسجل التغييرات 10 لغات.
- واجهة خلفية مشتركة: يعيد المحرر وخدمة المكون الخفيفة استخدام الموارد المتحقق منها والمحرك الأصلي نفسيهما, وتحرر الاتصالات الخاملة تلقائيا.

******

### لقطة للواجهة

******

تعرض لقطات Android غير المعدلة المحرر المستقل في المظهر النهاري, وتخطيط العربية RTL بحجم خط 170% في المظهر الليلي, ومدخل مركز مكونات AutoJs6 الحالي.

<table>
  <tr>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/standalone-phone-light.png?raw=true"
           alt="تحويل مستقل محلي في المظهر النهاري" width="280" />
      <br />
      <sub>تحويل مستقل محلي في المظهر النهاري</sub>
    </td>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/standalone-rtl-large-dark.png?raw=true"
           alt="تخطيط العربية RTL بحجم خط 170% في المظهر الليلي" width="280" />
      <br />
      <sub>تخطيط العربية RTL بحجم خط 170% في المظهر الليلي</sub>
    </td>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/plugin-center-enabled.png?raw=true"
           alt="التعرف على OpenCC 1.0.2 وتفعيله في مركز المكونات الإضافية" width="280" />
      <br />
      <sub>التعرف على OpenCC 1.0.2 وتفعيله في مركز المكونات الإضافية</sub>
    </td>
  </tr>
</table>

******

### الاستخدام

******

1. نزل ملف APK واحدا من [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) أو مركز مكونات AutoJs6 وثبته. اختر الحزمة المطابقة لـ ABI الجهاز, وعند التردد اختر `universal` أو راجع `كيفية اختيار حزمة التثبيت`.
2. للاستخدام المستقل افتح `OpenCC` من المشغل, واكتب النص أو الصقه صراحة, واختر نوعا من الأنواع الـ 14 ثم اضغط `تحويل`. لا يلزم AutoJs6 ولا منح إذن المكونات الإضافية.
3. للاستخدام كمكون إضافي حدث AutoJs6 إلى البنية الداخلية 3923 (6.7.1 Alpha4) أو أحدث; ويفي الإصدار 6.8.0 وما بعده بالمتطلب.
4. افتح مركز مكونات AutoJs6 وتأكد من التعرف على `OpenCC` وتفعيله. تجتاز الحزم الرسمية تحقق التوقيع تلقائيا من دون تفويض يدوي.
5. استخدم الكائن العام `opencc` مباشرة في البرامج النصية, مثل `opencc.s2t("汉字")`; لا حاجة إلى require أو import أو إعادة تشغيل المضيف.

> يدعم الوضعان Android 7.0 (API 24) وما فوق. ينطبق الحد الأدنى لبنية AutoJs6 على برامج المكون الإضافي فقط, ولا يعتمد التطبيق المستقل على مضيف. إذا أبلغ برنامج نصي عن مكون مفقود أو مضيف قديم فراجع `الأسئلة الشائعة`.

******

### بداية سريعة

******

بعد التثبيت يمكن تشغيل البرنامج النصي التالي كما هو; وتبين التعليقات المخرجات المتوقعة:

```javascript
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.t2jp("圖書館"));      // => 図書館
```

الطرق المختصرة مكافئة للطريقة العامة `opencc.convert(text, type)`; ويمكن أيضا استدعاء الكائن `opencc` نفسه كدالة, وأسماء أنواع التحويل غير حساسة لحالة الأحرف:

```javascript
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
console.log(opencc("汉字转换", "s2t"));         // => 漢字轉換
```

تعيد كل الطرق السلسلة المحولة بشكل متزامن; ويجري التحويل على قواميس محلية ولا يصدر أي طلب شبكة.

******

### أنواع التحويل

******

تدعم الطريقة `convert` والطرق المختصرة التي تحمل الأسماء نفسها أنواع تحويل OpenCC القياسية الـ 14 التالية, حيث ترمز S إلى الصينية المبسطة, وT إلى الصينية التقليدية (معيار OpenCC), وHK إلى الصينية التقليدية في هونغ كونغ, وTW إلى الصينية التقليدية في تايوان, وJP إلى الشينجيتاي اليابانية:

| النوع | اتجاه التحويل |
|---|---|
| `S2T` | من الصينية المبسطة إلى الصينية التقليدية |
| `T2S` | من الصينية التقليدية إلى الصينية المبسطة |
| `S2TW` | من الصينية المبسطة إلى الصينية التقليدية في تايوان |
| `TW2S` | من الصينية التقليدية في تايوان إلى الصينية المبسطة |
| `S2TWP` | من الصينية المبسطة إلى الصينية التقليدية في تايوان مع استبدال المفردات الشائعة في تايوان (مثلا يتحول `内存` إلى `記憶體`) |
| `TW2SP` | من الصينية التقليدية في تايوان إلى الصينية المبسطة مع استبدال المفردات الشائعة في البر الرئيسي الصيني (مثلا يتحول `滑鼠` إلى `鼠标`) |
| `S2HK` | من الصينية المبسطة إلى الصينية التقليدية في هونغ كونغ |
| `HK2S` | من الصينية التقليدية في هونغ كونغ إلى الصينية المبسطة |
| `T2TW` | من الصينية التقليدية إلى الصينية التقليدية في تايوان |
| `TW2T` | من الصينية التقليدية في تايوان إلى الصينية التقليدية |
| `T2HK` | من الصينية التقليدية إلى الصينية التقليدية في هونغ كونغ |
| `HK2T` | من الصينية التقليدية في هونغ كونغ إلى الصينية التقليدية |
| `T2JP` | من الصينية التقليدية (الكيوجيتاي) إلى الشينجيتاي اليابانية |
| `JP2T` | من الشينجيتاي اليابانية إلى الصينية التقليدية (الكيوجيتاي) |

الأنواع التي تحمل اللاحقة `P` تجري إلى جانب تحويل الحروف استبدالا للمفردات أيضا, بحيث يبدو الناتج طبيعيا للقراء المحليين; أما الأنواع الخالية من `P` فتحول أشكال الحروف فقط من دون المساس بالصياغة.

يحول `T2JP` و`JP2T` بين أشكال الحروف التقليدية القديمة (الكيوجيتاي) والشينجيتاي اليابانية, مثل `圖書館` و`図書館`; وهما يعالجان الفروق في أشكال الحروف وليسا ترجمة بين الصينية واليابانية.

******

### طرق البرامج النصية

******

يوفر الكائن العام `opencc` في جانب المضيف 33 طريقة في المجموع: الطريقة العامة `convert`, و14 طريقة مختصرة أساسية, و18 طريقة من الأسماء البديلة والطرق المركبة. وتقبل الوسيطة `type` في `convert(text, type)` جميع أسماء التحويل الـ 32 (الأساسية والمركبة على حد سواء) من دون حساسية لحالة الأحرف; وتمرير نوع مجهول يطلق الخطأ `Unknown OpenCC conversion type`.

الطرق المختصرة الأساسية الـ 14 تقابل أنواع التحويل في الجدول أعلاه واحدة لواحد; وكل استدعاء ينفذ تحويلا واحدا في المكون الإضافي:

```text
s2t   t2s   s2tw  tw2s  s2twp  tw2sp  s2hk
hk2s  t2tw  tw2t  t2hk  hk2t   t2jp   jp2t
```

`s2twi` و`twi2s` اسمان بديلان لـ `s2twp` و`tw2sp` على الترتيب (`twi` اختصار لـ Taiwan idiom, أي المفردات الشائعة في تايوان) ويتصرفان بالطريقة نفسها تماما.

الطرق المركبة المتبقية الـ 16 تسلسل عدة تحويلات أساسية بالترتيب, وتغطي الاتجاهات التي لا يوجد لها قاموس مباشر:

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

يرسل المضيف الحديث الذي يدعم العقد الموسع سلسلة التحويل المركبة كاملة في استدعاء واحد للمكون الإضافي; فمراحل `twi2jp` الثلاث تحتاج إلى رحلة Binder واحدة فقط. وتستمر المضيفات القديمة في استدعاء كل مرحلة وتبقى متوافقة مع هذا المكون الإضافي.

******

### كيفية اختيار حزمة التثبيت

******

يتضمن كل إصدار 5 ملفات APK لا تختلف إلا في معماريات المعالج (ABI) التي تضمنها من مكتبة OpenCC الأصلية:

| الحزمة | الفئة المستهدفة |
|---|---|
| `arm64-v8a` | الغالبية العظمى من هواتف Android وأجهزتها اللوحية الحديثة (ARM بمعمارية 64 بت); وهي الخيار الأول |
| `armeabi-v7a` | أجهزة ARM الأقدم بمعمارية 32 بت |
| `x86_64` | محاكيات x86 بمعمارية 64 بت وعدد قليل من أجهزة x86 |
| `x86` | محاكيات x86 بمعمارية 32 بت وعدد قليل من أجهزة x86 |
| `universal` | تضم المعماريات الأربع كلها وهي الأكبر حجما; تعمل على أي جهاز وهي الخيار الآمن عند التردد |

إذا ثبتت عن طريق الخطأ حزمة أحادية ABI لا تطابق معمارية الجهاز, فلن يستطيع المكون الإضافي توفير التحويل; وتثبيت حزمة `universal` يحل المشكلة.

******

### فحص ذاتي سريع

******

بعد التأكد من أن المكون الإضافي مثبت ومفعل في مركز المكونات الإضافية, شغل هذا البرنامج النصي المكون من سطر واحد لإجراء تحقق شامل من البداية إلى النهاية:

```javascript
console.log(opencc.s2t("汉字转换"));
```

ظهور الناتج `漢字轉換` يعني أن سلسلة المكون الإضافي تعمل بأكملها. إذا فشل البرنامج النصي, فاتبع رسالة الخطأ: ثبت هذا المكون الإضافي عندما تفيد الرسالة بفقدان مكون إضافي, وفعل المفتاح المقابل في مركز المكونات الإضافية عندما تفيد بأن المكون الإضافي معطل أو غير مفوض, وحدث AutoJs6 عندما تطلب مضيفا أحدث.

******

### الأسئلة الشائعة

******

#### كيف أتأكد من أن المكون الإضافي يعمل?

افتح مركز المكونات الإضافية في AutoJs6; فرؤية مكون `OpenCC` الإضافي في القائمة وهو مفعل تعني أن المضيف قد تعرف عليه. ثم شغل البرنامج النصي في `فحص ذاتي سريع` أعلاه; وظهور الناتج `漢字轉換` يؤكد أنه يعمل.

#### هل يمكنني استخدام OpenCC من دون تثبيت AutoJs6?

نعم. افتح أيقونة `OpenCC` وحول النص في المحرر المحلي. يلزم AutoJs6 فقط عندما يستدعي برنامج نصي المكون الإضافي عبر الكائن العام `opencc`; ويأتي الوضعان في ملف APK نفسه.

#### يظهر برنامج نصي الرسالة `المكون الإضافي المطلوب لـ "OpenCC plugin" مفقود`, فما العمل?

هذا يعني أن AutoJs6 لم يعثر على المكون الإضافي في الجهاز. ثبت المكون الإضافي ثم شغل البرنامج النصي مرة أخرى; ولا حاجة إلى إعادة تشغيل AutoJs6. إذا استمرت الرسالة بعد التثبيت, فتأكد من أن المكون الإضافي لم يزله النظام أو تطبيق حماية, وتحقق من حالتي التفعيل والتفويض في مركز المكونات الإضافية.

#### ما الفرق بين `s2tw` و`s2twp` (`s2twi`)?

يحول `s2tw` أشكال الحروف فقط (مثلا يتحول `软` إلى `軟`) ولا يمس الصياغة; بينما يستبدل `s2twp` إضافة إلى ذلك مفردات البر الرئيسي بالمفردات الشائعة في تايوان (مثلا يتحول `软件` إلى `軟體` و`鼠标` إلى `滑鼠`), و`s2twi` اسم بديل له. فضل `s2twp` للنصوص الموجهة إلى قراء تايوان, و`s2tw` عندما لا يلزم سوى توحيد أشكال الحروف.

#### لماذا يكون `opencc` غير متاح في البرامج النصية العاملة على محرك Node.js?

`opencc` حاليا حصري لمحرك Rhino, محرك JavaScript الافتراضي في AutoJs6; ولا توفر بيئة تشغيل Node.js تنفيذا له بعد. راجع [ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md) للاطلاع على الخطط ذات الصلة.

#### هل يتطلب التحويل اتصالا بالشبكة? وهل النص الطويل بطيء?

لا حاجة إلى الشبكة; فكل التحويل يجري محليا على قواميس OpenCC المرفقة مع المكون الإضافي. كل استدعاء لطريقة يقابل جولة واحدة من التواصل بين العمليات, وحتى النصوص الطويلة تتحول عادة في جولة واحدة; وفي حلقات الاستدعاء المكثفة فضل الأنواع الأساسية لتجنب الجولات الإضافية الناتجة عن الطرق المركبة.

#### ما الأذونات التي يطلبها المكون الإضافي? وهل بياناتي آمنة?

لا يعلن المكون الإضافي إلا إذن المكونات الإضافية المستخدم للتواصل مع AutoJs6, ولا يطلب أي أذونات نظام حساسة مثل الشبكة أو التخزين; وخدمته محمية بالإذن نفسه, فلا تستطيع التطبيقات الأخرى استدعاءها. والنص الجاري تحويله يبقى في ذاكرة الجهاز ولا يخزن ولا يرفع أبدا.

******

### الأذونات والأمان

******

للتطبيق المستقل ومدخل مكون AutoJs6 حدود منفصلة وصريحة:

- أذونات دنيا: لا يعلن البيان إلا `org.autojs.permission.PLUGIN` للتكامل, من دون أذونات حساسة للشبكة أو التخزين أو الكاميرا; ولا يمنح المستخدم المستقل إذن المكونات الإضافية.
- إجراءات صريحة: لا يقبل Launcher نصا مشتركا أو URI, ولا يقرأ الحافظة إلا بعد `لصق`, ولا يفتح لوحة النظام إلا بعد `مشاركة`.
- خدمة محمية: لا يستطيع الارتباط بها واستدعاءها إلا مضيف يحمل الإذن مثل AutoJs6. ويتحقق AutoJs6 أيضا من توقيع الحزمة, فلا يمكن للتطبيقات الأخرى استدعاء الخدمة.
- معالجة محلية: يستخدم المدخلان القواميس المدمجة بلا اتصال. لا تسجل المدخلات والنتائج ولا تحفظ أو تنسخ احتياطيا أو ترفع أو تجمع.

احصل على المكون الإضافي فقط من صفحة [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) الرسمية أو من مركز المكونات الإضافية في AutoJs6. فالحزم مجهولة المصدر قد لا تجتاز تحقق المضيف أو قد تحمل مخاطر حتى لو بدا رقم الإصدار مطابقا.

******

### واجهة المكون الإضافي

******

المعلومات التالية موجهة لمطوري مضيف AutoJs6 ومطوري المكونات الإضافية; يستخدم المضيف هذه المعرفات لاكتشاف المكون الإضافي والتفاوض على التوافق:

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

تستجيب `OpenccPluginService` للإجراء `org.autojs.plugin.OPENCC` (الفئة `opencc`) عبر `org.autojs.plugin.opencc.api.IOpenccPlugin` من opencc-api. يضيف الإصدار 2 من العقد اكتشاف الأنواع والتحويل الدفعي والتحويل المتسلسل بعد الطريقتين الأصليتين `getInfo()` و`convert(text, conversionType)`, ويعلن الإصدار والأنواع المدعومة عبر `PluginInfo.capabilities`; وتواصل المضيفات القديمة استخدام الطرق وأرقام المعاملات الأصلية. كما يتوفر `WakeActivity` لإيقاظ عملية المكون الإضافي.

يبني المكون الإضافي إصدار OpenCC الرسمي `ver.1.4.2` مباشرة عند الالتزام `025f371dc76b598d77384fbdab90c937471844d8` مع موارد الإصدار نفسه. تحتوي كل ABI على ملف `libopencc_jni.so` واحد مرتبط ساكنا ومحاذى إلى 16 KB, ويظل التحويل محليا بالكامل.

******

### خارطة الطريق

******

تدون خطط المكون الإضافي وتقدمه في ROADMAP.md بوصفها قائمة قابلة للتأشير, منظمة حسب مراحل رئيسية مع شروط قبول, وتغطي الوثائق وتجربة الإصدار, والهندسة والتكامل المستمر, وتعزيز قدرات التحويل, وتطور بيئة التشغيل. البنود غير المؤشرة تعبر عن نوايا لا عن قدرات حالية; ونرحب بالنقاش عبر Issues.

- [عرض ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md)

******

### سجل الإصدارات

******

#### v1.3.0

_2026/09/03_

- `تلميح` تعمل حزمة APK نفسها الآن كتطبيق مستقل يعمل بالكامل دون اتصال على Android 7.0 فما بعد, وتستمر أيضا كمكون AutoJs6 الإضافي الحالي; ولا يلزم AutoJs6 إلا لمسار المكون الإضافي
- `ميزة` إضافة مشغل من الشاشة الرئيسية ومحرر يعمل بالكامل دون اتصال لكل أنواع تحويل OpenCC الأربعة عشر, مع إجراءات التحويل والإلغاء والمسح واللصق والتبديل والنسخ والمشاركة, ومعالجة النص الطويل في الخلفية واستعادة الحالة بعد تدوير الشاشة أو إعادة إنشاء العملية
- `ميزة` إضافة واجهة مستقلة بعشر لغات تدعم السمات الفاتحة والداكنة واتجاه RTL والخطوط الكبيرة ودلالات TalkBack وترتيب التركيز واختصارات لوحة المفاتيح ومناطق تحرير قابلة للتمرير والتحديد بشكل مستقل وتخطيطات متجاوبة للهاتف والجهاز اللوحي والشاشة المنقسمة
- `تحسين` اشتراك المدخل المستقل ومدخل Binder في خلفية OpenCC الرسمية الوحيدة على مستوى العملية, مع الحفاظ على applicationId وهوية التوقيع وحدود إذن المكون الإضافي وأرقام معاملات AIDL والإعدادات الافتراضية للعمل دون اتصال ومن دون سجل
- `تحسين` توسيع التحقق ليشمل minSdk 24 وARM ‏32 بت وarm64 وx86 وx86_64 وصفحات 16 KB فعلية; وتدقيق خصائص locale وmanifest وR8 وELF وZIP لملفات APK النهائية وتثبيت لقطات واجهة أصلية قابلة لإعادة الإنتاج
- `تحسين` التحقق من أن الترقية الموضعية من v1.2.0 تحتفظ بمعرف UID للحزمة وخدمة المكون الإضافي مع إضافة Launcher واحد فقط, ثم تشغيل تحويلات الواجهة ومعاملة Binder القديمة الخام على release مصغرة وموقعة

#### v1.2.0

_2026/09/01_

- `تلميح` تغير تحديثات قواميس OpenCC 1.4.2 بعض النتائج عمدا, ومنها `复盘` -> `復盤` و`内卷` -> `內捲` والحفاظ على `什么怎么这么` و`内存条` -> `記憶體模組`; وترد القائمة المراجعة كاملة في تقرير الانتقال
- `تحسين` بناء OpenCC 1.4.2 الرسمي وقواميس الإصدار نفسه مباشرة في مكتبة JNI واحدة مرتبطة ساكنا لكل ABI مع إبقاء التحويل كله محليا
- `تحسين` دعم الأجهزة ذات حجم الصفحة 16 KB باستخدام NDK 28.2 ومحاذاة ELF وZIP إلى 16 KB والتحقق من Binder على محاكي حقيقي بحجم صفحة 16 KB
- `تحسين` تثبيت ZIP الموارد المثبت ذريًا مع التحقق من الحجم وSHA-256 والاسترداد التلقائي عند التلف وتحويل JNI آمن لـ Unicode وتخزين المحولات الساخنة مؤقتا
- `تبعية` إزالة الغلاف غير المصان `com.github.brooklet:android-opencc:1.2.2` وتثبيت OpenCC الرسمي `ver.1.4.2` عند الالتزام `025f371dc76b598d77384fbdab90c937471844d8`
- `تبعية` توثيق مصادر وتراخيص OpenCC وMarisa Trie وDarts Clone وRapidJSON المضمنة في `THIRD_PARTY_NOTICES.md`

#### v1.1.0

_2026/09/01_

- `ميزة` ترقية عقد مكون OpenCC الإضافي إلى الإصدار 2 مع `getSupportedConversionTypes()`, مما يتيح للمضيفات الحديثة اكتشاف أنواع التحويل الأربعة عشر التي يدعمها المكون فعليا
- `ميزة` إضافة `convertBatch(texts, conversionType)` لتحويل ما يصل إلى 1024 مقطعا نصيا في رحلة Binder واحدة مع الإبقاء على مسار الاستدعاء لكل عنصر للمضيفات القديمة
- `ميزة` إضافة `convertChain(text, conversionTypes)` لتنفيذ ما يصل إلى 32 مرحلة بالترتيب في استدعاء واحد, مما يخفض طرق التحويل المركبة في المضيفات الحديثة من 3 رحلات Binder كحد أقصى إلى رحلة واحدة
- `تحسين` تقديم تعليمات مترجمة عبر `PluginInfo.instruction` والإبلاغ عن إصدار العقد وأنواع التحويل المدعومة عبر capabilities
- `تحسين` الحفاظ على طرق AIDL الأصلية وأرقام المعاملات, مع اختبارات وحدات واختبارات Binder حقيقية للاستدعاءات الموسعة والتراجع إلى العقد القديم وحدود الحجم ومسارات الخطأ
- `تحسين` توحيد تخطيط README وطريقة إدارة إصدارات منصة Gradle

##### لمزيد من سجل الإصدارات

* [CHANGELOG.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/assets/doc/CHANGELOG-ar.md)

******

### البناء والتحقق

******

هذا القسم موجه للمطورين الراغبين في بناء المكون الإضافي من الشفرة المصدرية; ويكفي المستخدمين العاديين تثبيت ملفات APK الجاهزة من صفحة Releases.

بناء ملف APK من نوع debug:

```powershell
.\gradlew.bat :app:assembleDebug
```

تشغيل اختبارات JVM الوحدوية وبناء ملف APK لاختبارات instrumentation:

```powershell
.\gradlew.bat :app:testDebugUnitTest :app:assembleDebugAndroidTest
```

بناء ملفات APK من نوع release:

```powershell
.\gradlew.bat :app:assembleRelease
```

جمع نواتج الإصدار وإلحاق الإصدار وABI وملخص CRC32 باسم كل ملف:

```powershell
.\gradlew.bat :app:appendDigestToReleasedFiles
```

بناء ملفات APK للإصدار وتجهيز الملخصات وملاحظات الإصدار:

```powershell
py scripts\release\prepare_release.py
```

التحقق من تزامن مصادر الوثائق متعددة اللغات مع النواتج المولدة (يفرضه CI أيضا):

```powershell
py .python\generate_markdown.py --check
```

يتطلب البناء JDK 17 أو أحدث وAndroid SDK 36; وتدار إصدارات Gradle والمكونات الإضافية مركزيا عبر `version.properties` و`io.github.supermonster003.autojs6-platform-versions`.

******

### الترجمة وتوليد الوثائق

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

ملف `.readme/android_strings.json` هو المصدر الوحيد لنصوص الواجهة المستقلة وأخطاء الخدمة, وتوفر ملفات JSON اللغوية نص README ومركز المكونات. عدل مصادر JSON في `.readme/` و`.changelog/` ثم شغل `py .python/generate_markdown.py`; ولا تحرر ملفات `strings.xml` و`plugin_instruction.md` وREADME وسجل التغييرات المولدة يدويا. يتحقق `--check` من النواتج الـ 47.

******

### الترخيص

******

يوزع رمز المشروع بموجب [Mozilla Public License 2.0](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE). ويستخدم تحويل النص الصيني [OpenCC](https://github.com/BYVoid/OpenCC) (Apache License 2.0) مباشرة; وترد مصادر وتراخيص OpenCC وMarisa Trie وDarts Clone وRapidJSON المضمنة في [إشعارات الجهات الخارجية](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/THIRD_PARTY_NOTICES.md).

******

### الروابط

******

- وثائق AutoJs6 OpenCC: https://docs.autojs6.com/#/opencc
- مشروع AutoJs6: https://github.com/SuperMonster003/AutoJs6
- مشروع OpenCC الرسمي: https://github.com/BYVoid/OpenCC
- إشعارات الجهات الخارجية: https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/THIRD_PARTY_NOTICES.md
