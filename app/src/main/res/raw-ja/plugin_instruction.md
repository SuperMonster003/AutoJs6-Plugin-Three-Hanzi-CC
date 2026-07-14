OpenCC で中国語テキストを変換します:

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

よく使う変換タイプには `S2T`、`T2S`、`S2HK`、`S2TW`、`S2TWP`、`T2HK`、`T2TW`、`HK2S`、`HK2T`、`TW2S`、`TW2SP` があります。

その他の使用例は、AutoJs6 ドキュメントの [OpenCC](https://docs.autojs6.com/#/opencc) セクションを参照してください。
