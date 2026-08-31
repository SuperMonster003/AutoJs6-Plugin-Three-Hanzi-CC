<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>用于中文文本转换的 OpenCC 插件</p>

  <p>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/SuperMonster003/AutoJs6-Plugin-OpenCC?label=Release"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/SuperMonster003/AutoJs6-Plugin-OpenCC?color=A24232&label=Issues"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/SuperMonster003/AutoJs6-Plugin-OpenCC?color=534BAE&label=License"/></a>
  </p>
</div>

******

### 语言 (Languages)

******

当前 README.md 支持以下语言:

- 简体中文 [zh-Hans] # 当前
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-en.md)
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-fr.md)
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-es.md)
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ja.md)
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ko.md)
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ru.md)
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ar.md)

******

### 简介

******

OpenCC 插件 (OpenCC Plugin) 为 AutoJs6 提供基于 [OpenCC](https://github.com/BYVoid/OpenCC) 的中文文本转换能力. 安装本插件后, AutoJs6 脚本中的全局对象 `opencc` 即可正常工作, 一行代码即可在简体, 繁体, 香港繁体, 台湾正体与日文新字体之间完成转换, 无需导入模块, 无需联网.

插件采用宿主与插件分工的设计: AutoJs6 宿主提供脚本直接调用的 `opencc` API, 插件以独立应用的形式携带 OpenCC 转换引擎与词典. 从 AutoJs6 6.8.0 起宿主不再内置 OpenCC 运行时, 中文转换功能由本插件按需提供; 这样宿主安装包保持精简, 转换引擎也可以独立于宿主更新.

******

### 功能亮点

******

- 开箱即用: 插件安装到设备后由 AutoJs6 自动发现, 无需重启宿主, 无需任何配置, 脚本即可直接调用 `opencc` 全局对象.
- 14 种标准转换: 覆盖 OpenCC 的简繁转换, 香港/台湾地区用字转换与日文新字体转换, 并支持台湾常用词汇转换 (如 `软件` 与 `軟體` 的互换).
- 33 个脚本方法: 除通用的 `opencc.convert(text, type)` 外, 每种转换类型都有同名快捷方法, 还提供 `s2jp`, `tw2hk` 等 18 个别名与组合方法.
- 完全离线: 转换基于插件内置词典在设备本地完成, 插件不申请网络权限, 不收集任何数据.
- 按需选包: 提供 4 种单架构安装包与包含全部架构的 `universal` 包, 设备只需安装匹配包, 体积更小.
- 多语言: 插件信息, 使用说明, README 与更新日志覆盖 10 种语言.
- 轻量后台: 插件无独立界面, 由宿主按需唤醒与绑定, 空闲时自动释放连接.

******

### 界面截图

******

以下为 AutoJs6 插件中心的真实运行截图. OpenCC 1.0.2 (17) 已被宿主识别, 右侧开关处于启用状态. 画面保留原始 Android 截图, 未裁剪或调色.

<table>
  <tr>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/plugin-center-enabled.png?raw=true"
           alt="插件中心已识别并启用 OpenCC 1.0.2" width="360" />
      <br />
      <sub>插件中心已识别并启用 OpenCC 1.0.2</sub>
    </td>
  </tr>
</table>

******

### 使用方法

******

1. 将 AutoJs6 升级到内部版本号 3923 (6.7.1 Alpha4) 及以上; 6.8.0 正式版及更新版本均满足要求.
2. 从 [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) 页面或 AutoJs6 插件中心下载并安装插件 APK; 拿不准选哪个安装包时, 可直接选 `universal` 包, 或参考下方 `如何选择安装包`.
3. 打开 AutoJs6 的插件中心, 确认 `OpenCC` 插件已被识别并处于启用状态; 官方发布包会自动通过签名校验, 无需手动授权.
4. 在脚本中直接使用 `opencc` 全局对象, 例如 `opencc.s2t("汉字")`; 无需 require 或 import, 安装插件后也无需重启 AutoJs6.

> 插件支持 Android 7.0 (API 24) 及以上的设备. 若脚本运行时提示缺少插件或宿主版本过低, 请参考下方 `常见问题`.

******

### 快速上手

******

安装完成后, 以下脚本可直接运行, 注释为预期输出:

```javascript
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.t2jp("圖書館"));      // => 図書館
```

快捷方法与通用方法 `opencc.convert(text, type)` 等价; `opencc` 对象本身也可以作为函数调用, 转换类型名不区分大小写:

```javascript
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
console.log(opencc("汉字转换", "s2t"));         // => 漢字轉換
```

所有方法均同步返回转换后的字符串, 转换在本地词典上完成, 不产生任何网络请求.

******

### 转换类型

******

`convert` 方法与同名快捷方法支持以下 14 种 OpenCC 标准转换类型, 类型名中 S 表示简体, T 表示繁体 (OpenCC 标准), HK 表示香港繁体, TW 表示台湾正体, JP 表示日文新字体:

| 类型 | 转换方向 |
|---|---|
| `S2T` | 简体到繁体 |
| `T2S` | 繁体到简体 |
| `S2TW` | 简体到台湾正体 |
| `TW2S` | 台湾正体到简体 |
| `S2TWP` | 简体到台湾正体, 并替换为台湾常用词汇 (如 `内存` 转为 `記憶體`) |
| `TW2SP` | 台湾正体到简体, 并替换为大陆常用词汇 (如 `滑鼠` 转为 `鼠标`) |
| `S2HK` | 简体到香港繁体 |
| `HK2S` | 香港繁体到简体 |
| `T2TW` | 繁体到台湾正体 |
| `TW2T` | 台湾正体到繁体 |
| `T2HK` | 繁体到香港繁体 |
| `HK2T` | 香港繁体到繁体 |
| `T2JP` | 繁体 (旧字体) 到日文新字体 |
| `JP2T` | 日文新字体到繁体 (旧字体) |

带 `P` 后缀的类型在逐字转换之外还会进行词汇替换, 使结果更符合当地表达习惯; 不带 `P` 的类型只转换字形, 不改动用词.

`T2JP` 与 `JP2T` 在繁体旧字形与日文新字体 (Shinjitai) 之间转换, 例如 `圖書館` 与 `図書館`; 它们处理的是汉字字形差异, 而非中文与日文之间的翻译.

******

### 脚本方法

******

宿主侧的 `opencc` 全局对象共提供 33 个方法: 通用方法 `convert`, 14 个核心快捷方法, 以及 18 个别名与组合方法. `convert(text, type)` 的 `type` 参数接受全部 32 个转换名 (核心与组合均可), 不区分大小写; 传入未知类型会抛出 `Unknown OpenCC conversion type` 异常.

14 个核心快捷方法与上表的转换类型一一对应, 每次调用执行一次插件转换:

```text
s2t   t2s   s2tw  tw2s  s2twp  tw2sp  s2hk
hk2s  t2tw  tw2t  t2hk  hk2t   t2jp   jp2t
```

`s2twi` 与 `twi2s` 分别是 `s2twp` 与 `tw2sp` 的别名 (`twi` 表示 Taiwan idiom, 即台湾常用词汇), 行为完全相同.

其余 16 个组合方法由多次核心转换按顺序串联而成, 用于没有直达词典的转换方向:

```text
s2jp   = s2t  + t2jp          jp2s   = jp2t + t2s
hk2tw  = hk2t + t2tw          tw2hk  = tw2t + t2hk
hk2jp  = hk2t + t2jp          tw2jp  = tw2t + t2jp
t2twi  = t2s  + s2twi         twi2t  = twi2s + s2t
hk2twi = hk2s + s2twi         twi2hk = twi2s + s2hk
tw2twi = tw2s + s2twi         twi2tw = twi2s + s2tw
jp2hk  = jp2t + t2hk          jp2tw  = jp2t + t2tw
twi2jp = twi2s + s2t + t2jp   jp2twi = jp2t + t2s + s2twi
```

支持扩展契约的新版宿主会将整条组合链作为一次插件调用; 例如 `twi2jp` 的 3 个转换阶段只需 1 次 Binder 往返. 旧宿主仍按阶段调用, 与本插件保持兼容.

******

### 如何选择安装包

******

每个发行版本包含 5 个 APK, 差别仅在于内置了哪些处理器架构 (ABI) 的 OpenCC 原生库:

| 安装包 | 适用对象 |
|---|---|
| `arm64-v8a` | 绝大多数现代 Android 手机与平板 (64 位 ARM), 优先选择 |
| `armeabi-v7a` | 较早期的 32 位 ARM 设备 |
| `x86_64` | 64 位 x86 模拟器与少数 x86 设备 |
| `x86` | 32 位 x86 模拟器与少数 x86 设备 |
| `universal` | 内置全部 4 种架构, 体积最大; 适用于任何设备, 也是拿不准架构时的稳妥选择 |

若误装了与设备架构不匹配的单架构包, 插件将无法正常提供转换服务, 换装 `universal` 包即可解决.

******

### 快速自检

******

确认插件已安装并在插件中心处于启用状态后, 运行以下单行脚本即可完成端到端验证:

```javascript
console.log(opencc.s2t("汉字转换"));
```

输出 `漢字轉換` 即表示插件链路完整可用. 若脚本报错, 请按提示排查: 提示缺少插件时安装本插件; 提示未启用或未授权时到插件中心开启对应开关; 提示需要更高版本的宿主环境时升级 AutoJs6.

******

### 常见问题

******

#### 如何确认插件已经生效?

打开 AutoJs6 的插件中心, 能看到 `OpenCC` 插件并处于启用状态即表示宿主已识别; 再运行上方 `快速自检` 脚本, 输出 `漢字轉換` 即为生效.

#### 为什么应用列表里没有插件的图标?

这是正常现象. 插件没有独立界面, 也不在桌面创建启动图标, 安装后由 AutoJs6 在后台自动发现和调用, 全部交互都在 AutoJs6 内完成.

#### 脚本提示 `缺少 "OpenCC plugin" 所需的插件`, 怎么办?

这表示 AutoJs6 未在设备上发现本插件. 安装插件后再次运行脚本即可, 无需重启 AutoJs6; 若已安装仍提示缺失, 请确认插件未被系统或安全软件卸载, 并检查插件中心的启用与授权状态.

#### `s2tw` 和 `s2twp` (`s2twi`) 有什么区别?

`s2tw` 只做字形转换 (如 `软` 转为 `軟`), 不改动用词; `s2twp` 在此基础上还会把大陆用词替换为台湾常用词汇 (如 `软件` 转为 `軟體`, `鼠标` 转为 `滑鼠`), `s2twi` 是它的别名. 面向台湾读者的正式文本通常选 `s2twp`, 只需统一字形时选 `s2tw`.

#### 为什么 Node.js 引擎的脚本里用不了 `opencc`?

`opencc` 目前是 Rhino (AutoJs6 默认 JavaScript 引擎) 专属的全局对象, Node.js 运行时暂未提供对应实现. 相关支持计划可关注 [ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md).

#### 转换需要联网吗? 长文本会不会很慢?

不需要联网, 全部转换基于插件内置的 OpenCC 词典在本地完成. 每次方法调用对应一次跨进程通信, 单次转换较长文本通常一次往返即可; 高频循环调用时建议优先使用核心类型, 避免组合方法带来的多次往返.

#### 插件会申请哪些权限? 数据安全吗?

插件仅声明用于与 AutoJs6 通信的插件权限, 不申请网络, 存储等任何敏感系统权限; 服务本身也受同一权限保护, 其他应用无法调用. 待转换的文本只在设备内存中处理, 不会被存储或上传.

******

### 权限与安全

******

插件与 AutoJs6 之间通过 Android 系统的权限与签名机制建立信任:

- 最小权限: 插件清单仅声明 `org.autojs.permission.PLUGIN` 插件权限, 不含网络, 存储, 相机等任何敏感系统权限.
- 双向防护: 插件服务同样受该权限保护, 只有持有插件权限的宿主 (如 AutoJs6) 才能绑定与调用, 其他应用无法访问.
- 签名授权: AutoJs6 会校验插件签名, 官方发布包自动获得授权; 非官方签名的构建需在插件中心手动授权后才会被加载.
- 本地处理: 转换完全在设备本地完成, 插件不联网, 不落盘, 不收集任何用户数据.

请仅从官方 [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) 页面或 AutoJs6 插件中心获取插件. 来源不明的安装包即使版本号相同, 也可能无法通过宿主校验或暗藏风险.

******

### 插件接口

******

以下信息面向 AutoJs6 宿主与插件开发者, 宿主通过这些标识发现插件并完成兼容性协商:

```text
application id: io.github.supermonster003.autojs6.plugin.opencc
plugin id: opencc
engine: opencc
variant: default
service action: org.autojs.plugin.OPENCC
service category: opencc
aidl interface: org.autojs.plugin.opencc.api.IOpenccPlugin
aidl contract version: 2
aidl methods: getInfo(), convert(text, conversionType), getSupportedConversionTypes(), convertBatch(texts, conversionType), convertChain(text, conversionTypes)
batch/chain limits: 1024 texts / 32 stages
minimum host build: 3923 (6.7.1 Alpha4)
conversion library: com.github.brooklet:android-opencc:1.2.2
```

`OpenccPluginService` 响应 `org.autojs.plugin.OPENCC` action (category `opencc`), Binder 接口为 opencc-api 的 `org.autojs.plugin.opencc.api.IOpenccPlugin`. 契约版本 2 在原有 `getInfo()` 与 `convert(text, conversionType)` 之后追加类型发现, 批量转换与链式转换方法, 并通过 `PluginInfo.capabilities` 广告版本与支持类型; 旧宿主继续使用原有方法和事务编号. 另提供 `WakeActivity` 供宿主唤醒插件进程.

`PluginInfo.supportedAbis` 上报 `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86` 四种架构, 供宿主与插件中心识别可用变体; 转换由 `com.github.brooklet:android-opencc:1.2.2` 提供的 OpenCC 引擎与词典完成.

******

### 开发路线图

******

插件的能力规划与完成情况以可勾选清单维护在 ROADMAP.md 中, 按里程碑组织并附验收条件, 涵盖文档与发布体验, 工程化与持续集成, 转换能力增强与运行时演进等方向. 未勾选条目表示规划意向而非当前版本能力, 欢迎通过 Issues 参与讨论.

- [查看 ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md)

******

### 发行历史

******

#### v1.1.0

_2026/08/31_

- `新增` 升级到 OpenCC 插件契约版本 2, 新增 `getSupportedConversionTypes()`, 供新版宿主动态发现当前实际支持的 14 种转换类型
- `新增` 新增 `convertBatch(texts, conversionType)`, 单次 Binder 往返最多转换 1024 段文本, 同时保留旧宿主逐项调用的兼容路径
- `新增` 新增 `convertChain(text, conversionTypes)`, 单次调用最多顺序执行 32 个阶段, 让新版宿主的组合方法从最多 3 次 Binder 往返降为 1 次
- `优化` 通过 `PluginInfo.instruction` 交付调用方语言的插件说明, 并通过 capabilities 上报契约版本与支持的转换类型
- `优化` 保持原有 AIDL 方法及事务编号不变, 并为扩展调用, 旧契约回退, 大小上限与异常路径补充单元测试和真实 Binder 测试

#### v1.0.2

_2026/08/31_

- `提示` 本版本只改进文档与构建流程, OpenCC 转换行为和 14 种核心转换类型保持不变
- `优化` 重构 10 种语言的 README, 新增安装步骤, 选包指南, 快速自检, 33 个脚本方法清单, 常见问题与权限安全说明
- `优化` 将插件中心使用说明纳入同一套多语言 JSON 生成链路, 让 README, CHANGELOG 与 Android 资源由单一来源同步生成
- `优化` 增强文档校验脚本并接入 GitHub Actions, 自动检测跨语言结构不一致, 生成产物漂移, 孤儿文件, 版本不对齐与残留占位符
- `优化` 新增 ROADMAP.md, 以可验收的里程碑清单公开维护文档, 工程化, 转换能力与运行时演进计划
- `优化` 迁移 Gradle 构建配置到 `org.autojs.build.platform-versions` 1.4.1, 并通过 foojay 自动解析 JDK, 简化并统一构建环境

#### v1.0.1

_2026/07/14_

- `优化` 提供按处理器架构 (ABI) 拆分的安装包: `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86` 单架构包与包含全部架构的 `universal` 包, 设备按需安装, 体积更小
- `优化` 插件信息上报支持的 ABI 列表, AutoJs6 与插件中心可据此识别当前设备可用的插件变体
- `优化` 发布 APK 文件名附带版本号, 架构与 CRC32 校验码, 便于核对下载文件的完整性

##### 更多发行历史可参阅

* [CHANGELOG.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/assets/doc/CHANGELOG-zh-Hans.md)

******

### 构建与校验

******

本节面向希望从源码构建插件的开发者; 普通用户直接安装 Releases 页面的成品 APK 即可.

构建 debug APK:

```powershell
.\gradlew.bat :app:assembleDebug
```

运行 JVM 单元测试并构建 instrumentation 测试 APK:

```powershell
.\gradlew.bat :app:testDebugUnitTest :app:assembleDebugAndroidTest
```

构建 release APK; 在不入库的 `sign.properties` 中配置签名身份后自动签名, 未配置签名时产物不可发布:

```powershell
.\gradlew.bat :app:assembleRelease
```

归集发布产物并在文件名中附加版本号, 架构与 CRC32 校验码:

```powershell
.\gradlew.bat :app:appendDigestToReleasedFiles
```

一键构建并校验 5 个已签名 APK, 生成 `SHA256SUMS.txt` 与基于英文 CHANGELOG 的 `RELEASE_NOTES.md`:

```powershell
py scripts\release\prepare_release.py
```

校验多语言文档源与生成产物是否同步 (持续集成亦会执行):

```powershell
py .python\generate_markdown.py --check
```

构建需要 JDK 17 及以上与 Android SDK 36; Gradle 与各插件版本由 `version.properties` 及 `io.github.supermonster003.autojs6-platform-versions` 统一管理.

******

### 本地化与文档生成

******

```text
.readme/common.json
.readme/lang_*.json
.readme/template_readme.md
.readme/template_plugin_instruction.md
.changelog/lang_*.json
.changelog/template_changelog.md
.python/generate_markdown.py
docs/images/screenshots/README.md
docs/images/screenshots/plugin-center-enabled.png
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

`strings.xml` 提供本地化插件描述与错误信息, `plugin_instruction.md` 提供宿主插件中心内展示的使用说明. README 与更新日志一律修改 `.readme/` 与 `.changelog/` 下的 JSON 源文件, 再运行 `py .python/generate_markdown.py` 重新生成, 生成产物不手工编辑; 运行 `py .python/generate_markdown.py --check` 可校验源文件与生成产物是否同步.

******

### 许可

******

项目代码使用 [Mozilla Public License 2.0](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE). 中文转换能力来自 [OpenCC](https://github.com/BYVoid/OpenCC) (Apache License 2.0) 及其 Android 封装 [android-opencc](https://github.com/brooklet/android-opencc).

******

### 相关链接

******

- AutoJs6 OpenCC 文档: https://docs.autojs6.com/#/opencc
- AutoJs6 项目: https://github.com/SuperMonster003/AutoJs6
- OpenCC 官方项目: https://github.com/BYVoid/OpenCC
- Android OpenCC 项目: https://github.com/brooklet/android-opencc
