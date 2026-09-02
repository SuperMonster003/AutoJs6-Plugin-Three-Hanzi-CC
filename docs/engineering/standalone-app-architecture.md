# M5-A/B 独立 App 双入口与离线 UI 架构决策

记录日期: 2026-09-03
状态: Accepted（M5-A/B 原型；不是新的正式版本承诺）

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

基线是 GitHub 已公开的 v1.2.0 签名资产；原型是 2026-09-02 在相同版本号下仅用于本地验收的
minified release 构建，未发布且不会覆盖 v1.2.0：

| APK | v1.2.0 | M5-A 原型 | M5-B 原型 | M5 总增量 |
|---|---:|---:|---:|---:|
| arm64-v8a | 1,499,452 B | 1,528,088 B | 1,542,276 B | +42,824 B |
| armeabi-v7a | 1,160,706 B | 1,189,342 B | 1,203,530 B | +42,824 B |
| x86_64 | 1,508,249 B | 1,536,885 B | 1,551,073 B | +42,824 B |
| x86 | 1,461,662 B | 1,490,298 B | 1,504,486 B | +42,824 B |
| universal | 3,835,001 B | 3,863,637 B | 3,877,825 B | +42,824 B |

M5-A 的五种产物固定增加 `28,636 B`；M5-B 再固定增加 `14,188 B`，来自 Activity 操作/状态逻辑、
扩展 XML 和 10 语言类型/操作文案，ABI 原生载荷不变。构建期间项目的平台版本插件正在由维护者
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
- `onSaveInstanceState` 只保存来源文本、结果文本和稳定类型下标；旋转、分屏重建及系统带状态重建
  可以恢复必要编辑状态，不恢复或自动重放进行中的转换，也不写入 SharedPreferences、数据库或文件。

## Manifest、隐私与权限边界

| 组件/能力 | exported | 权限 | 行为 |
|---|---:|---|---|
| `OpenccActivity` | `true` | 无 | 只接受桌面启动；代码不读取外部路径或转换参数 |
| `OpenccPluginService` | `true` | `org.autojs.permission.PLUGIN` | 继续提供既有 OpenCC Binder 契约 |
| `WakeActivity` | `true` | `org.autojs.permission.PLUGIN` | 继续提供既有无界面唤醒协议 |

Manifest 仍没有 `INTERNET`。页面只在用户点击“粘贴”后读取剪贴板第一项的显式文本，不调用可能
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

## 后续边界

M5-C 继续扩充 UI/Binder 并发和生命周期故障矩阵；M5-D 完成十语言单一来源、可访问性和设备
截图；M5-E 才确定并公开第一个双形态版本号。M5-A/B 原型不会修改 v1.2.0 标签、Release 或
在线插件索引。
