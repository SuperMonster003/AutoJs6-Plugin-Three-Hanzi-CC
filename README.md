# AutoJs6 OpenCC Plugin

[中文](#中文) | [English](#english)

## 中文

[English](#english)

AutoJs6 OpenCC 插件为 AutoJs6 提供基于 OpenCC 的中文文本转换能力, 支持简体/繁体/香港繁体/台湾繁体和日文新字体相关转换.

### 功能

- 提供 `opencc` 插件服务, 插件 ID 为 `opencc`.
- 支持 AutoJs6 中的 `opencc.convert(text, type)` 和 `opencc.s2t(text)` / `opencc.t2s(text)` 等快捷方法.
- 插件信息和使用说明已支持多语言资源: 西班牙语/法语/俄语/阿拉伯语/日语/韩语/英语/简体中文/香港繁体和台湾繁体.
- 基于 `com.github.brooklet:android-opencc`.

### 使用示例

```js
let text = "汉字转换";
let converted = opencc.convert(text, "S2T");
console.log(converted);
```

也可以使用快捷方法:

```js
console.log(opencc.s2t("汉字转换"));
console.log(opencc.t2s("漢字轉換"));
```

### 转换类型

常用 OpenCC 转换类型包括:

```text
S2T, S2TW, S2TWP, S2HK,
T2S, T2TW, T2HK, T2JP,
TW2S, TW2T, TW2SP,
HK2S, HK2T,
JP2T
```

AutoJs6 还提供若干组合快捷方法, 例如 `s2jp`/`hk2tw`/`tw2hk`/`jp2s` 等.

### 发行历史

###### 2026/07/14

* `新增` OpenCC 插件服务, 插件 ID 为 `opencc`, 引擎为 `opencc`
* `新增` 支持通过 `org.autojs.plugin.OPENCC` 发现并调用插件
* `新增` 支持 OpenCC 常用转换类型: `S2T`/`S2TW`/`S2TWP`/`S2HK`/`T2S`/`T2TW`/`T2HK`/`T2JP`/`TW2S`/`TW2T`/`TW2SP`/`HK2S`/`HK2T`/`JP2T`
* `新增` 插件信息和使用说明的多语言资源: 西班牙语/法语/俄语/阿拉伯语/日语/韩语/英语/简体中文/香港繁体/台湾繁体
* `新增` 中英双语 README, 包含用法示例/构建说明和相关链接

### 构建

```powershell
.\gradlew.bat :app:assembleDebug
```

Release 构建:

```powershell
.\gradlew.bat :app:assembleRelease
```

构建参数来自 `version.properties`, 当前最低 SDK 为 24, 目标 SDK 为 36.

### 资源结构

```text
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

`strings.xml` 提供插件描述和错误信息本地化;`plugin_instruction.md` 提供宿主侧展示的插件使用说明.

### 相关链接

- AutoJs6 OpenCC 文档: https://docs.autojs6.com/#/opencc
- OpenCC 官方项目: https://github.com/BYVoid/OpenCC
- Android OpenCC 项目: https://github.com/qichuan/android-opencc

## English

[中文](#中文)

The AutoJs6 OpenCC Plugin provides OpenCC-powered Chinese text conversion for AutoJs6. It supports conversions between Simplified Chinese, Traditional Chinese, Hong Kong Traditional Chinese, Taiwan Traditional Chinese, and Japanese Shinjitai related forms.

### Features

- Provides the `opencc` plugin service with plugin ID `opencc`.
- Supports AutoJs6 APIs such as `opencc.convert(text, type)` and shortcuts like `opencc.s2t(text)` / `opencc.t2s(text)`.
- Plugin metadata and usage instructions are localized for Spanish, French, Russian, Arabic, Japanese, Korean, English, Simplified Chinese, Hong Kong Traditional Chinese, and Taiwan Traditional Chinese.
- Built on `com.github.brooklet:android-opencc`.

### Usage

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

### Conversion Types

Common OpenCC conversion types include:

```text
S2T, S2TW, S2TWP, S2HK,
T2S, T2TW, T2HK, T2JP,
TW2S, TW2T, TW2SP,
HK2S, HK2T,
JP2T
```

AutoJs6 also provides composed shortcut methods such as `s2jp`, `hk2tw`, `tw2hk`, and `jp2s`.

### Release History

###### 2026/07/14

* `Feature` Added the OpenCC plugin service with plugin ID `opencc` and engine `opencc`.
* `Feature` Added host discovery and invocation through `org.autojs.plugin.OPENCC`.
* `Feature` Supported common OpenCC conversion types: `S2T`, `S2TW`, `S2TWP`, `S2HK`, `T2S`, `T2TW`, `T2HK`, `T2JP`, `TW2S`, `TW2T`, `TW2SP`, `HK2S`, `HK2T`, and `JP2T`.
* `Feature` Added localized plugin metadata and usage instructions for Spanish, French, Russian, Arabic, Japanese, Korean, English, Simplified Chinese, Hong Kong Traditional Chinese, and Taiwan Traditional Chinese.
* `Feature` Added a bilingual Chinese/English README with usage examples, build instructions, and related links.

### Build

```powershell
.\gradlew.bat :app:assembleDebug
```

Release build:

```powershell
.\gradlew.bat :app:assembleRelease
```

Build parameters come from `version.properties`. The current minimum SDK is 24 and target SDK is 36.

### Resource Layout

```text
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

`strings.xml` contains localized plugin descriptions and error messages. `plugin_instruction.md` contains usage instructions displayed by the host.

### Links

- AutoJs6 OpenCC documentation: https://docs.autojs6.com/#/opencc
- OpenCC official project: https://github.com/BYVoid/OpenCC
- Android OpenCC project: https://github.com/qichuan/android-opencc
