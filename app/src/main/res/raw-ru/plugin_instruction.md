Используйте OpenCC для преобразования китайского текста:

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

Распространенные типы преобразования: `S2T`, `T2S`, `S2HK`, `S2TW`, `S2TWP`, `T2HK`, `T2TW`, `HK2S`, `HK2T`, `TW2S` и `TW2SP`.

Дополнительные примеры см. в разделе [OpenCC](https://docs.autojs6.com/#/opencc) документации AutoJs6.
