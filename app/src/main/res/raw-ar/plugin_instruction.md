استخدم OpenCC لتحويل النص الصيني:

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

تشمل أنواع التحويل الشائعة `S2T` و `T2S` و `S2HK` و `S2TW` و `S2TWP` و `T2HK` و `T2TW` و `HK2S` و `HK2T` و `TW2S` و `TW2SP`.

لمزيد من أمثلة الاستخدام، راجع قسم [OpenCC](https://docs.autojs6.com/#/opencc) في وثائق AutoJs6.
