# M5-A 独立 App 双入口架构决策

记录日期: 2026-09-02
状态: Accepted（M5-A 原型；不是新的正式版本承诺）

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

| APK | v1.2.0 | M5-A 原型 | 增量 |
|---|---:|---:|---:|
| arm64-v8a | 1,499,452 B | 1,528,088 B | +28,636 B |
| armeabi-v7a | 1,160,706 B | 1,189,342 B | +28,636 B |
| x86_64 | 1,508,249 B | 1,536,885 B | +28,636 B |
| x86 | 1,461,662 B | 1,490,298 B | +28,636 B |
| universal | 3,835,001 B | 3,863,637 B | +28,636 B |

五种产物的固定增量来自 Activity 代码、XML、主题、备份排除规则和 10 语言基础文案；ABI 原生
载荷不变。构建期间项目的平台版本插件正在由维护者独立升级，因此这些数字用于记录当前原型
资产，而不作为跨工具链的字节级长期阈值。真正的 M5 发布仍会在固定提交和工具链上重新建立基线。

## 生命周期与线程

- `OpenccConversionCoordinator` 保存 `applicationContext`，实例与 `OpenccNativeEngine` 均按进程
  惰性创建；打开页面本身不会解压/校验资源或建立 Converter。
- 第一次 UI 转换在单线程后台 executor 执行，结果只在主线程写回 View。Activity 销毁时增加
  generation、取消待处理任务并停止 executor，迟到结果不能写回旧页面。
- 服务解绑或 `onDestroy` 不再关闭共享 native engine。缓存由应用进程统一拥有并在进程结束时
  回收，避免一个入口销毁另一个入口仍在使用的 Converter。
- Binder 的单次、批量和链式请求与 UI 请求通过同一个锁串行进入同一 engine；既有 AIDL 事务号、
  限额和错误类型保持不变。

## Manifest、隐私与权限边界

| 组件/能力 | exported | 权限 | 行为 |
|---|---:|---|---|
| `OpenccActivity` | `true` | 无 | 只接受桌面启动；代码不读取外部路径或转换参数 |
| `OpenccPluginService` | `true` | `org.autojs.permission.PLUGIN` | 继续提供既有 OpenCC Binder 契约 |
| `WakeActivity` | `true` | `org.autojs.permission.PLUGIN` | 继续提供既有无界面唤醒协议 |

Manifest 仍没有 `INTERNET`。页面不读取剪贴板、不分享、不写日志，也不建立历史记录；
`allowBackup=false` 并为 Android 11 及 Android 12+ 分别配置全域排除规则，避免未来加入编辑状态
存储时意外进入云备份或设备迁移。官方 OpenCC 资源继续位于 `noBackupFilesDir`，Android 本身也会
排除该目录。备份语义参考 [Android Auto Backup 文档](https://developer.android.com/identity/data/autobackup)。

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
- 10 个现有 locale 已具备 M5-A 基础页面文案；面向用户的 14 类型名称、RTL/大字体/TalkBack/截图
  全矩阵仍属于 M5-B/M5-D，不因本原型提前标记完成。

## 后续边界

M5-B 将在当前 Activity 上增加友好类型名称、清空、复制、显式粘贴、交换、分享、可取消的重复
转换和更完整的状态恢复。M5-C 继续扩充 UI/Binder 并发和生命周期故障矩阵；M5-D 完成十语言
类型名称、可访问性和设备截图；M5-E 才确定并公开第一个双形态版本号。M5-A 原型不会修改
v1.2.0 标签、Release 或在线插件索引。
