{{ p_introduction_what }}

{{ p_instruction_backend }}

### {{ h3_quick_start }}

{{ p_quick_start_intro }}:

```javascript
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
```

### {{ h3_conversion_types }}

{{ p_conversion_types_intro }}:

```text
S2T   T2S   S2TW  TW2S  S2TWP  TW2SP  S2HK
HK2S  T2TW  TW2T  T2HK  HK2T   T2JP   JP2T
```

{{ p_conversion_types_phrase_note }}

### {{ h3_self_check }}

{{ p_self_check_intro }}:

```javascript
console.log(opencc.s2t("汉字转换"));
```

{{ p_self_check_result }}

{{ p_instruction_more }}
