# OpenCC 1.4.2 M4-B 性能与内存报告

记录日期: 2026-09-01

## 结论

官方 OpenCC 1.4.2 后端在首次安装后首转和新进程冷转时，会校验 1.24 MB 资源 ZIP 并建立常驻
`S2T` 转换器，因此冷路径和峰值内存均高于旧 `android-opencc:1.2.2`。转换器进入缓存后，官方
后端在 Android 15 arm64 真机上的热转中位数为 0.836 ms，旧引擎为 32.725 ms；1,024 段顺序
负载分别为 42.362 ms 和 33.530 s。官方后端以约 20.3 MiB 的额外峰值 PSS 换取约 39 倍热转
和约 792 倍批量吞吐。

官方后端在真机的首次安装后首转为 313.726 ms，新进程冷转为 285.502 ms，均未达到需要立即
改变资源格式的程度。当前继续使用官方同版本纯文本资源 ZIP，不引入由 CI 按 ABI 生成
`.ocd2` 的构建、版本和跨架构验证风险。后续上游升级使用同一基准重放；若冷路径出现明显回归，
再独立评估资源格式，而不是把未经验证的优化带入 v1.2.0。

## 方法

基准由 `OpenccPerformanceBenchmarkTest` 和 `scripts/benchmark/run_opencc_benchmark.py` 共同执行。
宿主运行器会拒绝重置已安装的插件，除非显式传入 `--allow-package-reset`；每个引擎均经过独立的
卸载/安装周期，并使用两个不同 PID：

1. `first-load` 删除对应引擎的设备端资源，测量资源安装、原生库加载和第一次 `S2T` 转换。
2. 强制停止应用后，`steady-state` 在新 PID 中对已安装资源执行第一次冷转换。
3. 冷转换之后先预热 20 次，再记录 200 次热转换的 min/median/p95/max。
4. 批量负载对 1,024 段文本顺序调用同一转换器；这对应插件 `convertBatch` 在一次 Binder 往返
   内部执行的转换循环，不把 Binder 客户端调度噪声混入旧/新原生引擎比较。
5. 测试进程在冷转换前后及内存负载期间采集 PSS、private dirty、Java heap 和 native heap；
   表中的“峰值增量”以稳态阶段转换前的进程 PSS 为基线。

单次热转换输入为 1,376 个 UTF-16 code units / 1,312 个 Unicode code points，包含简体中文、
ASCII、emoji 和 U+20000 非 BMP 字符。两引擎的输出都由测试断言为相同的预期繁体结果。时间数据
来自 debug 目标和 instrumentation 测试，只用于同设备、同 APK、同负载的迁移判断，不是跨设备
性能承诺，也不设置容易受模拟器负载影响的 CI 时间阈值。

## Android 15 arm64 真机

| 项目 | 值 |
|---|---|
| 设备 | Xiaomi `23046RP50C` |
| 系统 | Android 15 / API 35 |
| ABI | `arm64-v8a`, 64-bit 进程 |
| 页大小 | 4,096 bytes |
| 目标 APK SHA-256 | `5f20d12acaff5e9df94788f3be8793d7d46fa97c80685287925a6aad6cfc1cef` |
| 测试 APK SHA-256 | `7c783a1e6e5dabf9337bfcf85e945dd7c8f7b31a5a7fdf1de776cd95dd9ccbca` |

### 时间

| 引擎 | 首次安装后首转 | 新进程冷转 | 热转中位数 | 热转 p95 | 1,024 段总耗时 |
|---|---:|---:|---:|---:|---:|
| 旧 `android-opencc:1.2.2` | 54.446 ms | 41.422 ms | 32.725 ms | 36.830 ms | 33,529.584 ms |
| 官方 OpenCC 1.4.2 | 313.726 ms | 285.502 ms | 0.836 ms | 0.855 ms | 42.362 ms |

相同负载下，官方后端首次首转约为旧引擎的 5.76 倍，冷转约为 6.89 倍；进入热路径后，官方
后端的热转中位数约快 39.1 倍，1,024 段负载约快 791.5 倍。该结果说明冷路径成本来自一次性
资源校验和转换器建立，而非持续影响每次转换。

### 内存与资源

| 引擎 | 首次加载 PSS 增量 | 稳态峰值 PSS | 相对进程基线增量 | 安装后资源 |
|---|---:|---:|---:|---:|
| 旧 `android-opencc:1.2.2` | 8.70 MiB | 48.23 MiB | 11.27 MiB | 1,121,101 B |
| 官方 OpenCC 1.4.2 | 29.15 MiB | 68.08 MiB | 31.55 MiB | 1,237,703 B |

官方后端峰值增量比旧引擎多约 20.28 MiB。该内存由版本化资源 provider 和缓存转换器占用，
服务销毁时 `nativeClearCache` 会释放；并发调用仍由服务串行进入同一转换器，不会为每个 Binder
请求复制一套字典。

## 16 KB 页 x86_64 模拟器复核

| 项目 | 值 |
|---|---|
| 设备 | `sdk_gphone16k_x86_64` |
| 系统 | Android 17 / API 37 |
| ABI | `x86_64`, 64-bit 进程 |
| 页大小 | 16,384 bytes |
| 系统镜像 | `google_apis_ps16k`, build `CE2A.260420.019/15611780` |
| 目标 APK SHA-256 | `75ecfa1e9bed8f48930136b5b2bb2d32873569099ee0459d4a59a78ce41e056c` |
| 测试 APK SHA-256 | `7c783a1e6e5dabf9337bfcf85e945dd7c8f7b31a5a7fdf1de776cd95dd9ccbca` |

| 引擎 | 首次安装后首转 | 新进程冷转 | 热转中位数 | 热转 p95 | 1,024 段总耗时 | 峰值 PSS 增量 |
|---|---:|---:|---:|---:|---:|---:|
| 旧 `android-opencc:1.2.2` | 80.768 ms | 37.662 ms | 28.381 ms | 46.383 ms | 31,909.111 ms | 10.12 MiB |
| 官方 OpenCC 1.4.2 | 567.230 ms | 370.621 ms | 0.864 ms | 1.421 ms | 60.291 ms | 32.30 MiB |

模拟器绝对时间不用于发布阈值；它证明相同基准和 Unicode 负载在 `PAGE_SIZE=16384` 的真实进程
中可重复运行。该环境还完整通过插件发现、Binder 绑定、14 类型、差分语料、长文本、并发、资源
恢复以及不同 PID 的 restart prepare/verify 三阶段测试。

## API/ABI 设备矩阵

增强后的三阶段测试在本轮实际重放如下：

| 环境 | APK ABI | 页大小 | 结果 |
|---|---|---:|---|
| Android 7.0 / API 24 模拟器 | `x86` | 4 KB | 服务 + restart prepare/verify 通过 |
| Android 9 / API 28 真机 | `armeabi-v7a` | 4 KB | 服务 + restart prepare/verify 通过, `primaryCpuAbi=armeabi-v7a` |
| Android 10 / API 29 模拟器 | `x86` | 4 KB | 服务 + restart prepare/verify 通过, `primaryCpuAbi=x86` |
| Android 15 / API 35 真机 | `arm64-v8a` | 4 KB | 服务 + restart prepare/verify 通过, `primaryCpuAbi=arm64-v8a` |
| Android 16 / API 36 模拟器 | `x86_64` | 4 KB | 服务 + restart prepare/verify 通过 |
| Android 17 / API 37 16 KB 模拟器 | `x86_64` | 16 KB | 服务 + restart prepare/verify 通过, `PAGE_SIZE=16384` |

CI 的常规 API 35 任务现在先断言 `PAGE_SIZE=4096`；新增的 `google_apis_ps16k` 任务先断言
`PAGE_SIZE=16384`，再执行相同三阶段脚本。由此 16 KB 支持同时具有 ELF `PT_LOAD`、APK ZIP
对齐和真实 16 KB 进程运行三层门禁。

## Minified release APK 体积

| ABI | v1.0.2 | 当前官方后端 | 增量 |
|---|---:|---:|---:|
| `arm64-v8a` | 980,054 B | 1,489,096 B | +509,042 B (+51.9%) |
| `armeabi-v7a` | 924,348 B | 1,150,350 B | +226,002 B (+24.4%) |
| `x86_64` | 997,727 B | 1,497,893 B | +500,166 B (+50.1%) |
| `x86` | 1,000,704 B | 1,451,306 B | +450,602 B (+45.0%) |
| `universal` | 2,041,573 B | 3,824,645 B | +1,783,072 B (+87.3%) |

资源 ZIP 为五个 APK 的共同固定成本；universal 还同时携带四 ABI 静态链接库。v1.2.0 发布准备
会重新生成最终签名产物并更新此表，不用当前未发布的 1.1.0 文件冒充最终 Release。
