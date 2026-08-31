OpenCC 外掛 (OpenCC Plugin) 為 AutoJs6 提供基於 [OpenCC](https://github.com/BYVoid/OpenCC) 的中文文字轉換能力. 安裝本外掛後, AutoJs6 腳本中的全域物件 `opencc` 即可正常運作, 一行程式碼即可在簡體, 繁體, 香港繁體, 台灣正體與日文新字體之間完成轉換, 無需匯入模組, 無需連線.

### 快速上手

安裝完成後, 以下腳本可直接執行, 註解為預期輸出:

```javascript
console.log(opencc.s2t("汉字转换"));     // => 漢字轉換
console.log(opencc.t2s("漢字轉換"));     // => 汉字转换
console.log(opencc.s2twp("鼠标和软件")); // => 滑鼠和軟體
console.log(opencc.convert("汉字转换", "S2T")); // => 漢字轉換
```

### 轉換類型

`convert` 方法與同名快捷方法支援以下 14 種 OpenCC 標準轉換類型, 類型名稱中 S 表示簡體, T 表示繁體 (OpenCC 標準), HK 表示香港繁體, TW 表示台灣正體, JP 表示日文新字體:

```text
S2T   T2S   S2TW  TW2S  S2TWP  TW2SP  S2HK
HK2S  T2TW  TW2T  T2HK  HK2T   T2JP   JP2T
```

帶 `P` 後綴的類型在逐字轉換之外還會進行詞彙替換, 使結果更符合當地表達習慣; 不帶 `P` 的類型只轉換字形, 不更動用詞.

### 快速自我檢查

確認外掛已安裝並在外掛中心處於啟用狀態後, 執行以下單行腳本即可完成端對端驗證:

```javascript
console.log(opencc.s2t("汉字转换"));
```

輸出 `漢字轉換` 即表示外掛整體流程完整可用. 若腳本回報錯誤, 請按提示排查: 提示缺少外掛時安裝本外掛; 提示未啟用或未授權時到外掛中心開啟對應開關; 提示需要更高版本的主程式環境時升級 AutoJs6.

更多方法與完整轉換類型說明請參閱 [AutoJs6 OpenCC 文件](https://docs.autojs6.com/#/opencc) 與 [專案 README](https://github.com/SuperMonster003/AutoJs6-Plugin-OpenCC).
