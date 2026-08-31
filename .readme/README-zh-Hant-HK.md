<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>用於中文文本轉換的 OpenCC 插件</p>

  <p>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/SuperMonster003/AutoJs6-Plugin-OpenCC?label=Release"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/SuperMonster003/AutoJs6-Plugin-OpenCC?color=A24232&label=Issues"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/SuperMonster003/AutoJs6-Plugin-OpenCC?color=534BAE&label=License"/></a>
  </p>
</div>

******

### 語言 (Languages)

******

目前 README.md 支援以下語言:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hans.md)
- 繁體中文 (香港) [zh-Hant-HK] # 目前
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-en.md)
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-fr.md)
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-es.md)
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ja.md)
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ko.md)
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ru.md)
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-ar.md)

******

### 簡介

******

OpenCC 插件 (OpenCC Plugin) 為 AutoJs6 提供基於 [OpenCC](https://github.com/BYVoid/OpenCC) 的中文文本轉換能力. 安裝本插件後, AutoJs6 腳本中的全局對象 `opencc` 即可正常工作, 一行代碼即可在簡體, 繁體, 香港繁體, 台灣正體與日文新字體之間完成轉換, 無需導入模組, 無需連線.

插件採用宿主與插件分工的設計: AutoJs6 宿主提供腳本直接調用的 `opencc` API, 插件以獨立應用程式的形式攜帶 OpenCC 轉換引擎與詞典. 從 AutoJs6 6.8.0 起宿主不再內置 OpenCC 運行時, 中文轉換功能由本插件按需提供; 這樣宿主安裝包保持精簡, 轉換引擎也可以獨立於宿主更新.

******

### 功能亮點

******

- 開箱即用: 插件安裝到裝置後由 AutoJs6 自動發現, 無需重啟宿主, 無需任何配置, 腳本即可直接調用 `opencc` 全局對象.
- 14 種標準轉換: 覆蓋 OpenCC 的簡繁轉換, 香港/台灣地區用字轉換與日文新字體轉換, 並支援台灣常用詞彙轉換 (如 `软件` 與 `軟體` 的互換).
- 33 個腳本方法: 除通用的 `opencc.convert(text, type)` 外, 每種轉換類型都有同名快捷方法, 還提供 `s2jp`, `tw2hk` 等 18 個別名與組合方法.
- 完全離線: 轉換基於插件內置詞典在裝置本地完成, 插件不申請網絡權限, 不收集任何數據.
- 按需選包: 提供 4 種單架構安裝包與包含全部架構的 `universal` 包, 裝置只需安裝匹配的包, 體積更小.
- 多語言: 插件資訊, 使用說明, README 與更新日誌覆蓋 10 種語言.
- 輕量背景服務: 插件無獨立介面, 由宿主按需喚醒與綁定, 空閒時自動釋放連接.

******

### 使用方法

******

1. 將 AutoJs6 升級到內部版本號 3923 (6.7.1 Alpha4) 及以上; 6.8.0 正式版及更新版本均滿足要求.
2. 從 [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) 頁面或 AutoJs6 插件中心下載並安裝插件 APK; 不確定選哪個安裝包時, 可直接選 `universal` 包, 或參考下方 `如何選擇安裝包`.
3. 開啟 AutoJs6 的插件中心, 確認 `OpenCC` 插件已被識別並處於啟用狀態; 官方發佈包會自動通過簽名校驗, 無需手動授權.
4. 在腳本中直接使用 `opencc` 全局對象, 例如 `opencc.s2t("汉字")`; 無需 require 或 import, 安裝插件後也無需重啟 AutoJs6.

> 插件支援 Android 7.0 (API 24) 及以上的裝置. 若腳本運行時提示缺少插件或宿主版本過低, 請參考下方 `常見問題`.

******

### 快速上手

******

安裝完成後, 以下腳本可直接運行, 註釋為預期輸出:

```javascript
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.t2jp("圖書館"));      // => 図書館
```

快捷方法與通用方法 `opencc.convert(text, type)` 等價; `opencc` 對象本身也可以作為函數調用, 轉換類型名不區分大小寫:

```javascript
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
console.log(opencc("汉字转换", "s2t"));         // => 漢字轉換
```

所有方法均同步返回轉換後的字串, 轉換在本地詞典上完成, 不產生任何網絡請求.

******

### 轉換類型

******

`convert` 方法與同名快捷方法支援以下 14 種 OpenCC 標準轉換類型, 類型名中 S 表示簡體, T 表示繁體 (OpenCC 標準), HK 表示香港繁體, TW 表示台灣正體, JP 表示日文新字體:

| 類型 | 轉換方向 |
|---|---|
| `S2T` | 簡體到繁體 |
| `T2S` | 繁體到簡體 |
| `S2TW` | 簡體到台灣正體 |
| `TW2S` | 台灣正體到簡體 |
| `S2TWP` | 簡體到台灣正體, 並替換為台灣常用詞彙 (如 `内存` 轉為 `記憶體`) |
| `TW2SP` | 台灣正體到簡體, 並替換為大陸常用詞彙 (如 `滑鼠` 轉為 `鼠标`) |
| `S2HK` | 簡體到香港繁體 |
| `HK2S` | 香港繁體到簡體 |
| `T2TW` | 繁體到台灣正體 |
| `TW2T` | 台灣正體到繁體 |
| `T2HK` | 繁體到香港繁體 |
| `HK2T` | 香港繁體到繁體 |
| `T2JP` | 繁體 (舊字體) 到日文新字體 |
| `JP2T` | 日文新字體到繁體 (舊字體) |

帶 `P` 後綴的類型在逐字轉換之外還會進行詞彙替換, 使結果更符合當地表達習慣; 不帶 `P` 的類型只轉換字形, 不改動用詞.

`T2JP` 與 `JP2T` 在繁體舊字形與日文新字體 (Shinjitai) 之間轉換, 例如 `圖書館` 與 `図書館`; 它們處理的是漢字字形差異, 而非中文與日文之間的翻譯.

******

### 腳本方法

******

宿主側的 `opencc` 全局對象共提供 33 個方法: 通用方法 `convert`, 14 個核心快捷方法, 以及 18 個別名與組合方法. `convert(text, type)` 的 `type` 參數接受全部 32 個轉換名 (核心與組合均可), 不區分大小寫; 傳入未知類型會拋出 `Unknown OpenCC conversion type` 異常.

14 個核心快捷方法與上表的轉換類型一一對應, 每次調用執行一次插件轉換:

```text
s2t   t2s   s2tw  tw2s  s2twp  tw2sp  s2hk
hk2s  t2tw  tw2t  t2hk  hk2t   t2jp   jp2t
```

`s2twi` 與 `twi2s` 分別是 `s2twp` 與 `tw2sp` 的別名 (`twi` 表示 Taiwan idiom, 即台灣常用詞彙), 行為完全相同.

其餘 16 個組合方法由多次核心轉換按順序串聯而成, 用於沒有直達詞典的轉換方向:

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

組合方法的每一步都是一次獨立的插件調用, 例如 `twi2jp` 會依次執行 3 次轉換; 高頻循環或超長文本場景下, 優先使用核心類型可減少調用次數.

******

### 如何選擇安裝包

******

每個發行版本包含 5 個 APK, 差別僅在於內置了哪些處理器架構 (ABI) 的 OpenCC 原生庫:

| 安裝包 | 適用對象 |
|---|---|
| `arm64-v8a` | 絕大多數現代 Android 手機與平板 (64 位 ARM), 優先選擇 |
| `armeabi-v7a` | 較早期的 32 位 ARM 裝置 |
| `x86_64` | 64 位 x86 模擬器與少數 x86 裝置 |
| `x86` | 32 位 x86 模擬器與少數 x86 裝置 |
| `universal` | 內置全部 4 種架構, 體積最大; 適用於任何裝置, 也是不確定架構時的穩妥選擇 |

若誤裝了與裝置架構不匹配的單架構包, 插件將無法正常提供轉換服務, 換裝 `universal` 包即可解決.

******

### 快速自檢

******

確認插件已安裝並在插件中心處於啟用狀態後, 運行以下單行腳本即可完成端到端驗證:

```javascript
console.log(opencc.s2t("汉字转换"));
```

輸出 `漢字轉換` 即表示插件鏈路完整可用. 若腳本報錯, 請按提示排查: 提示缺少插件時安裝本插件; 提示未啟用或未授權時到插件中心開啟對應開關; 提示需要更高版本的宿主環境時升級 AutoJs6.

******

### 常見問題

******

#### 如何確認插件已經生效?

開啟 AutoJs6 的插件中心, 能看到 `OpenCC` 插件並處於啟用狀態即表示宿主已識別; 再運行上方 `快速自檢` 腳本, 輸出 `漢字轉換` 即為生效.

#### 為什麼應用程式列表裏沒有插件的圖示?

這是正常現象. 插件沒有獨立介面, 也不在桌面建立啟動圖示, 安裝後由 AutoJs6 在背景自動發現和調用, 全部互動都在 AutoJs6 內完成.

#### 腳本提示 `缺少 "OpenCC plugin" 所需的插件`, 怎麼辦?

這表示 AutoJs6 未在裝置上發現本插件. 安裝插件後再次運行腳本即可, 無需重啟 AutoJs6; 若已安裝仍提示缺失, 請確認插件未被系統或安全軟件卸載, 並檢查插件中心的啟用與授權狀態.

#### `s2tw` 和 `s2twp` (`s2twi`) 有什麼區別?

`s2tw` 只做字形轉換 (如 `软` 轉為 `軟`), 不改動用詞; `s2twp` 在此基礎上還會把大陸用詞替換為台灣常用詞彙 (如 `软件` 轉為 `軟體`, `鼠标` 轉為 `滑鼠`), `s2twi` 是它的別名. 面向台灣讀者的正式文本通常選 `s2twp`, 只需統一字形時選 `s2tw`.

#### 為什麼 Node.js 引擎的腳本裏無法使用 `opencc`?

`opencc` 目前是 Rhino (AutoJs6 預設 JavaScript 引擎) 專屬的全局對象, Node.js 運行時暫未提供對應實現. 相關支援計劃可關注 [ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md).

#### 轉換需要連線嗎? 長文本會不會很慢?

不需要連線, 全部轉換基於插件內置的 OpenCC 詞典在本地完成. 每次方法調用對應一次跨進程通訊, 單次轉換較長文本通常一次往返即可; 高頻循環調用時建議優先使用核心類型, 避免組合方法帶來的多次往返.

#### 插件會申請哪些權限? 數據安全嗎?

插件僅聲明用於與 AutoJs6 通訊的插件權限, 不申請網絡, 儲存空間等任何敏感系統權限; 服務本身也受同一權限保護, 其他應用程式無法調用. 待轉換的文本只在裝置記憶體中處理, 不會被儲存或上傳.

******

### 權限與安全

******

插件與 AutoJs6 之間通過 Android 系統的權限與簽名機制建立信任:

- 最小權限: 插件清單僅聲明 `org.autojs.permission.PLUGIN` 插件權限, 不含網絡, 儲存空間, 相機等任何敏感系統權限.
- 雙向防護: 插件服務同樣受該權限保護, 只有持有插件權限的宿主 (如 AutoJs6) 才能綁定與調用, 其他應用程式無法存取.
- 簽名授權: AutoJs6 會校驗插件簽名, 官方發佈包自動獲得授權; 非官方簽名的構建需在插件中心手動授權後才會被載入.
- 本地處理: 轉換完全在裝置本地完成, 插件不連線, 不寫入儲存空間, 不收集任何用戶數據.

請僅從官方 [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) 頁面或 AutoJs6 插件中心獲取插件. 來源不明的安裝包即使版本號相同, 也可能無法通過宿主校驗或暗藏風險.

******

### 插件介面

******

以下資訊面向 AutoJs6 宿主與插件開發者, 宿主通過這些標識發現插件並完成兼容性協商:

```text
application id: io.github.supermonster003.autojs6.plugin.opencc
plugin id: opencc
engine: opencc
variant: default
service action: org.autojs.plugin.OPENCC
service category: opencc
aidl interface: org.autojs.plugin.opencc.api.IOpenccPlugin
aidl methods: getInfo(), convert(text, conversionType)
minimum host build: 3923 (6.7.1 Alpha4)
conversion library: com.github.brooklet:android-opencc:1.2.2
```

`OpenccPluginService` 響應 `org.autojs.plugin.OPENCC` action (category `opencc`), Binder 介面為 opencc-api 的 `org.autojs.plugin.opencc.api.IOpenccPlugin`, 僅含 `getInfo()` 與 `convert(text, conversionType)` 兩個方法; 另提供 `WakeActivity` 供宿主喚醒插件進程.

`PluginInfo.supportedAbis` 上報 `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86` 四種架構, 供宿主與插件中心識別可用變體; 轉換由 `com.github.brooklet:android-opencc:1.2.2` 提供的 OpenCC 引擎與詞典完成.

******

### 開發路線圖

******

插件的能力規劃與完成情況以可勾選清單維護在 ROADMAP.md 中, 按里程碑組織並附驗收條件, 涵蓋文件與發佈體驗, 工程化與持續整合, 轉換能力增強與運行時演進等方向. 未勾選條目表示規劃意向而非目前版本能力, 歡迎通過 Issues 參與討論.

- [查看 ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md)

******

### 發行歷史

******

#### v1.0.2

_2026/08/31_

- `提示` 此版本只優化文檔與構建流程, OpenCC 轉換行為及 14 種核心轉換類型維持不變
- `優化` 重構 10 種語言的 README, 新增安裝步驟, 選包指南, 快速自檢, 33 個腳本方法清單, 常見問題及權限安全說明
- `優化` 將插件中心使用說明納入同一套多語言 JSON 生成鏈路, 讓 README, CHANGELOG 及 Android 資源由單一來源同步生成
- `優化` 強化文檔校驗腳本並接入 GitHub Actions, 自動檢測跨語言結構不一致, 生成產物漂移, 孤立檔案, 版本不對齊及殘留佔位符
- `優化` 新增 ROADMAP.md, 以可驗收的里程碑清單公開維護文檔, 工程化, 轉換能力及運行時演進計劃
- `優化` 將 Gradle 構建配置遷移至 `org.autojs.build.platform-versions` 1.4.1, 並透過 foojay 自動解析 JDK, 簡化及統一構建環境

#### v1.0.1

_2026/07/14_

- `優化` 提供按處理器架構 (ABI) 拆分的安裝包: `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86` 單架構包與包含全部架構的 `universal` 包, 裝置按需安裝, 體積更小
- `優化` 插件資訊上報支援的 ABI 列表, AutoJs6 與插件中心可據此識別目前裝置可用的插件變體
- `優化` 發佈 APK 檔案名附帶版本號, 架構與 CRC32 校驗碼, 便於核對下載檔案的完整性

#### v1.0.0

_2026/07/14_

- `新增` 首個正式版本: 以獨立插件形式為 AutoJs6 提供 OpenCC 中文轉換能力, 插件 ID 與引擎均為 `opencc`
- `新增` AutoJs6 通過 `org.autojs.plugin.OPENCC` 自動發現並調用插件, 安裝即用, 無需配置與重啟
- `新增` 支援全部 14 種 OpenCC 標準轉換類型, 覆蓋簡繁轉換, 香港/台灣地區用字與日文新字體: `S2T`/`S2TW`/`S2TWP`/`S2HK`/`T2S`/`T2TW`/`T2HK`/`T2JP`/`TW2S`/`TW2T`/`TW2SP`/`HK2S`/`HK2T`/`JP2T`
- `新增` 插件資訊與使用說明提供 10 種語言的本地化資源: 簡體中文, 香港繁體, 台灣繁體, 英語, 法語, 西班牙語, 日語, 韓語, 俄語, 阿拉伯語
- `新增` 提供多語言 README, 包含用法示例, 構建說明與相關連結

##### 更多發行歷史可參閱

* [CHANGELOG.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/assets/doc/CHANGELOG-zh-Hant-HK.md)

******

### 構建與校驗

******

本節面向希望從源代碼構建插件的開發者; 普通用戶直接安裝 Releases 頁面的成品 APK 即可.

構建 debug APK:

```powershell
.\gradlew.bat :app:assembleDebug
```

構建 release APK; 在不提交到版本庫的 `sign.properties` 中配置簽名身份後自動簽名, 未配置簽名時產物不可發佈:

```powershell
.\gradlew.bat :app:assembleRelease
```

歸集發佈產物並在檔案名中附加版本號, 架構與 CRC32 校驗碼:

```powershell
.\gradlew.bat :app:appendDigestToReleasedFiles
```

校驗多語言文件源與生成產物是否同步 (持續整合亦會執行):

```powershell
py .python\generate_markdown.py --check
```

構建需要 JDK 17 及以上與 Android SDK 36; Gradle 與各插件版本由 `version.properties` 及 `org.autojs.build.platform-versions` 統一管理.

******

### 本地化與文件生成

******

```text
.readme/common.json
.readme/lang_*.json
.readme/template_readme.md
.readme/template_plugin_instruction.md
.changelog/lang_*.json
.changelog/template_changelog.md
.python/generate_markdown.py
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
app/src/main/res/raw-*/plugin_instruction.md
```

`strings.xml` 提供本地化插件描述與錯誤資訊, `plugin_instruction.md` 提供宿主插件中心內展示的使用說明. README 與更新日誌一律修改 `.readme/` 與 `.changelog/` 下的 JSON 源文件, 再運行 `py .python/generate_markdown.py` 重新生成, 生成產物不手工編輯; 運行 `py .python/generate_markdown.py --check` 可校驗源文件與生成產物是否同步.

******

### 許可

******

項目代碼使用 [Mozilla Public License 2.0](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE). 中文轉換能力來自 [OpenCC](https://github.com/BYVoid/OpenCC) (Apache License 2.0) 及其 Android 封裝 [android-opencc](https://github.com/qichuan/android-opencc).

******

### 相關連結

******

- AutoJs6 OpenCC 文件: https://docs.autojs6.com/#/opencc
- AutoJs6 項目: https://github.com/SuperMonster003/AutoJs6
- OpenCC 官方項目: https://github.com/BYVoid/OpenCC
- Android OpenCC 項目: https://github.com/qichuan/android-opencc
