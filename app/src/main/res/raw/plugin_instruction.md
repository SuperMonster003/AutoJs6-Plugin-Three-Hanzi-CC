Use OpenCC to convert Chinese text:

```js
let text = "汉字转换";
let converted = opencc.convert(text, "S2T");
console.log(converted);
```

Shortcut methods are also available:

```js
console.log(opencc.s2t("汉字转换"));
console.log(opencc.t2s("漢字轉換"));
```

Common conversion types include `S2T`, `T2S`, `S2HK`, `S2TW`, `S2TWP`, `T2HK`, `T2TW`, `HK2S`, `HK2T`, `TW2S`, and `TW2SP`.

For more usage examples, refer to the [OpenCC](https://docs.autojs6.com/#/opencc) section in the AutoJs6 documentation.
