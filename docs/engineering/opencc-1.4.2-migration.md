# OpenCC 1.4.2 官方后端迁移记录

记录日期: 2026-09-01

## 结论

M4-A 与 M4-B 已通过仓库级、APK 级和设备级验收。M4-C 已将迁移期 `android-opencc` AAR
从所有 Gradle 配置和测试代码中彻底删除，官方 OpenCC 1.4.2 是唯一 `default` 后端。差分语料、
异常路径、性能/内存基准、四 ABI/API 设备矩阵以及 ELF/APK/真实 16 KB 页三层门禁均已完成；
v1.2.0 / build 19 的五包本地签名发布候选也已生成并验证。尚未完成的是需要维护者授权的源码
标签、GitHub Release 上传与插件中心索引更新，因此本记录不把本地候选表述为已公开发布。

## 上游追溯

| 项目 | 固定值 |
|---|---|
| OpenCC Release | `1.4.2` / `ver.1.4.2` |
| 官方源码提交 | `025f371dc76b598d77384fbdab90c937471844d8` |
| 官方资源 | `opencc-v1.4.2-resources.zip` |
| 资源大小 | `1,237,703` bytes |
| 资源 SHA-256 | `9ea0d303219b34d014d5c116677b5d325043beafb2c8a62ee889ca67f4d054a5` |
| 资源内容 | 39 个 stored entries，含 16 个配置和 manifest |
| Android 工具链 | NDK `28.2.13676358` / CMake `3.22.1` / C++17 |

`scripts/opencc/verify_upstream.py` 同时核对源码提交/标签/remote、ZIP 摘要、manifest
提交与来源、逐文件摘要、配置清单及配置引用闭包。`scripts/opencc/check_upstream.py` 进一步从
GitHub Release API 核对正式 Release、标签最终 commit 与资产 digest；2026-08-31 的在线重放
结果为无更新、无漂移。

## 新旧引擎差分审阅

M4-B 迁移窗口曾在测试 APK 中保留 `android-opencc:1.2.2`，并实测确认 14 种转换对基础语料
`汉字漢字软件軟體里面裏面` 的结果全部一致。M4-C 已删除这项测试依赖；下表保留当时采集并
审阅的历史旧值，当前设备测试继续固定官方 1.4.2 输出，而不再把旧引擎装入测试 APK：

| 类型 | 输入 | 旧基线 | 官方 1.4.2 | 审阅结论 |
|---|---|---|---|---|
| S2T | `托着` | `託着` | `托着` | 托/託候选顺序修正 |
| S2T | `复盘` | `覆盤` | `復盤` | 新增明确词条，修复错误字形 |
| S2T | `内卷` | `內卷` | `內捲` | 地区用字修正 |
| S2T | `谷神谷神星` | `穀神穀神星` | `谷神穀神星` | 古籍语境例外且保留谷神星 |
| T2S | `乾斷食乾紅` | `乾断食乾红` | `干断食干红` | 与官方 1.4.2 测试语料一致 |
| TW2S | `什么怎么这么` | `什幺怎幺这幺` | `什么怎么这么` | 修复么/幺破坏性转换 |
| S2TWP | `内存条` | `記憶體條` | `記憶體模組` | 台湾地区术语更新 |
| S2TWP | `数字人文` | `數字人文` | `數位人文` | 台湾地区术语更新 |
| S2TWP | `互联网络` | `網際網路絡` | `網際網路` | 修复短词优先导致的贪婪匹配错误 |
| S2TWP | `快闪存储器` | `快快閃記憶體儲器` | `快閃記憶體` | 修复短词优先导致的贪婪匹配错误 |
| S2TWP | `老挝人民民主共和国` | `寮國人民民主共和國` | `寮人民民主共和國` | 对齐台湾官方译名 |

官方输出断言位于 `OpenccPluginServiceTest`，旧值和审阅原因保留在本表。后续上游升级若改变
任一官方输出，必须先更新审阅记录再合并，不需要也不得重新引入已退役的旧包装库。

## 已通过门禁

- 官方核心和 JNI 已为 `arm64-v8a`、`armeabi-v7a`、`x86_64`、`x86` 构建成功。
- debug/release 各 5 个 APK 的 ABI 集合精确匹配；每个 ABI 仅含 `libopencc_jni.so`，且不含
  `libChineseConverter.so`、`libopencc.so`、`libc++_shared.so` 或旧 `assets/openccdata/`。
- 四 ABI 最终 JNI 的 ELF `PT_LOAD` 最低对齐均为 `0x4000`，均存在 GNU RELRO；10 个 APK
  均通过 Android Build Tools 37.0.0 的 `zipalign -c -P 16 4`；release APK 另通过签名校验，
  R8 后仍保留 JNI 类描述符和两个 native 方法。
- API 36 / x86_64 与 API 29 / x86 模拟器完成插件发现、绑定和 14 类型转换；增强测试还覆盖
  空文本、约 28K UTF-16 长文本、emoji、非 BMP、批量/链式上限、未知类型、64 路并发调用、
  同长度资源篡改、SHA-256 失败后自动恢复、关闭重开与已验证资源复用；两阶段测试还断言
  instrumentation PID 确实变化，并确认真实进程重启后资源文件时间戳不变。
- JVM 契约测试、5 个上游监视测试和 7 个发布工具测试通过。
- Android 15 / API 35 `arm64-v8a` 真机与 Android 9 / API 28 `armeabi-v7a` 真机已重放相同的
  三阶段增强测试；另在 API 24 `x86`、API 29 `x86` 和 API 36 `x86_64` 模拟器覆盖最低 API、
  32 位与 64 位路径。
- Android 17 / API 37 `google_apis_ps16k` x86_64 模拟器实际报告 `PAGE_SIZE=16384`，并通过
  安装、插件发现、14 类型、差分/异常测试和不同 PID 的资源重启复用；CI 新增 API 35
  `google_apis_ps16k` 任务，在运行相同三阶段脚本前硬校验页大小。
- 旧/新引擎性能和 PSS 已归档于 `docs/engineering/opencc-1.4.2-benchmark.md`。Android 15 arm64
  真机上官方后端首转 313.726 ms、冷转 285.502 ms、热转中位数 0.836 ms、1,024 段 42.362 ms；
  峰值 PSS 相对基线增加 31.55 MiB。当前保留官方 ZIP，不引入 `.ocd2` 生成链。
- M4-C 删除旧 AAR 后，`debugAndroidTestRuntimeClasspath`、`debugUnitTestRuntimeClasspath` 与
  `releaseRuntimeClasspath` 对 `com.github.brooklet:android-opencc` 的 dependency insight 均返回
  无匹配依赖；新的 instrumentation APK 也不含旧 native、资源目录或类标记。
- 删除迁移 AAR 后的新测试包已在 API 35 `arm64-v8a` 真机、API 28 `armeabi-v7a` 真机及
  API 37 / `PAGE_SIZE=16384` x86_64 模拟器重新通过服务 + restart prepare/verify 三阶段测试；
  测试脚本对没有 `getconf` 的旧 Android 从 `/proc/self/smaps` 的 `KernelPageSize` 回退探测。

## M4-C 本地发布候选

`scripts/release/prepare_release.py` 已从最终 minified release APK 原子生成
`build/release/v1.2.0`。该目录是本地构建产物而非提交内容；五包签名证书 SHA-256 均为
`31A681FCFFFB3E428420CAE280DED89292B12A3B0F59E19B7A73E32A8AE4C213`，与仓库留存的
v1.0.2 正式包一致。

| ABI | 本地候选文件 | 大小 | SHA-256 |
|---|---|---:|---|
| arm64-v8a | `autojs6-plugin-opencc-v1.2.0-arm64-v8a-f663d404.apk` | 1,499,452 B | `aa7007249475bc5312846652bae794c8eadb1c87205af9c7ec266d9934802923` |
| armeabi-v7a | `autojs6-plugin-opencc-v1.2.0-armeabi-v7a-1c9378a1.apk` | 1,160,706 B | `967b792f1fbe04d7bf689eb03903d927649d564f946511bbe80e03f7ec2cd8f2` |
| x86_64 | `autojs6-plugin-opencc-v1.2.0-x86_64-ab268561.apk` | 1,508,249 B | `a714c4786ebc491338f2841236c437ab14ec58ce58cbdecbc2d0b55c859286b0` |
| x86 | `autojs6-plugin-opencc-v1.2.0-x86-4dc6b9dc.apk` | 1,461,662 B | `0e69ad0f438c13f6bd6104ecfb8438b9965923fd26bad02fd39e69909db1fc37` |
| universal | `autojs6-plugin-opencc-v1.2.0-universal-9ff59a9c.apk` | 3,835,001 B | `2b2b03c430be83bc212ed6358c7ec08c13f4141c380f11ee95263afa6b0cc2d3` |

每个原始 release APK 和上述重命名候选均通过签名、精确 ABI、官方资源摘要、旧后端排除、
R8 JNI 标记、ELF `0x4000`/RELRO 与 `zipalign -c -P 16 4` 门禁。随包生成的
`SHA256SUMS.txt` 与 `RELEASE_NOTES.md` 已列出同一组文件和经审阅的主要词典变化。

## M4-C 尚未完成的外部门禁

- 经维护者确认后创建并推送 `v1.2.0` 源码标签，发布 GitHub Release 并上传本地候选五包、
  `SHA256SUMS.txt` 与发行说明。
- 更新插件中心在线索引中的版本、下载地址、摘要和兼容信息，并与 GitHub Release 交叉核对。

## v1.2.0 本地候选 APK 体积

同一开发机签名配置下，将 v1.2.0 本地候选的 minified release APK 与仓库留存的 v1.0.2
正式 APK 对比。若发布前代码或资源再次改变，必须重新生成候选并更新本表：

| ABI | v1.0.2 | 当前官方后端 | 增量 |
|---|---:|---:|---:|
| arm64-v8a | 980,054 B | 1,499,452 B | +519,398 B (+53.0%) |
| armeabi-v7a | 924,348 B | 1,160,706 B | +236,358 B (+25.6%) |
| x86_64 | 997,727 B | 1,508,249 B | +510,522 B (+51.2%) |
| x86 | 1,000,704 B | 1,461,662 B | +460,958 B (+46.1%) |
| universal | 2,041,573 B | 3,835,001 B | +1,793,428 B (+87.8%) |

主要固定成本是 1,237,703 B 的官方纯文本资源 ZIP。M4-B 的真机性能结论是不改为按 ABI 生成
`.ocd2`：冷路径仍低于 0.4 秒，热路径和批量吞吐显著改善，不值得为体积优化引入尚未建立的
跨架构词典生成与验证链。
