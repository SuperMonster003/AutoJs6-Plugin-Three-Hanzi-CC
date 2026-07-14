使用 OpenCC 轉換中文文本:

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

常用轉換類型包括 `S2T`, `T2S`, `S2HK`, `S2TW`, `S2TWP`, `T2HK`, `T2TW`, `HK2S`, `HK2T`, `TW2S`, `TW2SP`.

更多用法可參考 AutoJs6 文件的 [OpenCC](https://docs.autojs6.com/#/opencc) 章節.
