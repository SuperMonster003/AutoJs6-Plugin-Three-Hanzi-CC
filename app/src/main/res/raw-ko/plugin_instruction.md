OpenCC로 중국어 텍스트를 변환합니다:

```js
let text = "汉字转换";
let converted = opencc.convert(text, "S2T");
console.log(converted);
```

단축 메서드도 사용할 수 있습니다:

```js
console.log(opencc.s2t("汉字转换"));
console.log(opencc.t2s("漢字轉換"));
```

일반적인 변환 유형에는 `S2T`, `T2S`, `S2HK`, `S2TW`, `S2TWP`, `T2HK`, `T2TW`, `HK2S`, `HK2T`, `TW2S`, `TW2SP`가 있습니다.

더 많은 사용 예시는 AutoJs6 문서의 [OpenCC](https://docs.autojs6.com/#/opencc) 섹션을 참고하세요.
