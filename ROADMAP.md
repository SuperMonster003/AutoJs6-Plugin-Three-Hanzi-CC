# AutoJs6 OpenCC 插件 Roadmap

更新日期: 2026-09-03

本文档是 OpenCC 插件从"单一转换服务"逐步演进为"文档完善, 工程可靠, 能力可扩展"的中文转换方案的执行清单. 每个条目只有在代码/文档与可验证的验收条件同时满足后才可勾选.

## 状态与证据规则

- `[x]`: 已完成, 且本仓库存在可复核证据 (代码, 测试, 脚本或生成产物).
- `[ ]`: 尚未完成; 括号中的 `插件` / `API` / `宿主` / `测试` / `发布` / `依赖` 表示主要落点.
- 未勾选条目属于规划意向, 不代表当前版本能力; 标注 "宿主先行" 或 "契约升级" 的条目需等待 AutoJs6 宿主或 opencc-api 契约仓库先行支持.

## 总览

| 里程碑 | 状态 | 核心结果 | 主要落点 |
|---|---|---|---|
| M0 基线插件 | 已完成 | OpenCC 转换服务与多语言资源 | 插件/发布 |
| M1 文档与发布体验 | 已完成 | 用户导向文档, 文档 CI 与首个整改版本 | 发布 |
| M2 工程化与持续集成 | 已完成 | 构建/测试流水线与发布物料脚本化 | 测试/发布 |
| M3 转换能力增强 | 开发完成, 待宿主发布 | 类型枚举, 批量与链式转换, 本地化说明, 自定义词典评估 | API/插件/宿主 |
| M4 运行时与生态演进 | 已启动 | 官方 OpenCC 原生后端, 上游自动跟进, 16 KB 适配与词典生态 | 依赖/插件/测试/宿主/发布 |
| M5 插件与独立 App 双形态 | M5-A 至 M5-D 已完成 | 共用官方后端的桌面文本转换 UI、原插件入口与十语言无障碍体验 | App/插件/测试/发布 |

依赖顺序:

```text
M0 ──> M1 ──> M2 ──> M3 (契约条目需宿主先行)
        └──────────> M4 (依赖/宿主演进项可与 M2/M3 并行)
```

## M0: 基线插件 (v1.0.0 / v1.0.1, 已完成)

- [x] (插件) OpenCC 插件服务与 AIDL 契约: `OpenccPluginService` 响应 `org.autojs.plugin.OPENCC` (category `opencc`), Binder 接口为 opencc-api 的 `IOpenccPlugin`, 提供 `getInfo()` 与 `convert(text, conversionType)` 两个方法 (`app/src/main/java/.../opencc/OpenccPluginService.kt`); 另提供 `WakeActivity` 供宿主唤醒插件进程.
- [x] (插件) 14 种 OpenCC 标准转换类型直通 `com.github.brooklet:android-opencc:1.2.2` 转换引擎; 未知类型抛出带本地化文案的 `IllegalArgumentException` (`error_unsupported_conversion_type`).
- [x] (插件) `PluginInfo` 完整上报: id/engine/variant, 版本名与版本号, 作者, 最低宿主版本 (versionCode 3923, 即 AutoJs6 6.7.1 Alpha4) 与 `supportedAbis` 四种架构 (`app/src/main/java/.../opencc/PluginRuntimeInfo.kt`).
- [x] (发布) 按 ABI 拆分的 5 种安装包 (`arm64-v8a` / `armeabi-v7a` / `x86_64` / `x86` / `universal`), 发布文件名附带版本号, 架构与 CRC32 摘要 (`:app:appendDigestToReleasedFiles`).
- [x] (发布) 多语言资源: `strings.xml` 与 `plugin_instruction.md` 覆盖 10 种语言.

验收条件: 在 versionCode 不低于 3923 的 AutoJs6 中安装并启用后, 脚本可直接调用 `opencc` 全局对象的全部方法. (已满足)

## M1: 文档与发布体验 (已完成)

- [x] (发布) README 重构为用户导向结构 (2026-08-31): 简介 / 功能亮点 / 使用方法 / 快速上手 / 转换类型 / 脚本方法 / 如何选择安装包 / 快速自检 / 常见问题 / 权限与安全 / 插件接口 / 开发路线图 / 构建与校验, 10 种语言全部由 JSON 源再生成.
- [x] (发布) CHANGELOG 文案面向用户重写: 每条先讲可感知的结果, 再补技术细节, 10 种语言同步.
- [x] (发布) 文档生成脚本升级至同族插件最新实现 (`.python/generate_markdown.py`): 新增 `--check` 漂移检测, 跨语言键位与列表形状对齐校验, 产物清点与孤儿文件检测, 全角符号与机翻占位符拦截, 以及 `version.properties` 与最新 CHANGELOG 条目的版本对齐校验.
- [x] (发布) `plugin_instruction.md` 纳入生成链路: `.readme/template_plugin_instruction.md` 与同一组 10 语言 JSON 生成全部 11 份 Android 资源产物, 消除双源维护.
- [x] (发布) 新增 `.python/check_markdown.bat` 与 GitHub Actions 工作流 `.github/workflows/markdown.yml`, push/PR 自动校验文档源与生成产物同步.
- [x] (发布) 新建本 ROADMAP.md, 并在 README 增加 "开发路线图" 章节挂链.
- [x] (发布) 构建系统迁移与文档整改一并入库: 使用 `org.autojs.build.platform-versions` 统一解析 Gradle 插件版本, 并通过 foojay 自动解析 JDK; `:app:assembleDebug` 已在 JDK 21 / Gradle 9.5 / AGP 9.2.1 组合下验证通过.
- [x] (发布) 文档整改后的首个对外版本 v1.0.2 (2026-08-31): `version.properties` 与 10 语言 CHANGELOG 已更新, 5 个签名 APK 已完成版本/ABI/CRC32/SHA-256/签名连续性核验, `v1.0.2` 标签与 GitHub Release 已公开发布.
- [x] (发布) 提供插件在 AutoJs6 插件中心内被识别与启用状态的界面截图 (`docs/images/screenshots/plugin-center-enabled.png`), 接入 README 多语言生成链路; 原始 720 x 1280 PNG 未经裁剪或调色, 采集说明与 SHA-256 已记录, 文档生成器同时校验 PNG 格式, 尺寸, 哈希及模板唯一引用.

验收条件: `py .python/generate_markdown.py --check` 在本地与 CI 全绿; 新用户仅凭 README 即可独立完成安装, 选包与生效确认. (已满足)

## M2: 工程化与持续集成 (已完成)

- [x] (测试) 单元测试基础设施与首批 JVM 用例 (2026-08-31): `ConversionTypeContractTest` 双向核对 opencc-api 的 14 个常量与 `android-opencc` 的 `ConversionType` 枚举; `PluginRuntimeInfoTest` 断言版本, 作者, id/engine/variant, `REQUIRES_HOST_VERSION` 与四种 `supportedAbis` 的字段拼装.
- [x] (测试) instrumentation 用例: `OpenccPluginServiceTest` 通过 `org.autojs.plugin.OPENCC` 发现并绑定真实 Binder 服务, 断言 `getInfo()` 运行时字段, 对 14 种类型逐一执行 `convert`, 校验 S2T/T2S 结果并覆盖未知类型报错; 本地已在 API 35 arm64-v8a 真机和 API 36 x86_64 模拟器通过, CI 使用 API 35 Google APIs 模拟器分别安装并运行 arm64-v8a 与 x86_64 单架构 APK.
- [x] (测试) GitHub Actions 构建流水线 `.github/workflows/build.yml`: push/PR/手动运行 `:app:testDebugUnitTest`, `:app:assembleDebug` 与 `:app:assembleDebugAndroidTest`; `scripts/ci/verify_apk_variants.py` 校验 5 个 APK 清单及其内部原生 ABI 集合, 上传构建产物后由 `scripts/ci/verify_binder_round_trip.sh` 执行双 ABI Binder 往返矩阵.
- [x] (CI) 清洁环境可复现性修复: 将仅能从开发机 Maven Local 解析的 `org.autojs.build.platform-versions` 1.4.1 替换为 Maven Central 可解析的 `io.github.supermonster003.autojs6-platform-versions` 1.6.0; 使用全新 `GRADLE_USER_HOME` 与空 Maven Local 冷启动验证 Gradle 9.5 / Kotlin 2.3.20 / AGP 9.2.1 组合, 77 个 Gradle 任务及 5 个 APK 变体全部通过.
- [x] (发布) Release 产物脚本化: `scripts/release/prepare_release.py` 一键构建并归集 5 个已签名 APK, 校验版本集合, CRC32, APK/ABI 内容, 签名与签名证书连续性, 原子生成 `SHA256SUMS.txt` 及基于英文 CHANGELOG 的 `RELEASE_NOTES.md`; 7 个标准库测试覆盖完整流程, 缺包, 重复/混包, 错误 ABI, CRC 不一致与跨版本隔离.

验收条件: 主分支每次提交自动完成构建, 单元测试与 APK 变体校验; 发布产物由脚本生成且哈希可追溯. (已满足)

## M3: 转换能力增强 (v1.1.0, 开发完成, 待宿主发布)

- [x] (API/宿主) 转换类型枚举接口 (2026-08-31): opencc-api 在原有两个 AIDL 方法之后追加 `getSupportedConversionTypes()`, 以稳定有序的 `OpenccConversionTypes.ALL` 作为 14 种核心类型的单一契约; 插件同时通过 `PluginInfo.capabilities` 上报契约版本 2 与支持类型. 宿主提供统一读取入口, 对版本 2 插件读取动态结果, 对旧插件或未声明版本 2 的实现回退到契约内置列表.
- [x] (API/插件) 批量转换接口: 新增 `convertBatch(texts, conversionType)`, 每次 Binder 往返按输入顺序转换最多 1024 段文本; 插件在开始处理前统一校验类型和数量, 新宿主使用扩展调用, 旧插件则由宿主透明回退为逐项 `convert`.
- [x] (API/插件/宿主) 链式转换下沉: 新增 `convertChain(text, conversionTypes)`, 单次调用最多顺序执行 32 个核心转换阶段; 宿主的 16 个真正组合方法统一改用显式转换计划, 契约版本 2 插件只需 1 次 Binder 往返, 旧插件仍按原顺序逐阶段执行. `s2twi` 与 `twi2s` 两个直达别名继续使用单次核心转换.
- [x] (插件/宿主) `getInfo()` 填充 `instruction = "@raw/plugin_instruction"`, 由宿主资源解析器按调用方语言读取已有 10 语言 Markdown 说明; 解析器同时支持本地或带包名的 `@string/...` 与 `@raw/...` 引用.
- [x] (插件/依赖) 自定义词典可行性评估: 本地检查 `android-opencc:1.2.2` AAR 后确认其公开 API 仅接受固定 `ConversionType`, 词典与配置从内置 assets 整体复制; 虽然内部私有 JNI 入口接收配置名和数据目录, 但依赖反射与私有符号不具备可维护性. [android-opencc 使用说明](https://github.com/brooklet/android-opencc/blob/master/README.md) 展示的同样是固定枚举接口, 而[官方 OpenCC 转换器接口](https://github.com/BYVoid/OpenCC/blob/master/src/README.md)支持配置文件与搜索路径. 结论: M3 不引入不稳定的自定义词典入口; 后续必须先分叉并重建 Android 封装, 或迁移到公开配置/资源路径的官方 OpenCC JNI 封装, 再在 M4 独立立项.

开发验收已满足: AIDL 原有 `getInfo()` 与 `convert()` 的声明顺序及事务编号保持不变, 插件最低宿主版本仍为 3923; opencc-api 契约测试, 宿主扩展/旧契约双路由测试, 16 个组合计划测试, 资源引用解析测试与插件真实 Binder 测试均已覆盖. 插件测试矩阵已在 4 台真机和 3 个模拟器上通过, 覆盖 arm32/arm64/x86/x86_64 与 Android API 9/10/12/13/15/16. 用户侧的一次往返优化需等待对应 AutoJs6 宿主改动合入并发布, 旧宿主继续使用 v1 接口且转换行为不变.

## M4: 运行时与生态演进 (已启动)

M4 的主线是让插件摆脱停止跟进上游的 `com.github.brooklet:android-opencc:1.2.2` 封装, 由插件直接固定并构建 [BYVoid/OpenCC](https://github.com/BYVoid/OpenCC) 官方源码. 上游同步发生在仓库和 CI 的构建阶段, 已安装插件仍然完全离线转换, 不新增网络权限或设备端动态下载行为.

实施原则:

- 只跟踪 OpenCC 的正式 `ver.*` Release 标签, 不以移动中的 `master` 作为发布输入.
- OpenCC 源码提交, 官方资源 ZIP, 资源清单提交及 SHA-256 必须属于同一个 Release; 任一项不一致即拒绝构建或升级.
- 上游新版本采用逐级放权：M4-D-2 自动生成升级 PR，M4-D-3 在可信控制器核对完整机器门禁后自动合并，M4-D-4 再独立完成签名、Release 与插件索引发布；任一层均保留可立即切回 `pr-only` / `paused` 的熔断能力，不把机器人自批当作安全门禁.
- 第一阶段保持现有 14 种转换类型, AIDL 事务编号, 契约版本 2 和 `default` 变体兼容; 新配置和自定义词典另行升级 API/宿主契约.
- 原生库按四种 ABI 从源码重建并静态链接 C++ 运行时, 最终 APK 不携带外部 `libopencc.so` 或 `libc++_shared.so` 依赖.
- 旧引擎只在迁移期作为差分测试基线保留; 正式提升官方后端为 `default` 后删除旧 AAR, 不长期发布两套重复引擎.

### 推荐实施顺序与升阶门

```text
M4-A 官方后端原型 ──> M4-B 兼容/性能/16 KB ──> M4-C 正式替换与 v1.2.0
          │                                      │
          └─> M4-D-1 只读监视 ──> M4-D-2 自动 PR ──> M4-D-3 自动合并 ──> M4-D-4 自动发版
                                      ├─> M4-E 可选能力
                                      │
                                      └─> M5 双形态 App/UI
```

| 顺序 | 阶段 | 进入条件 | 必须产出 | 升阶条件 |
|---|---|---|---|---|
| 1 | M4-A | M2 构建/测试基线稳定 | 固定官方源码与资源, 自有 JNI/JVM 门面, Binder 无缝切换 | 四 ABI 可构建, 14 类型通过, 正式 APK 不含旧后端 |
| 2 | M4-B | M4-A 可在设备运行 | 新旧差分审阅, 异常/并发测试, 性能与体积报告, 16 KB 三层验收 | 行为差异可解释, 现有矩阵无回归, ELF/ZIP/真实 16 KB 设备全绿 |
| 3 | M4-C | M4-B 全部验收 | 删除迁移基线, 许可证与 10 语言文档, v1.2.0 产物/Release/索引 | 源码标签, 5 APK, 摘要, 签名, Release 与索引一致 |
| 4 | M4-D | 锁定格式在 M4-A 稳定; 自动改写在 M4-C 后启用 | 只读监视、原子升级 PR、可信自动合并控制器、独立签名与发布控制器 | 每一级先完成无副作用/失败关闭验收再放权；可按 `paused` / `pr-only` / `merge` / `release` 降级 |
| 5 | M4-E | 官方后端和上游同步流程稳定 | 新配置/自定义词典/宿主路由的独立契约升级 | 每项先有 API 与旧实现回退测试, 不阻塞主线发布 |
| 6 | M5 | M4-D-2 自动 PR 流程稳定; 不要求 M4-D-3/M4-D-4 或 M4-E 完成 | 同一 APK 同时保留 AutoJs6 插件服务与独立应用入口, 提供完全离线的文本转换 UI | 独立/插件两种入口共用同一后端且可并发运行, 权限/API/签名/五 ABI/16 KB/可访问性/隐私门禁全部通过 |

当前检查点 (2026-09-03): M4-A、M4-B 与 M4-C 已完成；`v1.2.0` 标签、GitHub Release 和
插件中心在线索引已公开且相互校验一致。M4-D-2 的原子更新器、升级 PR 正文、最小权限双阶段工作流、
显式 Build/Markdown 调度和远端 Actions 建 PR 权限均已落地，真实 GitHub 当前版本重放返回无更新、
无漂移。M4-D-3 的默认分支可信判定器、读/写 job 隔离、精确 SHA 工作流证据、资源/许可证门禁、
合并前二次判定和离线故障矩阵已实现；远端 `OPENCC_AUTOMATION_MODE=pr-only`，因此当前只产生
判定摘要而不会写入。`master` 按维护策略保持不受保护；待首个真实或受控更新 PR 完成在线 dry-run
后，才将策略提升为 `merge`。M4-D-4 不阻塞 M4-E 或 M5。M5-A 已完成同 APK Launcher、共享
转换协调器与平台 Views 选型；M5-B 已完成 14 类型离线 UI、显式剪贴板/分享、取消与状态恢复。
M5-C 已完成双入口并发/生命周期/资源首启/API 与最终 APK manifest 安全门禁；M5-D 已完成十语言
单一来源、RTL/大字体/日夜主题/键盘/旋转/分屏/手机/平板可访问性、两张可复核设备截图，以及
API 24 x86、API 28 armv7、API 35 arm64 和 API 36 x86_64/16 KB 页的最终设备矩阵。M5-E 继续作为
后续发布主线，当前不改变 v1.2.0 Release 或在线索引。

### M4-A: 官方 OpenCC 原生后端原型 (2026-08-31, 已完成)

- [x] (依赖) 以 Git 子模块引入官方 OpenCC, 固定 `ver.1.4.2` / `025f371dc76b598d77384fbdab90c937471844d8`; `opencc-upstream.properties` 记录完整上游身份, 清洁构建不依赖本地绝对路径.
- [x] (依赖/插件) 引入同版本 `opencc-v1.4.2-resources.zip`; 构建脚本与在线监视器校验 GitHub Release digest, ZIP manifest 和逐文件摘要, 设备端以单个版本化 ZIP 原子安装并校验.
- [x] (插件) 新建内部 `:opencc-native` Android Library, 使用 NDK 28.2/CMake 构建官方 OpenCC 与 Marisa, 为四 ABI 静态链接单一 `libopencc_jni.so`, 不执行上游宿主机字典/CLI 目标.
- [x] (插件) 实现薄 JNI 与 JVM 门面: 14 配置白名单, Converter 缓存, 标准 UTF-8/UTF-16 转换, emoji/非 BMP 保真, C++ 异常边界与资源修复均有设备测试；M5-A 后缓存生命周期由共享协调器提升到应用进程级.
- [x] (插件/API) Binder 服务已切换到官方后端且维持 v1/v2 契约; capabilities 新增 OpenCC 版本, commit 和资源 SHA-256, 最低宿主版本不变.
- [x] (测试) M4-A/M4-B 期间将 `android-opencc:1.2.2` 严格限制为 JVM/仪器差分基线; APK 门禁证明正式 5 APK 不含旧类库的 native/resources 或动态 C++ 运行时, M4-C 随后已将该测试依赖彻底删除.

M4-A 验收条件: 官方 1.4.2 核心和 JNI 在 `arm64-v8a` / `armeabi-v7a` / `x86_64` / `x86` 四 ABI 构建成功; 14 种转换通过 JVM 契约测试与真实 Binder 冒烟测试; 正式 APK 内不再出现旧 `ChineseConverter` 原生库, 旧 AAR 资源或 `libc++_shared.so`; 源码, 资源和运行时版本信息可相互追溯. (已满足; 证据见 `docs/engineering/opencc-1.4.2-migration.md`)

### M4-B: 兼容性, 性能与 16 KB 验收 (2026-09-01, 已完成)

- [x] (测试) M4-B 迁移窗口已完成新旧引擎差分: 14 类型基础语料一致, 11 条官方词典变化逐条固定旧值/新值与审阅原因; 旧基线随后从构建图删除, 历史值继续归档于 `docs/engineering/opencc-1.4.2-migration.md`, 官方值继续由设备测试固定.
- [x] (测试) 仪器测试覆盖空文本, 长文本, emoji, 非 BMP, 批量/链式上限, 未知类型, 同长度损坏资源, SHA-256 不匹配后恢复, 64 路并发调用; 两阶段测试以不同 PID 验证真实进程重启后复用已校验资源且不重写文件.
- [x] (测试) 旧/新引擎首次加载, 新进程冷转换, 200 次热转换, 1,024 段批量负载, 峰值 PSS 和五种 APK 体积已归档于 `docs/engineering/opencc-1.4.2-benchmark.md`; Android 15 arm64 真机上官方后端为 313.726 ms / 285.502 ms / 0.836 ms median / 42.362 ms / 31.55 MiB 增量. 冷路径低于 0.4 秒且热/批量显著改善, 当前不引入按 ABI 生成 `.ocd2` 的复杂度.
- [x] (依赖/发布) 使用 NDK 28.2 重建最终 JNI `.so`; 四 ABI 均通过 ELF `LOAD >= 0x4000` 与 RELRO 检查, debug/release 各 5 APK 通过 `zipalign -c -P 16 4`, `jniLibs.useLegacyPackaging` 已删除且 native entries 保持未压缩.
- [x] (测试) 增强后的三阶段测试已在 API 24–36 覆盖 `arm64-v8a` / `armeabi-v7a` / `x86_64` / `x86`; Android 17 / API 37 `google_apis_ps16k` x86_64 模拟器实际报告 `PAGE_SIZE=16384`, 并通过安装, 插件发现, Binder 往返, 14 类型和不同 PID 重启复用. CI 新增 API 35 `google_apis_ps16k` 门禁并在测试前硬校验页大小.

M4-B 验收条件: 差分结果均可解释并有审阅记录; 新后端在现有四 ABI/API 矩阵无行为回归; 性能和体积报告已归档; 16 KB ELF, ZIP 对齐和真实运行环境全部通过. (已满足)

### M4-C: 正式替换与 v1.2.0 发布 (2026-09-01, 已完成)

- [x] (依赖/插件) 从版本目录和应用的单元测试, instrumentation 及正式配置中删除 `com.github.brooklet:android-opencc`, 删除旧 `ChineseConverter` / `ConversionType` 引用与旧资源初始化逻辑, 将官方后端提升为唯一 `default` 引擎; 三条 Gradle 依赖图均明确返回无匹配依赖.
- [x] (发布) 补齐 OpenCC, Marisa, Darts Clone 与 RapidJSON 的许可证/NOTICE, 更新 README, 10 语言 CHANGELOG, 插件说明和本 Roadmap, 清楚标注内置 OpenCC 版本/提交, 词典摘要, 离线特性与 16 KB 支持状态; 36 个生成产物通过漂移检查.
- [x] (发布准备) 版本已提升为 `v1.2.0` / build 19; 既有发布脚本已在 `build/release/v1.2.0` 原子生成 5 个本地签名 APK, `SHA256SUMS.txt` 与 `RELEASE_NOTES.md`, 并通过 CRC32, SHA-256, 精确 ABI, APK/ELF/资源内容及签名连续性门禁. 签名证书 SHA-256 与仓库 v1.0.2 留存包一致 (`31A681FCFFFB3E428420CAE280DED89292B12A3B0F59E19B7A73E32A8AE4C213`).
- [x] (设备) 删除迁移 AAR 后重新在 API 35 `arm64-v8a`, API 28 `armeabi-v7a` 与 API 37 / 16 KB `x86_64` 环境执行服务 + restart prepare/verify 三阶段测试; 全部通过且测试包清理完成. 旧 Android 无 `getconf` 时, CI 脚本会从 `/proc/self/smaps` 的 `KernelPageSize` 安全回退探测.
- [x] (发布) `v1.2.0` 标签已固定到 `a96beae56dd42b4a419019a40d878aa5d172f638` 并推送；[GitHub Release](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases/tag/v1.2.0) 已作为 Latest 正式发布，上传上述 5 个已验证 APK、`SHA256SUMS.txt` 与 `RELEASE_NOTES.md`，并列出经审阅的主要词典输出变化。GitHub 回读的 7 个资产名称、大小和 SHA-256 均与本地候选一致。
- [x] (发布) 插件中心在线索引已由其远端生成工作流更新至提交 `a95d0b84eb80c51c51ef4752b0136e5483879aa9`；OpenCC 条目为 `v1.2.0` / build 19，四 ABI 兼容列表、5 个下载地址、大小和 SHA-256 均与 GitHub Release 逐项一致，图标与多语言说明固定到同一标签。

M4-C 验收条件: 正式产物仅包含官方后端；v1.2.0 的源码标签、5 个 APK、校验和、GitHub Release
与插件索引相互一致；旧宿主继续使用 v1 接口，新宿主继续使用 v2 批量/链式接口。(已满足)

### M4-D: 上游同步自动化

M4-D 使用分阶段信任模型。仓库默认 `GITHUB_TOKEN` 权限保持 `contents: read`，只有具体 job 按需提升；
`master` 按项目治理选择保持不受保护，因此后续合并控制器必须主动核验每一项条件，不能把 GitHub 的
“Merge”按钮可用、同一机器人自批或分支名称本身当作通过证据。

#### M4-D-1: 只读发现 (已完成)

- [x] (CI/依赖) `.github/workflows/opencc-upstream.yml` 每周定时及手动查询最新正式 Release；`check_upstream.py` 验证标签 commit、GitHub asset digest 和资源 manifest 后与锁定文件比较，普通 Gradle 构建保持离线。
- [x] (CI/测试) 当前 OpenCC 1.4.2 已在本地和 GitHub runner 多次重放为明确无更新、无漂移；网络/API/摘要/manifest 任一异常均失败而不是假定“无更新”。

M4-D-1 验收条件: 当前版本重放稳定、普通构建无网络依赖、发现异常失败关闭。(已满足)

#### M4-D-2: 原子升级 PR (当前阶段)

- [x] (CI/依赖) `update_upstream.py` 对新版本二次校验正式标签提交、GitHub 资源大小/digest、ZIP manifest 提交/来源、stored entry、逐文件 SHA-256 与 16 配置；仅在干净检出中原子更新子模块指针、锁文件和版本化资源，生成后验证或文件清单异常时回滚并失败关闭。14 个离线测试覆盖当前/更新、schema、路径逃逸、精确变更清单、回滚、工作流输出和审阅正文。
- [x] (CI/依赖) 工作流先以 `contents: read` 只读发现，再仅对已验证的新版本启动具有 `actions: write`、`contents: write` 与 `pull-requests: write` 的独立 job；它二次下载并拒绝 TOCTOU 漂移，保护已有开放 PR 中的修订，使用 lease 更新 `automation/opencc-<version>` 分支，并显式 dispatch Build/Markdown。
- [x] (CI/测试) Build integrity 同时生成并审计 debug/release 各 5 APK；升级分支执行四 ABI、固定转换语料、Binder 4 KB/16 KB、RELRO/ZIP 对齐、R8/资源/旧后端排除和 APK 字节报告。
- [x] (CI/治理) 2026-09-02 已启用仓库 “Allow GitHub Actions to create and approve pull requests”，同时保留默认 workflow permission 为只读；`master` 按维护者选择不启用 branch protection。当前生成工作流不调用 approve、merge、tag 或 release API。
- [ ] (CI/测试) 以首个真实新 Release 或受控模拟 Release 端到端生成一次 PR，核对自动分支、PR 正文、两条显式 dispatch、失败时保留开放 PR、同版本开放 PR 不被后续定时任务覆盖；当前 1.4.2 在线重放已满足无更新路径。

M4-D-2 验收条件: 清洁 CI 不依赖 Maven Local、开发机缓存或 `T:\\...`；新版本只产生精确白名单变更和可追溯 PR，失败不合并、不覆盖人工/机器人修订。当前代码、权限和无更新路径已满足，尚待一次更新 PR 实跑。

#### M4-D-3: 无人值守自动合并 (`pr-only` 部署阶段)

- [x] (CI/治理) 增加独立于 PR 生成器的 `opencc-auto-merge.yml` / `merge_upstream.py` 可信控制器；仓库变量支持 `paused` / `pr-only` / `merge`，默认并已远端固定为 `pr-only`，预留的 `release` 值在 M4-D-4 落地前明确失败关闭。任何异常保留 PR 并告警，不自动修测试、改词典预期或绕过失败。
- [x] (CI/安全) `workflow_run` 控制器只显式 checkout 默认分支中已审计的代码且 evaluator 仅有读权限，不以写权限 checkout/执行 PR 内容；只接受同仓库、base=`master`、作者为预期 GitHub Actions Bot、head=`automation/opencc-<semver>` 且 SHA 精确匹配的开放 PR，并核对单一直接 bot commit 及锁文件/子模块/旧新资源四项 path/status 清单。
- [x] (CI/测试) 对同一 head SHA 查询显式 dispatch 的 Build integrity 与 Markdown integrity，选择最新精确 run 并要求精确 job 清单全部 `completed/success`；同时重新下载并验证最新官方 Release/ZIP，固定许可证证据不得变化，资源增长不得超过 512 KiB 或 25%。较旧成功 run、分支同名 run 或 PR 页面可合并状态均不能替代证据。
- [x] (CI/并发) 读侧和写侧都确认当前 base SHA、单一 commit parent、无冲突/请求更改/`do-not-merge` 或 `automation-pause[d]` 熔断；写 job 获得权限后重复全部门禁，合并调用绑定预期 head SHA，仅删除未变化分支。workflow 按 branch/head concurrency 串行，判定与 merge API 均为幂等设计并记录摘要。
- [x] (CI/治理) 不要求同一机器人批准自己创建的 PR；若未来引入独立 Reviewer App，其 approval 只作为额外审计信号，不能替代上述可复核门禁。11 个离线样本已覆盖成功、paused/release 失败关闭、陈旧 base、冲突、额外路径、错误/失败 run、请求更改、熔断、许可证/体积漂移、GitHub 服务故障和 SHA 绑定 merge。
- [ ] (CI/在线验收) 以 M4-D-2 的首个真实或受控更新 PR 在远端 `pr-only` 连续重放成功与失败样本，确认 workflow summary、无写副作用和 GitHub API 实际字段；随后才由维护者把变量提升为 `merge`，并以一次真实升级验证自动 squash merge/分支清理及一键退回 `pr-only`。

M4-D-3 验收条件: 在不保护 `master` 的治理选择下，受控成功样本可在所有精确门禁完成后自动合并；失败、陈旧 SHA、额外文件、冲突、熔断或服务异常样本全部保持未合并，且能一键退回 `pr-only`。当前代码、离线故障注入和远端只读策略已满足，尚待更新 PR 的在线 dry-run 与一次 `merge` 实跑。

#### M4-D-4: 自动签名与发布

- [ ] (发布/安全) 建立与合并控制器隔离的发布工作流和 GitHub Environment；签名材料仅来自加密 secrets，固定并校验现有证书 SHA-256，日志、缓存和 artifact 均不得包含 keystore/口令。没有完整签名配置时只生成可审计候选，不降级为未签名发布。
- [ ] (发布) 为纯 OpenCC 依赖升级定义确定性的版本/build 递增、十语言 changelog/迁移记录生成和兼容性分类；API、权限、applicationId、签名或许可证发生非白名单变化时自动停止并退回 `pr-only`。
- [ ] (发布/测试) 从刚合并且精确固定的 `master` commit 重建 5 个签名 APK，复跑签名连续性、四 ABI、R8、ELF/ZIP 16 KB、Binder 4 KB/16 KB、资源摘要与 APK 体积门禁；原子创建 tag、GitHub Release、`SHA256SUMS.txt` 和 release notes，并从 GitHub 回读全部资产名称/大小/SHA-256。
- [ ] (发布/索引) Release 回读一致后才显式 dispatch 插件索引更新并回读线上条目；tag/Release/索引任一步已有冲突、版本倒退或内容不一致时停止，不覆盖既有正式版本。合并由 `GITHUB_TOKEN` 产生时显式 dispatch 发布工作流，不依赖不会触发的递归 push 事件。
- [ ] (发布/治理) 先在 `release` 策略下完成受控候选/草稿与回滚演练，再启用正式 latest 发布；保留仓库变量级暂停、Release 撤回/非 latest 和索引回退手册。自动发布不阻塞 M4-E/M5 开发。

M4-D-4 验收条件: 一个允许自动发布的真实升级可从正式上游 Release 到签名 APK、GitHub Release 和插件索引全程无人值守且相互回读一致；所有故障注入均停在最后一个已验证状态，不泄露签名材料、不产生半发布。

M4-D 总体验收条件: D1/D2 建立可复现发现与升级 PR，D3 以精确机器门禁替代重复人工合并，D4 再将同样的失败关闭原则扩展到签名和公开发布。各阶段独立放权、可降级、可审计；D3/D4 是自动化增强，不阻塞 M4-E 或 M5。

### M4-E: 可选配置, 自定义词典与宿主扩展

- [ ] (API/插件/宿主) 在官方后端稳定后评估公开 `HK2SP` 与 `S2HKP` 两个现有资源配置; 先更新 opencc-api 的稳定类型列表和契约测试, 再更新宿主路由/类型声明与插件实现, 旧插件继续通过能力探测回退.
- [ ] (API/插件/宿主) 基于官方公开 `ResourceProvider` / 配置接口设计自定义词典能力, 明确资源大小, 配置白名单, 路径隔离, 校验, 生命周期和 Binder 限额; 不使用反射或旧 AAR 私有 JNI, 不接受未约束的任意文件读取.
- [ ] (宿主) Node.js 运行时支持继续作为宿主先行项: 宿主侧 `opencc` 目前为 Rhino 专属, Node.js 运行时仅有类型声明; 待宿主完成调用路由与资源边界设计后复用同一插件能力, 并更新 FAQ.

M4-E 验收条件: 每项扩展均先有 API 契约和旧实现回退测试, 再修改宿主与插件; 未发布的宿主能力不提前标记为插件现有功能.

M4 总体验收条件: M4-A 至 M4-D 全部完成后, 插件能够从官方固定 Release 可复现地构建并由自动化及时发现后续版本, 同时在四 ABI, 现有 API 矩阵和 16 KB 设备上保持可验证兼容. M4-E 为独立可选扩展, 不阻塞官方后端迁移和 v1.2.0 发布.

## M5: AutoJs6 插件与独立 App 双形态

目标是让同一个 applicationId、同一签名和同一组按 ABI 发布的 APK 同时具备两种合法入口：

- AutoJs6 继续通过现有受 `org.autojs.permission.PLUGIN` 保护的 Binder 服务发现和调用 OpenCC；
- 用户也可以从系统桌面直接启动 OpenCC App，在可视化页面中完成本地文本转换，不要求安装或启动 AutoJs6。

双形态不是复制两套引擎。UI、Binder 服务和后续其他入口必须复用同一应用层转换门面、官方资源安装器、
Converter 缓存、类型白名单和错误模型；独立 UI 不通过一次无意义的 Binder 回环调用自身服务，也不能改变
既有 AIDL 事务编号、插件 ID、`default` 变体或宿主能力探测结果。M4-E 的新增配置若尚未发布，M5 首版只展示
当前稳定的 14 种类型；未来新增类型必须通过能力数据驱动 UI，而不是硬编码假定所有后端都支持。

### M5-A: 双入口架构与最小原型 (2026-09-02, 已完成)

- [x] (插件/App) 从 `OpenccPluginService` 提取进程级惰性 `OpenccConversionCoordinator`；服务和 Activity 共用同一 engine/锁/类型解析/限额，原生门面、资源校验、Converter 缓存、JNI 和资源 ZIP 均没有复制。服务销毁不再关闭另一入口仍可能使用的缓存。
- [x] (App) 新增普通 `MAIN`/`LAUNCHER` `OpenccActivity`，同时保留受插件权限保护、无界面的 `WakeActivity` 与现有服务；桌面入口不要求 `org.autojs.permission.PLUGIN`，服务与 Wake 仍由 PackageManager 仪器断言该权限。
- [x] (App/依赖) 依据 minSdk 24、实测五 APK 固定增量 28,636 B、惰性冷启动、RTL/可访问性和现有工具链选用平台 Android Views/XML；未新增 UI runtime、网络、账号、分析或动态资源依赖，决策与复核数据见 `docs/engineering/standalone-app-architecture.md`。
- [x] (测试) `OpenccDualEntryTest` 从 Launcher 和 Binder 路径转换同一组含 emoji/非 BMP 的 `S2T` 文本，核对相同输出与 OpenCC version/commit/resource SHA-256，并审计单一 Launcher、组件权限及无 `INTERNET`；CI Binder 脚本已在所有设备 job 纳入该测试。

M5-A 验收条件: 同一 debug APK 可从桌面启动并继续被插件协议发现；UI 与服务共享后端，现有 Binder 三阶段测试、五 APK 内容门禁和 16 KB 设备测试无回归。 (已满足；API 35/arm64 与 API 28/32-bit armv7 真机通过双入口测试，Android 16/API 36/x86_64/`PAGE_SIZE=16384` 通过 Launcher + Binder + restart 三阶段，debug/release 各五 APK 通过 R8/签名/资源/ELF/ZIP 门禁，证据见 `docs/engineering/standalone-app-architecture.md`)

### M5-B: 离线文本转换 UI

- [x] (App/UI) 提供来源文本、结果文本、稳定转换类型选择器和明确的“转换”动作；14 种类型使用面向用户的名称并同时显示可核对的稳定代码，不以模糊的“简/繁”二选一掩盖地区与 JP 字形差异。
- [x] (App/UI) 提供清空、复制结果、显式粘贴、交换输入/输出文本（不隐式改变转换类型）和系统分享；所有剪贴板读取与分享只能由用户动作触发，不在启动、恢复或后台阶段自动读取。
- [x] (App/UI) 长文本转换在非主线程执行，支持取消、重复点击去抖、进度/错误状态和 Activity 销毁后的安全收尾；空文本、超长文本、emoji、非 BMP、RTL 混排与资源自动恢复沿用现有边界。
- [x] (App/状态) 旋转、分屏和系统进程重建后恢复必要的编辑状态；默认不建立永久转换历史，不把输入/输出写入日志、分析、备份或网络。若未来增加历史，必须单独设计显式开关、删除和数据迁移策略。

M5-B 验收条件: 用户无需 AutoJs6 即可完成 14 种转换及复制/分享；主线程无长转换阻塞，隐私默认值为不持久化、不自动读剪贴板、完全离线。 (已满足；完整交互、取消代际、分享 Intent、状态重建和设备矩阵证据见 `docs/engineering/standalone-app-architecture.md`)

### M5-C: 双形态并发、生命周期与安全

- [x] (测试) `OpenccDualEntryLifecycleTest` 在 Activity 长文本转换期间并发 64 路 Binder 请求和 16 轮独立 engine 转换/缓存清理，随后验证后台/回前台、最后一次解绑后服务真实销毁、UI 重开及两入口交替使用；现有旋转重建和增强后的不同 PID Bundle/资源重建测试共同覆盖 Activity 与进程生命周期，未出现崩溃、串型或迟到结果污染。
- [x] (安全) `verify_apk_variants.py` 直接解析每个 debug/release APK 的二进制 `AndroidManifest.xml`，拒绝额外 Activity/alias/Service/receiver/provider、额外权限、组件权限漂移、data/share filter 和自定义任务属性；设备端 PackageManager 再核对组件全集、普通任务栈、单一 Launcher、受插件权限保护的 Wake/Service 及恶意 URI/文本 payload 不进入编辑器。Launcher 仍只声明 `MAIN`/`LAUNCHER`。
- [x] (插件/API) `opencc-api.aar` 固定 SHA-256 `5f3001e28fb4c4967b0a4faeb4547a41a679b35cbd209d272a6a79f7ba00ab45`；JVM 快照锁定五个 AIDL 签名和 1–5 事务号，设备测试直接以原始事务 1/2 重放 v1 `getInfo`/`convert`，再覆盖 v2 枚举/批量/链式调用。插件 ID/engine/`default` 变体、最低宿主、能力元数据、宿主 33 方法及旧宿主回退均未改动；UI 选择 T2S 后 Binder 显式 S2T 仍返回 S2T 结果。
- [x] (离线) 最终二进制 manifest 和 PackageManager 双重审计证明唯一请求权限仍为 `org.autojs.permission.PLUGIN`、不存在 `INTERNET`，并新增 `usesCleartextTraffic=false`；两个独立新进程分别证明打开 UI、绑定服务和读取能力均不触碰资源，首个 UI 转换可从 APK 内同版本资源修复同长度损坏副本，首个 Binder 转换可从缺失状态安装且最终只留下 SHA-256 一致的单一 ZIP，无设备端下载路径。

M5-C 验收条件: UI 与 Binder 可在同一进程生命周期内安全并发；攻击面仅增加一个无敏感参数的 Launcher Activity，插件权限边界、离线属性和资源完整性不下降。 (已满足；API 35 arm64、API 28/32-bit armv7 与 Android 16/API 36/x86_64/`PAGE_SIZE=16384` 均通过八阶段设备矩阵，debug/release 五 APK 安全门禁和详细证据见 `docs/engineering/standalone-app-architecture.md`)

### M5-D: 多语言、可访问性与设备体验 (2026-09-03, 已完成)

- [x] (App/UI) `.readme/android_strings.json` 成为 UI 文案单一来源，与 README/插件说明同由生成器维护；英语、阿拉伯语、西班牙语、法语、日语、韩语、俄语、简体中文、香港繁体和台湾繁体的 locale/key/格式参数严格同构，Manifest `localeConfig` 精确声明同一组 10 个 locale。生成链现覆盖 47 个受控产物，并明确将 JP 路径描述为汉字字形转换而非语言翻译。
- [x] (App/UI) 页面同时支持日/夜主题、LTR/RTL、170% 字体、TalkBack 标题/标签/live status/进度描述与确定焦点链；所有操作目标至少 48 dp，来源和结果可独立滚动/选择。自定义多行类型选择项避免窄屏截断，Ctrl+Enter 执行转换、Escape 取消；真实旋转到相反方向再恢复可保留 Unicode 编辑状态，320 x 480 阿拉伯语夜间手机、360 x 360 分屏和 960 x 600 `sw600dp` 平板配置均有仪器断言。
- [x] (测试) `OpenccAccessibilityLayoutTest` 固定语义、键盘流、触控尺寸、日夜色彩、RTL、字体放大、横竖屏重建、分屏与手机/平板布局；`OpenccDocumentationScreenshotTest` 提供可重放的无个人数据截图夹具。最终脚本已在 API 24/x86/4 KB 模拟器、API 28/armeabi-v7a/4 KB 真机、API 35/arm64-v8a/4 KB 真机及 API 36/x86_64/16 KB 模拟器通过；API 35 与 API 36 另在阿拉伯语、170% 字号和夜间模式运行增强用例并恢复设备状态。Actions 新增独立 minSdk 24/x86 门禁。
- [x] (文档) 10 语言 README、11 份 Android 插件说明和 FAQ 均同时说明独立 App 与 AutoJs6 插件两条路径，清楚区分 ABI 选择、直接启动和宿主内启用步骤，并明确独立使用不要求安装 AutoJs6 或授予插件权限。README 纳入 1080 x 1920 英语日间与阿拉伯语 RTL/大字体/夜间原始设备截图；PNG 参数、SHA-256、唯一引用和完整资产清单均由生成器校验。

M5-D 验收条件: 10 语言及 47 个生成物无漂移，LTR/RTL、TalkBack、大字体、旋转/分屏和手机/平板布局均有代码、测试与原始截图证据；最终 APK 的 `localeConfig`、资源与文档双路径表述均有自动门禁。 (已满足；详细证据见 `docs/engineering/standalone-app-architecture.md` 与 `docs/images/screenshots/README.md`)

### M5-E: 双形态正式发布

- [ ] (发布) 沿用同一 applicationId、签名证书和五种 ABI 产物，验证从 v1.2.0 及后续纯插件版本原地升级后同时出现 Launcher 且插件中心仍识别同一插件，不创建互相冲突的“App 版/插件版”包名。
- [ ] (发布) Release、`SHA256SUMS.txt`、官方插件索引与 APK manifest 同时记录独立入口、插件服务、最低 Android、ABI、16 KB 和完全离线能力；发布前重新执行签名连续性、R8、ELF/ZIP、UI 与 Binder 全矩阵。
- [ ] (发布) 首个双形态版本号和发布日期仅在 M5-A 至 M5-D 全部验收后确定；不得为了预占版本号提前修改公开索引或把原型表述为稳定 App。

M5 总体验收条件: 用户安装同一个正式 APK 后，既可从桌面使用完整离线转换 UI，也可由 AutoJs6 通过原协议调用；两种模式共享官方固定后端且互不破坏，升级、签名、隐私、权限、可访问性、四 ABI 与 16 KB 兼容均有自动化和设备证据。

## 边界 (非目标)

- 不做中文与日文之间的翻译: JP 相关转换仅处理汉字字形 (繁体旧字体与日文新字体), 不涉及语言翻译.
- M5 的独立界面只提供本地文本转换，不扩展为云同步、账号系统、在线翻译、富文本编辑器或任意第三方无权限调用接口；Binder 服务仍只接受 AutoJs6 插件权限保护的调用。
- 不自定义宿主 API 形态: `opencc` 全局对象的方法集与组合逻辑由 AutoJs6 宿主定义, 插件侧忠实提供 14 种核心转换.
- 不引入网络能力: 转换始终基于内置词典在设备本地完成.
