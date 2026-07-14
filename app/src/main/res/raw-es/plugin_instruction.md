Usa OpenCC para convertir texto chino:

```js
let text = "汉字转换";
let converted = opencc.convert(text, "S2T");
console.log(converted);
```

También hay métodos abreviados:

```js
console.log(opencc.s2t("汉字转换"));
console.log(opencc.t2s("漢字轉換"));
```

Los tipos de conversión comunes incluyen `S2T`, `T2S`, `S2HK`, `S2TW`, `S2TWP`, `T2HK`, `T2TW`, `HK2S`, `HK2T`, `TW2S` y `TW2SP`.

Para más ejemplos de uso, consulta la sección [OpenCC](https://docs.autojs6.com/#/opencc) de la documentación de AutoJs6.
