The OpenCC Plugin brings [OpenCC](https://github.com/BYVoid/OpenCC)-based Chinese text conversion to AutoJs6. Once the plugin is installed, the global `opencc` object in AutoJs6 scripts just works: a single line of code converts text between Simplified Chinese, Traditional Chinese, Hong Kong Traditional, Taiwan Traditional, and Japanese Shinjitai, with no imports and no network access.

This release embeds official OpenCC 1.4.2 and its pinned same-release dictionaries. Processing remains fully offline, and the native packages support Android devices with 16 KB memory pages.

### Quick Start

After installation the following script runs as-is; the comments show the expected output:

```javascript
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
```

### Conversion Types

The `convert` method and the same-named shortcuts support the following 14 standard OpenCC conversion types, where S stands for Simplified, T for Traditional (OpenCC standard), HK for Hong Kong Traditional, TW for Taiwan Traditional, and JP for Japanese Shinjitai:

```text
S2T   T2S   S2TW  TW2S  S2TWP  TW2SP  S2HK
HK2S  T2TW  TW2T  T2HK  HK2T   T2JP   JP2T
```

Types with a `P` suffix also perform vocabulary substitution on top of character conversion, so the result reads naturally to local readers; types without `P` convert character forms only and leave the wording untouched.

### Quick Self-Check

After confirming the plugin is installed and enabled in the plugin center, run this one-line script for an end-to-end verification:

```javascript
console.log(opencc.s2t("汉字转换"));
```

An output of `漢字轉換` means the whole plugin chain works. If the script fails, follow the error message: install this plugin when it reports a missing plugin, toggle the corresponding switch in the plugin center when it reports the plugin is disabled or unauthorized, and update AutoJs6 when it requires a newer host.

See the [AutoJs6 OpenCC documentation](https://docs.autojs6.com/#/opencc) and the [project README](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC) for the full method list and conversion type reference.
