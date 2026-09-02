<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>
    <picture>
      <source srcset="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap-night/ic_launcher.png?raw=true" media="(prefers-color-scheme: dark)" />
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/app/src/main/res/mipmap/ic_launcher.png?raw=true" alt="autojs6-plugin-opencc-ic-launcher" border="0" width="128" />
    </picture>
  </p>

  <p>可獨立使用並相容 AutoJs6 的離線 OpenCC 中文轉換器</p>

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

OpenCC 只需安裝一個 APK, 即可透過兩種入口使用基於 [OpenCC](https://github.com/BYVoid/OpenCC) 的中文文字轉換: 直接從桌面啟動完全離線的 Android App, 或讓 AutoJs6 將同一個 APK 識別為外掛並在腳本中使用全域物件 `opencc`. 兩條路徑都涵蓋簡體, 通用繁體, 香港繁體, 台灣正體與日文新字體.

獨立編輯器與受權限保護的 AutoJs6 Binder 服務共用唯一的官方 OpenCC 引擎, 同一組固定詞典, 快取, 轉換類型和錯誤模型. 獨立 App 不要求安裝 AutoJs6; 外掛模式則保持現有腳本 API, 並允許轉換引擎獨立於主程式更新.

******

### 功能亮點

******

- 一個 APK, 兩種用法: 無需 AutoJs6 即可從桌面圖示進入視覺化轉換頁面, 也可讓 AutoJs6 腳本透過同一次安裝呼叫 `opencc`.
- 14 種標準轉換: 涵蓋 OpenCC 的簡繁轉換, 香港/台灣地區用字轉換與日文新字體轉換, 並支援台灣常用詞彙轉換 (如 `软件` 與 `軟體` 的互換).
- 33 個腳本方法: 除通用的 `opencc.convert(text, type)` 外, 每種轉換類型都有同名快捷方法, 還提供 `s2jp`, `tw2hk` 等 18 個別名與組合方法.
- 完全離線: 轉換基於外掛內建詞典在裝置本機完成, 外掛不申請網路權限, 不收集任何資料.
- 依需求選擇套件: 提供 4 種單一架構安裝套件與包含全部架構的 `universal` 套件, 裝置只需安裝相符的套件, 體積更小.
- 多語言: 獨立 UI, 外掛資訊, 使用說明, README 與更新日誌涵蓋 10 種語言.
- 共用後端: 編輯器與輕量外掛服務重用同一份已驗證資源和原生引擎, 外掛連線閒置時自動釋放.

******

### 介面截圖

******

以下均為未經修飾的 Android 實際執行畫面, 依序展示日間模式獨立編輯器, 170% 字型下的阿拉伯語 RTL 夜間版面, 以及原有 AutoJs6 外掛中心入口.

<table>
  <tr>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/standalone-phone-light.png?raw=true"
           alt="日間主題下的獨立離線轉換" width="280" />
      <br />
      <sub>日間主題下的獨立離線轉換</sub>
    </td>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/standalone-rtl-large-dark.png?raw=true"
           alt="夜間主題, 170% 字型下的阿拉伯語 RTL 版面" width="280" />
      <br />
      <sub>夜間主題, 170% 字型下的阿拉伯語 RTL 版面</sub>
    </td>
    <td align="center">
      <img src="https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/docs/images/screenshots/plugin-center-enabled.png?raw=true"
           alt="外掛中心已識別並啟用 OpenCC 1.0.2" width="280" />
      <br />
      <sub>外掛中心已識別並啟用 OpenCC 1.0.2</sub>
    </td>
  </tr>
</table>

******

### 使用方法

******

1. 從 [Releases](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/releases) 頁面或 AutoJs6 外掛中心下載並安裝一個 APK. 選擇與裝置 ABI 相符的安裝套件; 不確定時選擇 `universal`, 或參考下方 `如何選擇安裝套件`.
2. 獨立使用時, 從桌面啟動 `OpenCC`, 輸入或主動貼上文字, 選擇 14 種轉換類型之一並點選 `轉換`. 此路徑不要求安裝 AutoJs6, 也不要求使用者授予外掛權限.
3. 作為外掛使用時, 將 AutoJs6 升級到內部版本號 3923 (6.7.1 Alpha4) 及以上; 6.8.0 正式版及更新版本均符合要求.
4. 開啟 AutoJs6 外掛中心, 確認 `OpenCC` 已被識別並處於啟用狀態. 官方發布套件會自動通過簽章驗證, 無需手動授權.
5. 在腳本中直接使用 `opencc` 全域物件, 例如 `opencc.s2t("汉字")`; 無需 require, import 或重新啟動主程式.

> 兩種模式都支援 Android 7.0 (API 24) 及以上裝置. 最低 AutoJs6 版本只約束外掛腳本, 獨立 App 不依賴主程式. 若腳本提示缺少外掛或主程式版本過低, 請參考下方 `常見問題`.

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

支援擴充契約的新版主程式會將整條組合鏈作為一次外掛呼叫; 例如 `twi2jp` 的 3 個轉換階段只需 1 次 Binder 往返. 舊版主程式仍按階段呼叫, 與本外掛保持相容.

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

#### 不安裝 AutoJs6 也可以使用 OpenCC 嗎?

可以. 從桌面開啟 `OpenCC` 圖示即可在完全離線的編輯器中轉換文字. 只有腳本透過全域物件 `opencc` 呼叫外掛時才需要 AutoJs6; 兩種模式來自同一個 APK.

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

獨立 App 與 AutoJs6 外掛入口具有相互分離且明確的安全邊界:

- 最小權限: 資訊清單只宣告用於整合的 `org.autojs.permission.PLUGIN`, 不含網路, 儲存空間, 相機等敏感系統權限; 獨立使用者無需授予外掛權限.
- 明確編輯操作: Launcher 不接收外部分享文字或 URI, 只有點選 `貼上` 才讀取剪貼簿, 只有點選 `分享` 才開啟系統分享面板.
- 受保護的外掛服務: 只有持有外掛權限的主程式 (如 AutoJs6) 才能繫結呼叫, AutoJs6 還會驗證安裝套件簽章; 其他應用程式無法呼叫服務.
- 本機處理: 兩種入口都使用內建詞典完全離線轉換. 輸入和結果不會記錄日誌, 持久化, 備份, 上傳或收集.

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
aidl contract version: 2
aidl methods: getInfo(), convert(text, conversionType), getSupportedConversionTypes(), convertBatch(texts, conversionType), convertChain(text, conversionTypes)
batch/chain limits: 1024 texts / 32 stages
minimum host build: 3923 (6.7.1 Alpha4)
conversion backend: OpenCC 1.4.2 (ver.1.4.2)
OpenCC source commit: 025f371dc76b598d77384fbdab90c937471844d8
OpenCC resources SHA-256: 9ea0d303219b34d014d5c116677b5d325043beafb2c8a62ee889ca67f4d054a5
```

`OpenccPluginService` 會回應 `org.autojs.plugin.OPENCC` action (category `opencc`), Binder 介面為 opencc-api 的 `org.autojs.plugin.opencc.api.IOpenccPlugin`. 契約版本 2 在原有 `getInfo()` 與 `convert(text, conversionType)` 之後追加類型探索, 批次轉換與鏈式轉換方法, 並透過 `PluginInfo.capabilities` 公告版本與支援類型; 舊版主程式繼續使用原有方法和交易編號. 另提供 `WakeActivity` 供主程式喚醒外掛處理程序.

外掛直接建置固定在提交 `025f371dc76b598d77384fbdab90c937471844d8` 的官方 OpenCC `ver.1.4.2`, 並使用同一發行版的配套資源. 每個 ABI 僅包含一個靜態連結且按 16 KB 對齊的 `libopencc_jni.so`, 轉換始終完全離線.

******

### 開發路線圖

******

外掛的能力規劃與完成情況以可勾選清單維護在 ROADMAP.md 中, 依里程碑組織並附驗收條件, 涵蓋文件與發布體驗, 工程化與持續整合, 轉換能力增強與執行環境演進等方向. 未勾選條目表示規劃意向而非目前版本能力, 歡迎透過 Issues 參與討論.

- [檢視 ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/ROADMAP.md)

******

### 發行歷史

******

#### v1.2.0

_2026/09/01_

- `提示` OpenCC 1.4.2 的詞典更新會有意改變少量結果, 包括 `复盘` -> `復盤`, `内卷` -> `內捲`, 保留 `什么怎么这么` 及 `内存条` -> `記憶體模組`; 完整審閱清單請見移轉報告
- `優化` 將官方 OpenCC 1.4.2 及同版本詞典直接建置為每個 ABI 一個靜態連結的 JNI 程式庫, 所有轉換繼續完全離線
- `優化` 使用 NDK 28.2, 16 KB ELF 與 ZIP 對齊及真實 16 KB 模擬器 Binder 驗證, 支援 16 KB 頁面大小裝置
- `優化` 以大小和 SHA-256 驗證原子安裝固定資源 ZIP, 支援損壞自動復原, Unicode 安全 JNI 轉換及熱路徑轉換器快取
- `相依性` 移除已停止維護的 `com.github.brooklet:android-opencc:1.2.2` 封裝程式庫, 並將官方 OpenCC `ver.1.4.2` 固定至提交 `025f371dc76b598d77384fbdab90c937471844d8`
- `相依性` 在 `THIRD_PARTY_NOTICES.md` 中記錄內建 OpenCC, Marisa Trie, Darts Clone 與 RapidJSON 的來源和授權

#### v1.1.0

_2026/09/01_

- `新增` 升級至 OpenCC 外掛契約版本 2, 新增 `getSupportedConversionTypes()`, 供新版主程式動態探索目前實際支援的 14 種轉換類型
- `新增` 新增 `convertBatch(texts, conversionType)`, 單次 Binder 往返最多轉換 1024 段文字, 同時保留舊版主程式逐項呼叫的相容路徑
- `新增` 新增 `convertChain(text, conversionTypes)`, 單次呼叫最多依序執行 32 個階段, 讓新版主程式的組合方法從最多 3 次 Binder 往返降至 1 次
- `優化` 透過 `PluginInfo.instruction` 提供呼叫方語言的外掛說明, 並透過 capabilities 回報契約版本與支援的轉換類型
- `優化` 保持原有 AIDL 方法及交易編號不變, 並為擴充呼叫, 舊契約回退, 大小上限與例外路徑補充單元測試和真實 Binder 測試
- `優化` 統一 README 版式與 Gradle 平台版本管理方式

#### v1.0.2

_2026/08/31_

- `提示` 此版本僅改善文件與建置流程, OpenCC 轉換行為及 14 種核心轉換類型維持不變
- `優化` 重構 10 種語言的 README, 新增安裝步驟, 套件選擇指南, 快速自我檢查, 33 個腳本方法清單, 常見問題與權限安全說明
- `優化` 將外掛中心使用說明納入同一套多語言 JSON 產生流程, 讓 README, CHANGELOG 與 Android 資源由單一來源同步產生
- `優化` 強化文件檢查腳本並接入 GitHub Actions, 自動偵測跨語言結構不一致, 產生物漂移, 孤立檔案, 版本未對齊與殘留預留位置標記
- `優化` 新增 ROADMAP.md, 以可驗收的里程碑清單公開維護文件, 工程化, 轉換能力與執行階段演進計畫
- `優化` 將 Gradle 建置設定遷移至 `org.autojs.build.platform-versions` 1.4.1, 並透過 foojay 自動解析 JDK, 簡化並統一建置環境

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

執行 JVM 單元測試並建置 instrumentation 測試 APK:

```powershell
.\gradlew.bat :app:testDebugUnitTest :app:assembleDebugAndroidTest
```

建置 release APK:

```powershell
.\gradlew.bat :app:assembleRelease
```

彙整發布產物並在檔名中附加版本號, 架構與 CRC32 檢查碼:

```powershell
.\gradlew.bat :app:appendDigestToReleasedFiles
```

建置 release APK 並準備校驗和與發行說明:

```powershell
py scripts\release\prepare_release.py
```

驗證多語言文件來源檔與產生產物是否同步 (持續整合也會執行):

```powershell
py .python\generate_markdown.py --check
```

建置需要 JDK 17 及以上與 Android SDK 36; Gradle 與各外掛版本由 `version.properties` 及 `io.github.supermonster003.autojs6-platform-versions` 統一管理.

******

### 在地化與文件產生

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

`.readme/android_strings.json` 是獨立 UI 與服務錯誤文案的單一來源, 各語言 JSON 則提供 README 和外掛中心文案. 一律修改 `.readme/` 與 `.changelog/` 下的 JSON 來源檔案, 再執行 `py .python/generate_markdown.py`; 產生的 `strings.xml`, `plugin_instruction.md`, README 和更新日誌都不手動編輯. `--check` 會驗證全部 47 個產生產物.

******

### 授權

******

專案程式碼採用 [Mozilla Public License 2.0](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/LICENSE). 中文轉換能力直接來自 [OpenCC](https://github.com/BYVoid/OpenCC) (Apache License 2.0); 內建 OpenCC, Marisa Trie, Darts Clone 與 RapidJSON 的來源和授權請見[第三方聲明](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/THIRD_PARTY_NOTICES.md).

******

### 相關連結

******

- AutoJs6 OpenCC 文件: https://docs.autojs6.com/#/opencc
- AutoJs6 專案: https://github.com/SuperMonster003/AutoJs6
- OpenCC 官方專案: https://github.com/BYVoid/OpenCC
- 第三方聲明: https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC/blob/master/THIRD_PARTY_NOTICES.md
