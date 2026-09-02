# M5-A/B/C/D 独立 App 双入口、离线 UI、可访问性与安全架构决策

记录日期: 2026-09-03
状态: Accepted（M5-A/B/C/D 原型；不是新的正式版本承诺）

## 结论

同一个 APK 新增普通 `MAIN` / `LAUNCHER` Activity，同时原样保留 AutoJs6 的受权限保护
Binder 服务与无界面唤醒 Activity。独立页面使用 Android 平台 Views/XML，不引入 Compose、
AppCompat、Material Components、网络或分析依赖。两种入口都直接调用进程级、惰性初始化的
`OpenccConversionCoordinator`，协调器再调用唯一的 `OpenccNativeEngine`、官方资源安装器和
`libopencc_jni.so`：

```text
系统桌面 ──> OpenccActivity ───────┐
                                   ├──> OpenccConversionCoordinator
AutoJs6 ──> OpenccPluginService ───┘          │
                                              └──> OpenccNativeEngine
                                                     │
                                                     ├──> 官方资源 ZIP/校验器
                                                     └──> libopencc_jni.so
```

UI 不通过 Binder 回环调用自身服务，因此独立模式不要求安装或运行 AutoJs6，也不会复制 JNI、
资源 ZIP、Converter 缓存、类型解析、批量/链式限额或错误模型。

## Views 与 Compose 选型

| 维度 | 平台 Views/XML（采用） | Compose（本阶段不采用） |
|---|---|---|
| minSdk 24 | 直接使用系统 `Activity`、Views 和 Material 系统主题 | 可以支持，但需要 Compose compiler/runtime 与配套配置 |
| 运行时依赖 | 新增 0 个；现有 runtime classpath 不变 | 需要引入一组新的 UI runtime artifacts |
| APK 增量 | 五个 minified APK 均为 `28,636 B` | 官方迁移示例显示混合 Views/Compose 的增量可能达到数百 KiB，实际值仍取决于项目 |
| 冷启动 | `onCreate` 只创建平台控件、14 项代码列表和静态版本文本；不加载资源 ZIP 或 Converter | 首次组合还需初始化 Compose runtime |
| RTL/可访问性 | `start`/`end` 布局、平台标签/提示、48 dp 操作目标、可选择结果文本和 live region | 能实现同等能力，但本项目没有可复用的 Compose 设计系统 |
| 工具链风险 | 沿用既有 Android/Kotlin/R8 配置 | 增加 compiler plugin 与版本兼容面 |

Android 官方说明两套 UI 工具都可使用；官方的迁移度量示例也明确提示 APK 结果与项目相关。
因此这里不把示例数字当成本项目预测，而以本仓库的 release 实测和“零新增依赖”为决策依据。
如果未来已有 Compose 设计系统、复杂状态界面或跨页面复用收益超过固定成本，可单独 ADR 重新评估，
无需改变共享协调器或 Binder 契约。

参考：

- [Android UI 开发总览](https://developer.android.com/develop/ui)
- [Compose 与 Views 的迁移度量](https://developer.android.com/develop/ui/compose/migrate/compare-metrics)
- [应用启动与惰性初始化](https://developer.android.com/topic/performance/vitals/launch-time)
- [Android 线程模型](https://developer.android.com/topic/performance/threads)

## APK 实测

基线是 GitHub 已公开的 v1.2.0 签名资产；原型是 2026-09-02 至 2026-09-03 在相同版本号下仅用于本地验收的
minified release 构建，未发布且不会覆盖 v1.2.0：

| APK | v1.2.0 | M5-A 原型 | M5-B 原型 | M5-C 原型 | M5 总增量 |
|---|---:|---:|---:|---:|---:|
| arm64-v8a | 1,499,452 B | 1,528,088 B | 1,542,276 B | 1,542,312 B | +42,860 B |
| armeabi-v7a | 1,160,706 B | 1,189,342 B | 1,203,530 B | 1,203,566 B | +42,860 B |
| x86_64 | 1,508,249 B | 1,536,885 B | 1,551,073 B | 1,551,109 B | +42,860 B |
| x86 | 1,461,662 B | 1,490,298 B | 1,504,486 B | 1,504,522 B | +42,860 B |
| universal | 3,835,001 B | 3,863,637 B | 3,877,825 B | 3,877,861 B | +42,860 B |

M5-A 的五种产物固定增加 `28,636 B`；M5-B 再固定增加 `14,188 B`，来自 Activity 操作/状态逻辑、
扩展 XML 和 10 语言类型/操作文案；M5-C 仅因显式禁止明文流量的最终 Manifest 属性再增加 `36 B`，
测试与静态门禁代码均不进入正式 APK，ABI 原生载荷不变。构建期间项目的平台版本插件正在由维护者
独立升级，因此这些数字用于记录当前原型资产，而不作为跨工具链的字节级长期阈值。真正的 M5
发布仍会在固定提交和工具链上重新建立基线。

## 生命周期与线程

- `OpenccConversionCoordinator` 保存 `applicationContext`，实例与 `OpenccNativeEngine` 均按进程
  惰性创建；打开页面本身不会解压/校验资源或建立 Converter。
- 第一次 UI 转换在单线程后台 executor 执行，结果只在主线程写回 View；活动请求存在时转换按钮
  被禁用，业务入口也拒绝重复请求。用户按取消、编辑来源、切换类型或销毁 Activity 时会中断 Future、
  增加 generation 并停止进度状态；已经进入 OpenCC 的原生调用可能完成，但迟到结果因 generation
  不匹配而绝不能写回页面，下一次请求仍按共享锁顺序执行。
- 服务解绑或 `onDestroy` 不再关闭共享 native engine。缓存由应用进程统一拥有并在进程结束时
  回收，避免一个入口销毁另一个入口仍在使用的 Converter。
- Binder 的单次、批量和链式请求与 UI 请求通过同一个锁串行进入同一 engine；既有 AIDL 事务号、
  限额和错误类型保持不变。
- `onSaveInstanceState` 通过最小 `OpenccEditorState` 只保存来源文本、结果文本和稳定类型下标；旋转、
  分屏重建及系统带状态重建可以恢复必要编辑状态，不恢复或自动重放进行中的转换，也不写入
  SharedPreferences、数据库或文件。设备测试将真实 Activity 产生的最小 Bundle 序列化后在不同 PID
  解码，配合同一 Activity 的 `recreate()` 往返覆盖保存端、跨进程载荷和恢复端。

## Manifest、隐私与权限边界

| 组件/能力 | exported | 权限 | 行为 |
|---|---:|---|---|
| `OpenccActivity` | `true` | 无 | 只声明 `MAIN`/`LAUNCHER`；代码忽略外部 URI、ClipData、文本和转换参数 |
| `OpenccPluginService` | `true` | `org.autojs.permission.PLUGIN` | 继续提供既有 OpenCC Binder 契约 |
| `WakeActivity` | `true` | `org.autojs.permission.PLUGIN` | 继续提供既有无界面唤醒协议 |

Manifest 仍没有 `INTERNET`，并显式设置 `usesCleartextTraffic=false`。页面只在用户点击“粘贴”后读取剪贴板第一项的显式文本，不调用可能
解析 URI 的 coercion；只在点击“复制”后写入结果，只在点击“分享”后发出 `ACTION_SEND` 的
`text/plain` 系统 chooser。启动、恢复、后台阶段和按钮可用性计算都不读取剪贴板，Manifest 也不
接收外部分享。页面不写输入/输出日志，不建立历史记录；`allowBackup=false` 并为 Android 11 及
Android 12+ 分别配置全域排除规则，避免未来加入编辑状态存储时意外进入云备份或设备迁移。官方
OpenCC 资源继续位于 `noBackupFilesDir`，Android 本身也会排除该目录。备份语义参考
[Android Auto Backup 文档](https://developer.android.com/identity/data/autobackup)。

## M5-A 验收证据

- `OpenccDualEntryTest` 从真实 Launcher Activity 选择 `S2T` 并转换包含 emoji/U+20000 的固定文本，
  随后在 Activity 仍存活时绑定插件服务，核对相同输出和 OpenCC version/commit/resource SHA-256。
- 同一测试通过 PackageManager 核对恰好一个桌面入口、Launcher 无插件权限、服务与 Wake Activity
  仍受插件权限保护，并核对 APK 未取得 `INTERNET`。
- Android 16 / API 36 / x86_64 / `PAGE_SIZE=16384` 已通过新双入口测试，以及既有服务、14 类型、
  资源损坏恢复和不同 PID 重启复用测试。
- Android 15 / API 35 / arm64-v8a 和 Android 9 / API 28 / 32-bit armeabi-v7a 真机也已通过新
  双入口测试；测试前设备均未安装目标包，测试后目标与 instrumentation 包已清理。
- debug/release 各五 APK 内容门禁强制保留 `OpenccActivity` 和 JNI bridge；release 五 APK 均通过
  R8、签名、唯一 native 库、官方资源 SHA-256、ELF `LOAD >= 0x4000`、RELRO 与
  `zipalign -P 16`。
- 10 个现有 locale 已具备 M5-A 基础页面文案；RTL/大字体/TalkBack/截图全矩阵仍属于 M5-D，
  不因本原型提前标记完成。

## M5-B 验收证据

- 类型选择器用本地化的简体、通用繁体、香港繁体、台湾繁体、繁体旧字形、日文新字体及地区术语
  名称描述全部 14 个转换，同时保留 `HK2S` 至 `TW2SP` 稳定代码；`S2TW`/`S2TWP`、
  `TW2S`/`TW2SP` 与 JP 字形路径均为不同且唯一的标签。
- `OpenccStandaloneUiTest` 从真实 Launcher 页面逐项执行 14 种转换，并覆盖空输入、约 30K 字符的
  长文本、emoji、U+20000 非 BMP 和阿拉伯文 RTL 混排；转换始终在后台 executor 执行。
- 同一测试验证活动请求期间转换按钮禁用、显式取消、取消后的迟到结果隔离；验证设置剪贴板不会
  自动改变来源，只有粘贴按钮读取，复制按钮写入转换结果，交换不改变类型。
- 分享测试用阻断式 `ActivityMonitor` 捕获用户点击，确认只发出 `ACTION_CHOOSER` 包装的
  `ACTION_SEND`、MIME 为 `text/plain` 且负载精确等于结果，测试期间不会真的打开外部应用。
- Activity `recreate()` 后来源、结果、emoji/U+20000/RTL 混排与 `TW2SP` 类型均恢复；临时状态、
  进行中任务和剪贴板不会自动恢复或读取。测试会在结束前恢复设备原剪贴板。
- Android 16 / API 36 / x86_64 / `PAGE_SIZE=16384` 模拟器与 Android 9 / API 28 / 32-bit
  armeabi-v7a 真机均通过 Service、双入口、完整 UI 和两阶段进程重启共五次 instrumentation；
  目标包与测试包在每轮结束后自动清理。
- debug/release 各五 APK 已通过资源、旧后端排除、R8/JNI、ELF 16 KB/RELRO、ZIP 16 KB 对齐和
  签名门禁；JVM 测试及 10 语言/36 份 Markdown 漂移检查通过。

## M5-C 验收证据

- `OpenccDualEntryLifecycleTest` 在一个 Activity 存活期间启动长文本 UI 转换，同时以 10 个工作线程
  发送 64 个 Binder 请求，并穿插 16 个独立 `OpenccNativeEngine` 的转换/`close()`；`close()` 会清空
  JNI 全局 Converter 缓存，因此该竞争实际覆盖共享协调器锁与 JNI mutex 的交界。全部请求按各自显式
  类型返回正确值，缓存清理后的 UI/Binder 后续调用也会透明重建 Converter。
- 同一测试把编辑器任务移到后台，在此期间继续完成 Binder 转换，再由 shell 模拟用户从系统任务切回；
  原 Activity、来源、结果和类型保持不变且没有创建第二个页面。最后一个 Binder 客户端解绑后，测试以
  ActivityManager 等待 bound-only Service 的 `ServiceRecord` 消失，再验证仍存活的 UI 和随后新开的 UI
  都可转换，并重新绑定服务交替执行 S2T/T2S。
- 恶意显式启动测试携带 `content://` URI、`EXTRA_TEXT` 与 `ClipData`，编辑器仍为空。PackageManager
  运行时审计精确要求两个 Activity、一个 Service、零 receiver/provider、唯一插件权限、单一普通任务
  Launcher、受 `org.autojs.permission.PLUGIN` 保护的 Wake/Service，并证明本包不会响应隐式
  `ACTION_SEND text/plain` 或外部 `ACTION_VIEW` URI。
- `verify_apk_variants.py` 新增无第三方依赖的 Android Binary XML 解析器，对 debug/release 各五个最终
  APK 验证相同组件全集、exported/permission 归属、每个 intent-filter、无 `<data>`、无自定义进程/任务
  属性、`allowBackup=false`、`usesCleartextTraffic=false` 与唯一 requested permission。负向 Python
  测试固定拒绝 `INTERNET`、额外 receiver 和分享接收 filter。
- `PluginApiCompatibilityTest` 固定 `IOpenccPlugin` 五个方法签名、v1/v2/current 契约常量、插件
  ID/engine/`default` 变体及事务 1–5；APK 门禁另固定当前 `opencc-api.aar` SHA-256。真实 Binder 测试
  一方面直接向事务 1/2 写 Parcel，证明旧宿主 `getInfo()`/`convert()` 编号和负载仍兼容；另一方面
  强制生成的 AIDL client 走 Proxy/Parcel 而不是同进程 local interface，使 v2 类型枚举、批量、链式、
  能力元数据和并发请求都覆盖真实序列化路径。独立 UI 不修改任何宿主代码或 33 个脚本方法计划，
  也不保存会影响 Binder 默认值的偏好。
- `OpenccEntryResourceTest` 由脚本分两次 instrumentation/两个新进程运行。独立阶段先删除版本资源，
  证明仅打开页面不会安装，再制造与官方 ZIP 同长度的损坏副本并由首个 UI 转换恢复；Binder 阶段再次
  从缺失状态开始，证明绑定、`getInfo()` 和类型枚举均保持惰性，首个转换才从 APK asset 安装。两阶段
  均校验最终 SHA-256、asset 长度和目录中只存在一个正式 ZIP、没有临时文件。
- `OpenccResourceRestartTest` 除原有 PID/资源长度/摘要/mtime 证据外，现将真实 Activity 保存出的最小
  editor Bundle 跨 instrumentation 进程序列化并复核；验证阶段 PID 不同，资源不重写，编辑状态的
  Unicode/emoji/U+20000/RTL 与类型下标也完整一致。
- 八阶段设备脚本已在 Android 15/API 35 arm64 真机、Android 9/API 28 的 32-bit armv7 真机和
  Android 16/API 36 x86_64/`PAGE_SIZE=16384` 模拟器通过；每轮均执行两个资源首启阶段、服务全契约、
  双入口/manifest、并发生命周期、完整 UI 和两阶段真实进程重建，并在结束时卸载目标/测试包。

## M5-D 单一来源与本地化

- `.readme/android_strings.json` 是独立 UI 文案的唯一人工维护源；它与 10 份 README 语言 JSON、
  README 模板和插件说明模板一起由 `.python/generate_markdown.py` 校验并生成。受控清单现为 47 份：
  10 份本地化 README、根 README、14 份 CHANGELOG、11 份 Android `plugin_instruction.md` 和
  11 份 `strings.xml`。生成器的 `--check` 会拒绝缺失/孤立产物、locale/key 集不一致、格式参数漂移和模板
  未替换占位符。
- `res/xml/locales_config.xml` 精确声明 `ar`、`en`、`es`、`fr`、`ja`、`ko`、`ru`、`zh-Hans`、
  `zh-Hant-HK` 和 `zh-Hant-TW`，Manifest 通过 `android:localeConfig` 公开相同集合；Python 测试同时核对 JSON、
  Android 资源目录和 locale config，最终 APK 门禁再要求二进制 Manifest 中存在非零 localeConfig
  资源引用。
- 每种语言的简介、使用步骤、FAQ、安全边界和插件说明都明确：这是同一个 APK，既可不安装 AutoJs6
  而从桌面独立启动，也可由 AutoJs6 按原插件协议调用。独立路径不需要授予插件权限；宿主版本与启用
  插件步骤只属于插件路径。JP 配置始终描述为汉字字形转换，不宣称中文与日文互译。

## M5-D 可访问性与响应式布局

- 标题标记为 accessibility heading；来源、类型、结果均有显式标签，并通过 `labelFor` 关联对应控件；
  状态使用 polite live region，进度条有动态 content description。XML 和仪器测试固定来源 → 粘贴 → 清空 →
  类型 → 转换 → 结果 → 复制 → 交换 → 分享 → 来源的循环焦点链；取消按钮出现时回到转换按钮。所有操作
  目标最小尺寸为 48 dp。
- 来源和结果区域都支持长内容的独立滚动与文本选择。类型选择器使用可换行的自定义 spinner item/dropdown，
  避免 14 个地区/字形名称在窄屏或大字体下被单行截断；硬件键盘 `Ctrl+Enter` 转换、`Escape` 取消。
- 布局使用 start/end 语义并同时验证日间与夜间前景/背景对比关系。合成配置覆盖阿拉伯语 RTL、170% 字号、
  夜间 320 x 480 手机；2 倍字体 360 x 360 分屏；1.3 倍字体 960 x 600、`sw600dp` 平板。真实 Activity
  从设备当前方向旋转到相反方向并恢复原方向，验证转换类型及含 emoji/非 BMP/RTL 的来源和结果不丢失；
  因而测试不依赖设备初始为手机竖屏。

## M5-D 截图与设备矩阵

两张新增截图均由 `OpenccDocumentationScreenshotTest` 在 Android 16/API 36/x86_64/16 KB 页模拟器上
以确定性示例生成，经 `UiAutomation` 原样保存，没有裁剪、调色或个人数据；README 三栏同时保留既有
插件中心截图：

| 文件 | 场景 | PNG | SHA-256 |
|---|---|---|---|
| `standalone-phone-light.png` | 英语、日间、独立 App 完整操作流 | 1080 x 1920、8-bit RGB | `BC9A577A0CF9892BAE81B66CD2DD137C578BF6C8C71156C4503978CF5662ED4C` |
| `standalone-rtl-large-dark.png` | 阿拉伯语 RTL、170% 字号、夜间与可滚动布局 | 1080 x 1920、8-bit RGB | `BCCBF805931990C056AB1E78E628F63F0DAE733081827AE899E1BC31D4900F6F` |

生成器固定三张文档 PNG 的完整资产清单、尺寸、位深、颜色类型、SHA-256 和模板唯一引用；采集命令与
环境恢复说明见 `docs/images/screenshots/README.md`。

最终设备脚本逐环境安装单 ABI debug APK 和 instrumentation APK，执行资源首次安装、可访问性、服务
全契约、双入口、并发/生命周期、独立 UI 与两阶段进程重启，并在退出时恢复 locale/字号/夜间模式和
卸载两个包：

| Android / API | 环境 | ABI | 页大小 | M5-D 重点 |
|---|---|---|---:|---|
| Android 7.0 / API 24 | 模拟器 | x86 | 4 KB | minSdk、旧 Clipboard/ActivityMonitor 路径与完整 UI |
| Android 9 / API 28 | 真机 | armeabi-v7a | 4 KB | 32-bit ARM、旧 Android 与完整矩阵 |
| Android 15 / API 35 | 真机 | arm64-v8a | 4 KB | 平板初始横屏、自适应旋转；阿拉伯语/170%/夜间增强重放 |
| Android 16 / API 36 | 模拟器 | x86_64 | 16 KB | 当前高 API、真实 16 KB 运行时；阿拉伯语/170%/夜间增强重放 |

清洁工作树构建通过 JVM 测试、debug/androidTest/release 五变体和 R8 共 199 个 Gradle 任务；debug 与
unsigned release 各五个最终 APK 均通过组件/权限、localeConfig、资源、旧后端排除、R8/JNI、ELF
`LOAD >= 0x4000`、RELRO 与原生条目检查。GitHub Actions 另新增 API 24/x86/minSdk 完整设备门禁，
并保留 arm64/x86_64 4 KB 与 x86_64 16 KB 作业。

## 后续边界

M5-A/B/C/D 验收完成后，第一个双形态候选按向后兼容功能版本确定为 `v1.3.0` / build 20。版本号进入
候选源码不等于公开发布：M5-E 仍须从固定提交重建并签名五种 ABI，使用仅依赖 Android 平台的 Java release 探针验证
v1.2.0 原地升级后 UID/首次安装时间不变、唯一 Launcher、真实 UI 转换和原始 Binder 事务，再核对
插件中心识别、发布说明、tag、GitHub 资产与在线索引回读一致。在这些门禁完成前，v1.2.0 仍是公开
Latest，候选不得覆盖其标签、Release 或索引。
