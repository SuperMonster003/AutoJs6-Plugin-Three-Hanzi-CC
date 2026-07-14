Utilisez OpenCC pour convertir du texte chinois :

```js
let text = "汉字转换";
let converted = opencc.convert(text, "S2T");
console.log(converted);
```

Des méthodes raccourcies sont aussi disponibles :

```js
console.log(opencc.s2t("汉字转换"));
console.log(opencc.t2s("漢字轉換"));
```

Les types de conversion courants incluent `S2T`, `T2S`, `S2HK`, `S2TW`, `S2TWP`, `T2HK`, `T2TW`, `HK2S`, `HK2T`, `TW2S` et `TW2SP`.

Pour plus d'exemples, consultez la section [OpenCC](https://docs.autojs6.com/#/opencc) de la documentation AutoJs6.
