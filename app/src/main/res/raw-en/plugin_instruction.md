3-Hanzi CC is an offline Chinese converter based on OpenCC. It converts text between Simplified Chinese, Traditional Chinese, Hong Kong Traditional, Taiwan Traditional and Japanese Shinjitai. You can use it on its own from the launcher, and it also gives AutoJs6 scripts the global object `opencc`.

### Getting started

1. Open 3-Hanzi CC from the launcher and type text in "Source text", or tap "Paste" to read it from the clipboard.
2. Choose a direction in "Conversion type", then tap "Convert".
3. Read the output under "Result", then tap "Copy" or "Share" to use it.
4. In AutoJs6 scripts, call the global object `opencc` directly; see the example below.

### Main features

- **14 conversions**: Cover the common directions between Simplified, Traditional, Hong Kong Traditional, Taiwan Traditional and Japanese Shinjitai. Types marked "Taiwan terminology" also replace words, for example "鼠标" becomes "滑鼠".
- **Quick editing**: "Invert" switches to the opposite conversion direction, "Swap" exchanges the source text and the result, and "Clear" removes the text.
- **Offline conversion**: Conversion runs on the device with built-in dictionaries and needs no network; text is never uploaded or saved.
- **Personalization**: Adjust the language, dark mode, theme color and launcher icon. With "Remember conversion type" on, the last conversion type comes back the next time you open the app.
- **Plugin tool**: In AutoJs6 6.8.0 or later, the plugin also provides the `opencc_convert` tool, which plugins such as MCP Server and the `plugins.tools` API of scripts can call.

### Using it in scripts

Use the global object `opencc` in AutoJs6 scripts without importing anything. Every conversion type has a method of the same name, and `convert` takes the type as an argument:

```js
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
```

- Conversion types are case-insensitive, for example `S2T`, `S2TWP`, `HK2S` and `T2JP`. Combined methods such as `s2jp` and `hk2tw` run several conversions in sequence.
- Node.js scripts load it with `require('autojs6:opencc')` and Bun scripts use `host.opencc`; the methods are the same and all return a Promise.

### Requirements

- Android 7.0 or later. AutoJs6 is not needed when you use the app on its own from the launcher.
- Scripts need AutoJs6 6.7.1 Alpha4 or later, with this plugin enabled in "Plugin Center".
- Node.js scripts need the Node.js Runtime plugin 1.7.0 or later; Bun scripts need the Bun Runtime plugin 0.2.6 or later, with `text.opencc` left on in its settings page (on by default).
- The network permission is used only to check for app updates. "Automatically check for updates" is on by default, checks at most once every 12 hours, and can be turned off in "Settings".

### FAQ

**Using it without AutoJs6**

Open 3-Hanzi CC from the launcher to convert text; AutoJs6 is needed only when scripts call `opencc`.

**The difference between `s2tw` and `s2twp`**

`s2tw` converts characters only, for example "软件" becomes "軟件"; `s2twp` also switches to common Taiwan vocabulary, for example "软件" becomes "軟體". `s2twi` is an alias of `s2twp`.

**When a script reports a missing plugin**

Make sure this plugin is installed and enabled in "Plugin Center" of AutoJs6, then run the script again. AutoJs6 does not need a restart.

See [AutoJs6 docs > OpenCC](https://docs.autojs6.com/#/opencc) for all methods and conversion types and the [project page](https://github.com/SuperMonster003/AutoJs6-Plugin-Three-Hanzi-CC) for more information.
