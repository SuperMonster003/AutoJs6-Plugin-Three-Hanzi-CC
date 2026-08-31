<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>用於中文文字轉換的 OpenCC 外掛</p>

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
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/.readme/README-zh-Hant-HK.md)
- 繁體中文 (台灣) [zh-Hant-TW] # 目前
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

OpenCC 外掛 (OpenCC Plugin) 為 AutoJs6 提供基於 [OpenCC](https://github.com/BYVoid/OpenCC) 的中文文字轉換能力. 安裝本外掛後, AutoJs6 腳本中的全域物件 `opencc` 即可正常運作, 一行程式碼即可在簡體, 繁體, 香港繁體, 台灣正體與日文新字體之間完成轉換, 無需匯入模組, 無需連線.

外掛採用主程式與外掛分工的設計: AutoJs6 主程式提供腳本直接呼叫的 `opencc` API, 外掛以獨立應用程式的形式攜帶 OpenCC 轉換引擎與詞典. 從 AutoJs6 6.8.0 起主程式不再內建 OpenCC 執行環境, 中文轉換功能由本外掛視需要提供; 這樣主程式安裝套件保持精簡, 轉換引擎也可以獨立於主程式更新.

******

### 功能亮點

******

- 開箱即用: 外掛安裝到裝置後由 AutoJs6 自動發現, 無需重新啟動主程式, 無需任何設定, 腳本即可直接呼叫 `opencc` 全域物件.
- 14 種標準轉換: 涵蓋 OpenCC 的簡繁轉換, 香港/台灣地區用字轉換與日文新字體轉換, 並支援台灣常用詞彙轉換 (如 `软件` 與 `軟體` 的互換).
- 33 個腳本方法: 除通用的 `opencc.convert(text, type)` 外, 每種轉換類型都有同名快捷方法, 還提供 `s2jp`, `tw2hk` 等 18 個別名與組合方法.
- 完全離線: 轉換基於外掛內建詞典在裝置本機完成, 外掛不申請網路權限, 不收集任何資料.
- 依需求選擇套件: 提供 4 種單一架構安裝套件與包含全部架構的 `universal` 套件, 裝置只需安裝相符的套件, 體積更小.
- 多語言: 外掛資訊, 使用說明, README 與更新日誌涵蓋 10 種語言.
- 輕量背景服務: 外掛無獨立介面, 由主程式視需要喚醒與繫結, 閒置時自動釋放連線.

******

### 介面截圖

******

以下為 AutoJs6 外掛中心的實際執行畫面. OpenCC 1.0.2 (17) 已由宿主識別, 右側開關處於啟用狀態. 畫面保留原始 Android 截圖, 未經裁切或調色.

<table>
  <tr>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/plugin-center-enabled.png?raw=true"
           alt="外掛中心已識別並啟用 OpenCC 1.0.2" width="360" />
      <br />
      <sub>外掛中心已識別並啟用 OpenCC 1.0.2</sub>
    </td>
  </tr>
</table>

******

### 使用方法

******

1. 將 AutoJs6 升級到內部版本號 3923 (6.7.1 Alpha4) 及以上; 6.8.0 正式版及更新版本均符合要求.
2. 從 [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) 頁面或 AutoJs6 外掛中心下載並安裝外掛 APK; 不確定該選哪個安裝套件時, 可直接選 `universal` 套件, 或參考下方 `如何選擇安裝套件`.
3. 開啟 AutoJs6 的外掛中心, 確認 `OpenCC` 外掛已被識別並處於啟用狀態; 官方發布套件會自動通過簽章驗證, 無需手動授權.
4. 在腳本中直接使用 `opencc` 全域物件, 例如 `opencc.s2t("汉字")`; 無需 require 或 import, 安裝外掛後也無需重新啟動 AutoJs6.

> 外掛支援 Android 7.0 (API 24) 及以上的裝置. 若腳本執行時提示缺少外掛或主程式版本過低, 請參考下方 `常見問題`.

******

### 快速上手

******

安裝完成後, 以下腳本可直接執行, 註解為預期輸出:

```javascript
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.t2jp("圖書館"));      // => 図書館
```

快捷方法與通用方法 `opencc.convert(text, type)` 等價; `opencc` 物件本身也可以作為函式呼叫, 轉換類型名稱不區分大小寫:

```javascript
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
console.log(opencc("汉字转换", "s2t"));         // => 漢字轉換
```

所有方法均同步回傳轉換後的字串, 轉換在本機詞典上完成, 不會產生任何網路請求.

******

### 轉換類型

******

`convert` 方法與同名快捷方法支援以下 14 種 OpenCC 標準轉換類型, 類型名稱中 S 表示簡體, T 表示繁體 (OpenCC 標準), HK 表示香港繁體, TW 表示台灣正體, JP 表示日文新字體:

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

帶 `P` 後綴的類型在逐字轉換之外還會進行詞彙替換, 使結果更符合當地表達習慣; 不帶 `P` 的類型只轉換字形, 不更動用詞.

`T2JP` 與 `JP2T` 在繁體舊字形與日文新字體 (Shinjitai) 之間轉換, 例如 `圖書館` 與 `図書館`; 它們處理的是漢字字形差異, 而非中文與日文之間的翻譯.

******

### 腳本方法

******

主程式端的 `opencc` 全域物件共提供 33 個方法: 通用方法 `convert`, 14 個核心快捷方法, 以及 18 個別名與組合方法. `convert(text, type)` 的 `type` 參數接受全部 32 個轉換名稱 (核心與組合均可), 不區分大小寫; 傳入未知類型會拋出 `Unknown OpenCC conversion type` 例外.

14 個核心快捷方法與上表的轉換類型一一對應, 每次呼叫執行一次外掛轉換:

```text
s2t   t2s   s2tw  tw2s  s2twp  tw2sp  s2hk
hk2s  t2tw  tw2t  t2hk  hk2t   t2jp   jp2t
```

`s2twi` 與 `twi2s` 分別是 `s2twp` 與 `tw2sp` 的別名 (`twi` 表示 Taiwan idiom, 即台灣常用詞彙), 行為完全相同.

其餘 16 個組合方法由多次核心轉換依序串聯而成, 用於沒有直達詞典的轉換方向:

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

組合方法的每一步都是一次獨立的外掛呼叫, 例如 `twi2jp` 會依序執行 3 次轉換; 高頻迴圈或超長文字的情境下, 優先使用核心類型可減少呼叫次數.

******

### 如何選擇安裝套件

******

每個發行版本包含 5 個 APK, 差別僅在於內建了哪些處理器架構 (ABI) 的 OpenCC 原生程式庫:

| 安裝套件 | 適用對象 |
|---|---|
| `arm64-v8a` | 絕大多數現代 Android 手機與平板 (64 位元 ARM), 優先選擇 |
| `armeabi-v7a` | 較早期的 32 位元 ARM 裝置 |
| `x86_64` | 64 位元 x86 模擬器與少數 x86 裝置 |
| `x86` | 32 位元 x86 模擬器與少數 x86 裝置 |
| `universal` | 內建全部 4 種架構, 體積最大; 適用於任何裝置, 也是不確定架構時的穩妥選擇 |

若誤裝了與裝置架構不相符的單一架構套件, 外掛將無法正常提供轉換服務, 改為安裝 `universal` 套件即可解決.

******

### 快速自我檢查

******

確認外掛已安裝並在外掛中心處於啟用狀態後, 執行以下單行腳本即可完成端對端驗證:

```javascript
console.log(opencc.s2t("汉字转换"));
```

輸出 `漢字轉換` 即表示外掛整體流程完整可用. 若腳本回報錯誤, 請按提示排查: 提示缺少外掛時安裝本外掛; 提示未啟用或未授權時到外掛中心開啟對應開關; 提示需要更高版本的主程式環境時升級 AutoJs6.

******

### 常見問題

******

#### 如何確認外掛已經生效?

開啟 AutoJs6 的外掛中心, 能看到 `OpenCC` 外掛並處於啟用狀態即表示主程式已識別; 再執行上方 `快速自我檢查` 腳本, 輸出 `漢字轉換` 即為生效.

#### 為什麼應用程式清單裡沒有外掛的圖示?

這是正常現象. 外掛沒有獨立介面, 也不會在桌面建立啟動圖示, 安裝後由 AutoJs6 在背景自動發現和呼叫, 全部互動都在 AutoJs6 內完成.

#### 腳本提示 `缺少 "OpenCC plugin" 所需的外掛`, 怎麼辦?

這表示 AutoJs6 未在裝置上發現本外掛. 安裝外掛後再次執行腳本即可, 無需重新啟動 AutoJs6; 若已安裝仍提示缺失, 請確認外掛未被系統或安全軟體解除安裝, 並檢查外掛中心的啟用與授權狀態.

#### `s2tw` 和 `s2twp` (`s2twi`) 有什麼差別?

`s2tw` 只做字形轉換 (如 `软` 轉為 `軟`), 不更動用詞; `s2twp` 在此基礎上還會把大陸用詞替換為台灣常用詞彙 (如 `软件` 轉為 `軟體`, `鼠标` 轉為 `滑鼠`), `s2twi` 是它的別名. 以台灣讀者為對象的正式文件通常選 `s2twp`, 只需要統一字形時選 `s2tw`.

#### 為什麼 Node.js 引擎的腳本裡無法使用 `opencc`?

`opencc` 目前是 Rhino (AutoJs6 預設 JavaScript 引擎) 專屬的全域物件, Node.js 執行環境尚未提供對應實作. 相關支援計畫可關注 [ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md).

#### 轉換需要連線嗎? 長文字會不會很慢?

不需要連線, 全部轉換基於外掛內建的 OpenCC 詞典在本機完成. 每次方法呼叫對應一次跨處理程序通訊, 單次轉換較長文字通常一次往返即可; 高頻迴圈呼叫時建議優先使用核心類型, 避免組合方法帶來的多次往返.

#### 外掛會申請哪些權限? 資料安全嗎?

外掛僅宣告用於與 AutoJs6 通訊的外掛權限, 不申請網路, 儲存空間等任何敏感系統權限; 服務本身也受同一權限保護, 其他應用程式無法呼叫. 待轉換的文字只在裝置記憶體中處理, 不會被儲存或上傳.

******

### 權限與安全

******

外掛與 AutoJs6 之間透過 Android 系統的權限與簽章機制建立信任:

- 最小權限: 外掛資訊清單僅宣告 `org.autojs.permission.PLUGIN` 外掛權限, 不含網路, 儲存空間, 相機等任何敏感系統權限.
- 雙向防護: 外掛服務同樣受該權限保護, 只有持有外掛權限的主程式 (如 AutoJs6) 才能繫結與呼叫, 其他應用程式無法存取.
- 簽章授權: AutoJs6 會驗證外掛簽章, 官方發布套件自動獲得授權; 非官方簽章的建置需在外掛中心手動授權後才會被載入.
- 本機處理: 轉換完全在裝置本機完成, 外掛不連線, 不寫入儲存空間, 不收集任何使用者資料.

請僅從官方 [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) 頁面或 AutoJs6 外掛中心取得外掛. 來源不明的安裝套件即使版本號相同, 也可能無法通過主程式驗證或暗藏風險.

******

### 外掛介面

******

以下資訊面向 AutoJs6 主程式與外掛開發者, 主程式透過這些識別資訊發現外掛並完成相容性協商:

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

`OpenccPluginService` 會回應 `org.autojs.plugin.OPENCC` action (category `opencc`), Binder 介面為 opencc-api 的 `org.autojs.plugin.opencc.api.IOpenccPlugin`, 僅含 `getInfo()` 與 `convert(text, conversionType)` 兩個方法; 另提供 `WakeActivity` 供主程式喚醒外掛處理程序.

`PluginInfo.supportedAbis` 回報 `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86` 四種架構, 供主程式與外掛中心識別可用變體; 轉換由 `com.github.brooklet:android-opencc:1.2.2` 提供的 OpenCC 引擎與詞典完成.

******

### 開發路線圖

******

外掛的能力規劃與完成情況以可勾選清單維護在 ROADMAP.md 中, 依里程碑組織並附驗收條件, 涵蓋文件與發布體驗, 工程化與持續整合, 轉換能力增強與執行環境演進等方向. 未勾選條目表示規劃意向而非目前版本能力, 歡迎透過 Issues 參與討論.

- [檢視 ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md)

******

### 發行歷史

******

#### v1.0.2

_2026/08/31_

- `提示` 此版本僅改善文件與建置流程, OpenCC 轉換行為及 14 種核心轉換類型維持不變
- `優化` 重構 10 種語言的 README, 新增安裝步驟, 套件選擇指南, 快速自我檢查, 33 個腳本方法清單, 常見問題與權限安全說明
- `優化` 將外掛中心使用說明納入同一套多語言 JSON 產生流程, 讓 README, CHANGELOG 與 Android 資源由單一來源同步產生
- `優化` 強化文件檢查腳本並接入 GitHub Actions, 自動偵測跨語言結構不一致, 產生物漂移, 孤立檔案, 版本未對齊與殘留預留位置標記
- `優化` 新增 ROADMAP.md, 以可驗收的里程碑清單公開維護文件, 工程化, 轉換能力與執行階段演進計畫
- `優化` 將 Gradle 建置設定遷移至 `org.autojs.build.platform-versions` 1.4.1, 並透過 foojay 自動解析 JDK, 簡化並統一建置環境

#### v1.0.1

_2026/07/14_

- `優化` 提供依處理器架構 (ABI) 拆分的安裝套件: `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86` 單一架構套件與包含全部架構的 `universal` 套件, 裝置依需求安裝, 體積更小
- `優化` 外掛資訊回報支援的 ABI 清單, AutoJs6 與外掛中心可據此識別目前裝置可用的外掛變體
- `優化` 發布 APK 檔名附帶版本號, 架構與 CRC32 檢查碼, 便於核對下載檔案的完整性

#### v1.0.0

_2026/07/14_

- `新增` 首個正式版本: 以獨立外掛形式為 AutoJs6 提供 OpenCC 中文轉換能力, 外掛 ID 與引擎均為 `opencc`
- `新增` AutoJs6 透過 `org.autojs.plugin.OPENCC` 自動發現並呼叫外掛, 安裝即用, 無需設定與重新啟動
- `新增` 支援全部 14 種 OpenCC 標準轉換類型, 涵蓋簡繁轉換, 香港/台灣地區用字與日文新字體: `S2T`/`S2TW`/`S2TWP`/`S2HK`/`T2S`/`T2TW`/`T2HK`/`T2JP`/`TW2S`/`TW2T`/`TW2SP`/`HK2S`/`HK2T`/`JP2T`
- `新增` 外掛資訊與使用說明提供 10 種語言的在地化資源: 簡體中文, 香港繁體, 台灣繁體, 英文, 法文, 西班牙文, 日文, 韓文, 俄文, 阿拉伯文
- `新增` 提供多語言 README, 包含用法範例, 建置說明與相關連結

##### 更多發行歷史可參閱

* [CHANGELOG.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/assets/doc/CHANGELOG-zh-Hant-TW.md)

******

### 建置與驗證

******

本節適用於希望從原始碼建置外掛的開發者; 一般使用者直接安裝 Releases 頁面的預先建置 APK 即可.

建置 debug APK:

```powershell
.\gradlew.bat :app:assembleDebug
```

建置 release APK; 在不納入版本控制的 `sign.properties` 中設定簽章身分後自動簽署, 未設定簽章時產物不可發布:

```powershell
.\gradlew.bat :app:assembleRelease
```

彙整發布產物並在檔名中附加版本號, 架構與 CRC32 檢查碼:

```powershell
.\gradlew.bat :app:appendDigestToReleasedFiles
```

驗證多語言文件來源檔與產生產物是否同步 (持續整合也會執行):

```powershell
py .python\generate_markdown.py --check
```

建置需要 JDK 17 及以上與 Android SDK 36; Gradle 與各外掛版本由 `version.properties` 及 `org.autojs.build.platform-versions` 統一管理.

******

### 在地化與文件產生

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

`strings.xml` 提供在地化的外掛描述與錯誤訊息, `plugin_instruction.md` 提供主程式外掛中心內顯示的使用說明. README 與更新日誌一律修改 `.readme/` 與 `.changelog/` 下的 JSON 來源檔案, 再執行 `py .python/generate_markdown.py` 重新產生, 產生產物不手動編輯; 執行 `py .python/generate_markdown.py --check` 可驗證來源檔案與產生產物是否同步.

******

### 授權

******

專案程式碼採用 [Mozilla Public License 2.0](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE). 中文轉換能力來自 [OpenCC](https://github.com/BYVoid/OpenCC) (Apache License 2.0) 及其 Android 封裝 [android-opencc](https://github.com/qichuan/android-opencc).

******

### 相關連結

******

- AutoJs6 OpenCC 文件: https://docs.autojs6.com/#/opencc
- AutoJs6 專案: https://github.com/SuperMonster003/AutoJs6
- OpenCC 官方專案: https://github.com/BYVoid/OpenCC
- Android OpenCC 專案: https://github.com/qichuan/android-opencc
