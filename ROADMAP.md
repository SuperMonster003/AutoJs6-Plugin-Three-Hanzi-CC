# AutoJs6 OpenCC 插件 Roadmap

更新日期: 2026-08-31

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
| M3 转换能力增强 | 未开始 | 类型枚举, 批量与链式转换, 自定义词典评估 | API/插件/宿主 |
| M4 运行时与生态演进 | 未开始 | 16 KB 内存页适配, Node.js 跟进与词典演进 | 依赖/宿主/发布 |

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

## M3: 转换能力增强 (未开始)

- [ ] (API/宿主) 转换类型枚举接口: opencc-api 契约新增 `getSupportedConversionTypes()`, 宿主与插件中心可动态展示当前插件实际支持的类型, 替代双方各自硬编码 (契约升级, 宿主先行).
- [ ] (API/插件) 批量转换接口: 契约新增 `convertBatch(texts, conversionType)`, 一次跨进程往返转换多段文本, 降低高频调用场景的 Binder 开销 (契约升级, 宿主先行).
- [ ] (API/插件) 链式转换下沉: 契约支持一次调用按序执行多个转换类型, 使宿主侧 `twi2jp` 等组合方法从最多 3 次往返降为 1 次 (契约升级, 宿主先行).
- [ ] (插件) `getInfo()` 返回体填充 `instruction` 字段 (按调用方语言返回使用说明摘要), 与插件中心的说明展示打通.
- [ ] (插件/依赖) 自定义词典可行性评估: 调研 `android-opencc` 对自定义 OpenCC 配置与词典的扩展能力, 或评估迁移至官方 OpenCC JNI 封装的成本与收益, 结论回写本文件后再决定是否立项.

验收条件: 契约相关条目在宿主发布对应支持后实施并保持向后兼容 (旧宿主仍可使用既有两方法接口); 每项新能力附带对应测试用例.

## M4: 运行时与生态演进 (未开始)

- [ ] (依赖/发布) 16 KB 内存页适配: 评估 `android-opencc:1.2.2` 原生库在 16 KB page size 设备 (Android 15+) 上的加载兼容性; 如不满足, 推动依赖升级或以 16 KB 对齐参数重建, 真机验证通过后在 README 与发布说明中标注支持状态.
- [ ] (宿主) Node.js 运行时支持跟进: 宿主侧 `opencc` 目前为 Rhino 专属, Node.js 运行时仅有类型声明; 待宿主完成词典打包与资源查找设计后同步适配并更新 FAQ (宿主先行).
- [ ] (依赖) OpenCC 词典与引擎版本演进: 跟进上游 OpenCC 新版词典与配置, 评估以新 variant 并行发布的可行性, 保持现有 `default` 变体行为不回归.
- [ ] (发布) 插件中心在线索引元数据维护: 确保官方插件索引仓库中本插件的下载地址与版本信息随每次 Release 同步更新.

验收条件: 各演进项在真机验证通过且现有设备行为不回归后勾选; 依赖宿主或上游的条目仅在对应能力发布后开始实施.

## 边界 (非目标)

- 不做中文与日文之间的翻译: JP 相关转换仅处理汉字字形 (繁体旧字体与日文新字体), 不涉及语言翻译.
- 不提供独立界面与桌面入口: 插件仅通过 AutoJs6 插件权限被宿主调用, 不接受第三方应用访问.
- 不自定义宿主 API 形态: `opencc` 全局对象的方法集与组合逻辑由 AutoJs6 宿主定义, 插件侧忠实提供 14 种核心转换.
- 不引入网络能力: 转换始终基于内置词典在设备本地完成.
