<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>可独立使用并兼容 AutoJs6 的离线 OpenCC 中文转换器</p>

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

OpenCC 只需安装一个 APK, 即可通过两种入口使用基于 [OpenCC](https://github.com/BYVoid/OpenCC) 的中文文本转换: 直接从桌面启动完全离线的 Android App, 或让 AutoJs6 将同一个 APK 识别为插件并在脚本中使用全局对象 `opencc`. 两条路径都覆盖简体, 通用繁体, 香港繁体, 台湾正体与日文新字体.

独立编辑器与受权限保护的 AutoJs6 Binder 服务共用唯一的官方 OpenCC 引擎, 同一组固定词典, 缓存, 转换类型和错误模型. 独立 App 不要求安装 AutoJs6; 插件模式则保持现有脚本 API, 并允许转换引擎独立于宿主更新.

******

### 功能亮点

******

- 一个 APK, 两种用法: 无需 AutoJs6 即可从桌面图标进入可视化转换页面, 也可让 AutoJs6 脚本通过同一次安装调用 `opencc`.
- 14 种标准转换: 覆盖 OpenCC 的简繁转换, 香港/台湾地区用字转换与日文新字体转换, 并支持台湾常用词汇转换 (如 `软件` 与 `軟體` 的互换).
- 33 个脚本方法: 除通用的 `opencc.convert(text, type)` 外, 每种转换类型都有同名快捷方法, 还提供 `s2jp`, `tw2hk` 等 18 个别名与组合方法.
- 完全离线: 转换基于插件内置词典在设备本地完成, 插件不申请网络权限, 不收集任何数据.
- 按需选包: 提供 4 种单架构安装包与包含全部架构的 `universal` 包, 设备只需安装匹配包, 体积更小.
- 多语言: 独立 UI, 插件信息, 使用说明, README 与更新日志覆盖 10 种语言.
- 共用后端: 编辑器与轻量插件服务复用同一份已校验资源和原生引擎, 插件连接空闲时自动释放.

******

### 界面截图

******

以下均为未经修饰的 Android 真实运行截图, 依次展示日间模式独立编辑器, 170% 字体下的阿拉伯语 RTL 夜间布局, 以及原有 AutoJs6 插件中心入口.

<table>
  <tr>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/standalone-phone-light.png?raw=true"
           alt="日间主题下的独立离线转换" width="280" />
      <br />
      <sub>日间主题下的独立离线转换</sub>
    </td>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/standalone-rtl-large-dark.png?raw=true"
           alt="夜间主题, 170% 字体下的阿拉伯语 RTL 布局" width="280" />
      <br />
      <sub>夜间主题, 170% 字体下的阿拉伯语 RTL 布局</sub>
    </td>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/plugin-center-enabled.png?raw=true"
           alt="插件中心已识别并启用 OpenCC 1.0.2" width="280" />
      <br />
      <sub>插件中心已识别并启用 OpenCC 1.0.2</sub>
    </td>
  </tr>
</table>

******

### 使用方法

******

1. 从 [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) 页面或 AutoJs6 插件中心下载并安装一个 APK. 选择与设备 ABI 匹配的安装包; 拿不准时选择 `universal`, 或参考下方 `如何选择安装包`.
2. 独立使用时, 从桌面启动 `OpenCC`, 输入或主动粘贴文本, 选择 14 种转换类型之一并点击 `转换`. 此路径不要求安装 AutoJs6, 也不要求用户授予插件权限.
3. 作为插件使用时, 将 AutoJs6 升级到内部版本号 3923 (6.7.1 Alpha4) 及以上; 6.8.0 正式版及更新版本均满足要求.
4. 打开 AutoJs6 插件中心, 确认 `OpenCC` 已被识别并处于启用状态. 官方发布包会自动通过签名校验, 无需手动授权.
5. 在脚本中直接使用 `opencc` 全局对象, 例如 `opencc.s2t("汉字")`; 无需 require, import 或重启宿主.

> 两种模式都支持 Android 7.0 (API 24) 及以上设备. 最低 AutoJs6 版本只约束插件脚本, 独立 App 不依赖宿主. 若脚本提示缺少插件或宿主版本过低, 请参考下方 `常见问题`.

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

#### 不安装 AutoJs6 也可以使用 OpenCC 吗?

可以. 从桌面打开 `OpenCC` 图标即可在完全离线的编辑器中转换文本. 只有脚本通过全局对象 `opencc` 调用插件时才需要 AutoJs6; 两种模式来自同一个 APK.

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

独立 App 与 AutoJs6 插件入口具有相互分离且明确的安全边界:

- 最小权限: 清单只声明用于集成的 `org.autojs.permission.PLUGIN`, 不含网络, 存储, 相机等敏感系统权限; 独立用户无需授予插件权限.
- 显式编辑操作: Launcher 不接收外部分享文本或 URI, 只有点击 `粘贴` 才读取剪贴板, 只有点击 `分享` 才打开系统分享面板.
- 受保护的插件服务: 只有持有插件权限的宿主 (如 AutoJs6) 才能绑定调用, AutoJs6 还会校验安装包签名; 其他应用无法调用服务.
- 本地处理: 两种入口都使用内置词典完全离线转换. 输入和结果不会记录日志, 持久化, 备份, 上传或收集.

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
conversion backend: OpenCC 1.4.2 (ver.1.4.2)
OpenCC source commit: 025f371dc76b598d77384fbdab90c937471844d8
OpenCC resources SHA-256: 9ea0d303219b34d014d5c116677b5d325043beafb2c8a62ee889ca67f4d054a5
```

`OpenccPluginService` 响应 `org.autojs.plugin.OPENCC` action (category `opencc`), Binder 接口为 opencc-api 的 `org.autojs.plugin.opencc.api.IOpenccPlugin`. 契约版本 2 在原有 `getInfo()` 与 `convert(text, conversionType)` 之后追加类型发现, 批量转换与链式转换方法, 并通过 `PluginInfo.capabilities` 广告版本与支持类型; 旧宿主继续使用原有方法和事务编号. 另提供 `WakeActivity` 供宿主唤醒插件进程.

插件直接构建固定在提交 `025f371dc76b598d77384fbdab90c937471844d8` 的官方 OpenCC `ver.1.4.2`, 并使用同一发行版的配套资源. 每个 ABI 仅包含一个静态链接且按 16 KB 对齐的 `libopencc_jni.so`, 转换始终完全离线.

******

### 开发路线图

******

插件的能力规划与完成情况以可勾选清单维护在 ROADMAP.md 中, 按里程碑组织并附验收条件, 涵盖文档与发布体验, 工程化与持续集成, 转换能力增强与运行时演进等方向. 未勾选条目表示规划意向而非当前版本能力, 欢迎通过 Issues 参与讨论.

- [查看 ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md)

******

### 发行历史

******

#### v1.2.0

_2026/09/01_

- `提示` OpenCC 1.4.2 的词典更新会有意改变少量结果, 包括 `复盘` -> `復盤`, `内卷` -> `內捲`, 保留 `什么怎么这么` 及 `内存条` -> `記憶體模組`; 完整审阅清单见迁移报告
- `优化` 将官方 OpenCC 1.4.2 及同版本词典直接构建为每个 ABI 一个静态链接的 JNI 库, 所有转换继续完全离线
- `优化` 使用 NDK 28.2, 16 KB ELF 与 ZIP 对齐及真实 16 KB 模拟器 Binder 验证, 支持 16 KB 页大小设备
- `优化` 以大小和 SHA-256 校验原子安装固定资源 ZIP, 支持损坏自动恢复, Unicode 安全 JNI 转换及热路径转换器缓存
- `依赖` 移除已停止维护的 `com.github.brooklet:android-opencc:1.2.2` 包装库, 并固定官方 OpenCC `ver.1.4.2` 到提交 `025f371dc76b598d77384fbdab90c937471844d8`
- `依赖` 在 `THIRD_PARTY_NOTICES.md` 中记录内置 OpenCC, Marisa Trie, Darts Clone 与 RapidJSON 的来源和许可

#### v1.1.0

_2026/09/01_

- `新增` 升级到 OpenCC 插件契约版本 2, 新增 `getSupportedConversionTypes()`, 供新版宿主动态发现当前实际支持的 14 种转换类型
- `新增` 新增 `convertBatch(texts, conversionType)`, 单次 Binder 往返最多转换 1024 段文本, 同时保留旧宿主逐项调用的兼容路径
- `新增` 新增 `convertChain(text, conversionTypes)`, 单次调用最多顺序执行 32 个阶段, 让新版宿主的组合方法从最多 3 次 Binder 往返降为 1 次
- `优化` 通过 `PluginInfo.instruction` 交付调用方语言的插件说明, 并通过 capabilities 上报契约版本与支持的转换类型
- `优化` 保持原有 AIDL 方法及事务编号不变, 并为扩展调用, 旧契约回退, 大小上限与异常路径补充单元测试和真实 Binder 测试
- `优化` 统一 README 版式与 Gradle 平台版本管理方式

#### v1.0.2

_2026/08/31_

- `提示` 本版本只改进文档与构建流程, OpenCC 转换行为和 14 种核心转换类型保持不变
- `优化` 重构 10 种语言的 README, 新增安装步骤, 选包指南, 快速自检, 33 个脚本方法清单, 常见问题与权限安全说明
- `优化` 将插件中心使用说明纳入同一套多语言 JSON 生成链路, 让 README, CHANGELOG 与 Android 资源由单一来源同步生成
- `优化` 增强文档校验脚本并接入 GitHub Actions, 自动检测跨语言结构不一致, 生成产物漂移, 孤儿文件, 版本不对齐与残留占位符
- `优化` 新增 ROADMAP.md, 以可验收的里程碑清单公开维护文档, 工程化, 转换能力与运行时演进计划
- `优化` 迁移 Gradle 构建配置到 `org.autojs.build.platform-versions` 1.4.1, 并通过 foojay 自动解析 JDK, 简化并统一构建环境

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

构建 release APK:

```powershell
.\gradlew.bat :app:assembleRelease
```

归集发布产物并在文件名中附加版本号, 架构与 CRC32 校验码:

```powershell
.\gradlew.bat :app:appendDigestToReleasedFiles
```

构建 release APK 并准备校验和与发行说明:

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
.readme/android_strings.json
.readme/lang_*.json
.readme/template_readme.md
.readme/template_plugin_instruction.md
.changelog/lang_*.json
.changelog/template_changelog.md
.python/generate_markdown.py
docs/images/screenshots/README.md
docs/images/screenshots/plugin-center-enabled.png
docs/images/screenshots/standalone-phone-light.png
docs/images/screenshots/standalone-rtl-large-dark.png
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

`.readme/android_strings.json` 是独立 UI 与服务错误文案的单一来源, 各语言 JSON 则提供 README 和插件中心文案. 一律修改 `.readme/` 与 `.changelog/` 下的 JSON 源文件, 再运行 `py .python/generate_markdown.py`; 生成的 `strings.xml`, `plugin_instruction.md`, README 和更新日志都不手工编辑. `--check` 会校验全部 47 个生成产物.

******

### 许可

******

项目代码使用 [Mozilla Public License 2.0](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE). 中文转换能力直接来自 [OpenCC](https://github.com/BYVoid/OpenCC) (Apache License 2.0); 内置 OpenCC, Marisa Trie, Darts Clone 与 RapidJSON 的来源和许可见[第三方声明](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/THIRD_PARTY_NOTICES.md).

******

### 相关链接

******

- AutoJs6 OpenCC 文档: https://docs.autojs6.com/#/opencc
- AutoJs6 项目: https://github.com/SuperMonster003/AutoJs6
- OpenCC 官方项目: https://github.com/BYVoid/OpenCC
- 第三方声明: https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/THIRD_PARTY_NOTICES.md
