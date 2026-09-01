OpenCC 插件 (OpenCC Plugin) 为 AutoJs6 提供基于 [OpenCC](https://github.com/BYVoid/OpenCC) 的中文文本转换能力. 安装本插件后, AutoJs6 脚本中的全局对象 `opencc` 即可正常工作, 一行代码即可在简体, 繁体, 香港繁体, 台湾正体与日文新字体之间完成转换, 无需导入模块, 无需联网.

本版本内置官方 OpenCC 1.4.2 及固定在同一发行版的配套词典. 所有处理继续完全离线, 原生安装包支持使用 16 KB 内存页的 Android 设备.

### 快速上手

安装完成后, 以下脚本可直接运行, 注释为预期输出:

```javascript
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
```

### 转换类型

`convert` 方法与同名快捷方法支持以下 14 种 OpenCC 标准转换类型, 类型名中 S 表示简体, T 表示繁体 (OpenCC 标准), HK 表示香港繁体, TW 表示台湾正体, JP 表示日文新字体:

```text
S2T   T2S   S2TW  TW2S  S2TWP  TW2SP  S2HK
HK2S  T2TW  TW2T  T2HK  HK2T   T2JP   JP2T
```

带 `P` 后缀的类型在逐字转换之外还会进行词汇替换, 使结果更符合当地表达习惯; 不带 `P` 的类型只转换字形, 不改动用词.

### 快速自检

确认插件已安装并在插件中心处于启用状态后, 运行以下单行脚本即可完成端到端验证:

```javascript
console.log(opencc.s2t("汉字转换"));
```

输出 `漢字轉換` 即表示插件链路完整可用. 若脚本报错, 请按提示排查: 提示缺少插件时安装本插件; 提示未启用或未授权时到插件中心开启对应开关; 提示需要更高版本的宿主环境时升级 AutoJs6.

更多方法与完整转换类型说明参见 [AutoJs6 OpenCC 文档](https://docs.autojs6.com/#/opencc) 与 [项目 README](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC).
