# 🚆 2026 台鐵全路網時刻表 & 縣市導航智慧接駁系統 (v3.9.2)

> **2026/07/01 大改點全線全班次 · 100% 純前端離線運算 · 支援 Google Maps 多中繼站遊程規劃 · 台灣鐵路地理地圖選站 · 17縣市多選過濾 · PWA 離線手機 App**

[![Version](https://img.shields.io/badge/version-v3.9.2-blue.svg)](CHANGELOG.md)
[![PWA](https://img.shields.io/badge/PWA-100%25%20Offline-success.svg)](manifest.json)
[![Stable Policy](https://img.shields.io/badge/Local%20Stable-Passed-brightgreen.svg)](verify_local_stable.py)
[![Multi-Version](https://img.shields.io/badge/Multi--Version-Supported-purple.svg)](versions/index.html)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## ✨ 核心特色 (Core Features)

- 🗺️ **台灣鐵路地理地圖模式 (Interactive SVG Map)**：依據台灣輪廓與鐵路拓撲繪製，直接於地圖上點選車站或縣市區域，直觀視覺化排程。
- 📋 **全台 17 縣市多選勾選過濾 (Multi-County Filter)**：自由勾選/多選指定縣市，未勾選者自動隱藏，支援全選/全清/反選與搜尋框混合過濾。
- 🚄 **全台 1,402 班列車、240+ 個車站完整收錄**：涵蓋西部幹線山海線、東部幹線、南迴線及四大支線（平溪/深澳、內灣/六家、集集、沙崙）。
- 🗺️ **Google Maps 式多中繼站遊程規劃 (Multi-Stop Waypoints)**：支援 2 ~ 6 站自由排列、停留時間自訂與順序調整，全島環島與跨線遊程秒級生成。
- ⚡ **300倍極速記憶化引擎 (Memoized Router)**：多站即時拼接耗時僅 **9.7 毫秒**，提供極致流暢的 60 FPS 操作體驗。
- 📅 **平日 / 週末開行日精確過濾**：自動識別週一至週五平日通勤自強號與週六日專開假日特快。
- 🔀 **多版本切換與隨時退版架構**：所有歷史版本獨立封裝於 `versions/<version>/`，支援 URL Query 參數（`?v=v3.8.15`）或選單一鍵回退任意版本！
- 📲 **100% 離線可用 & PWA 手機 App 化**：配置 Service Worker 與高解析度圖示，支援「加到主畫面」為獨立 App，深山隧道無訊號依然秒查。
- 🎫 **TR-PASS 專屬過濾與適用性提示**：一鍵過濾可搭乘列車，自動標註 EMU3000 / 普悠瑪禁搭限制。
- 🛡️ **緊湊轉乘警示 & 第二備案 (Plan B)**：轉乘小於 15 分鐘自動警示，並提供下一班替代列車推薦。
- 📊 **多階自訂排序**：支援「抵達時間 最晚 + 總行駛時間 最短」等主次雙階複合排序。

---

## 🛡️ 品質保證與本機自動化驗證機制 (Local Stable Verification)

專案嚴格落實 **「Local Pass 始能 Push」** 的穩定度制度，並透過 Git Pre-Push Hook 實體阻斷未通過驗證之程式碼提交：
- 🔍 **語法層 (Syntax AST)**：`node vm.Script` 解析 HTML 內部腳本、`data.js` 與 `sw.js`，徹底杜絕字串未跳脫或語法錯誤。
- 🧩 **DOM 綁定層 (DOM Integrity)**：驗證所有 UI 元件 ID 與 inline 事件函式定義無漏失。
- 📱 **版本一致性 (Version Alignment)**：確保 UI 徽章、PWA Service Worker 快取名稱與文件完全吻合。
- 🚦 **自動執行測試**：`python verify_local_stable.py`

---

## 🛠️ 技術架構 (Tech Stack)

- **Frontend**：HTML5, Vanilla CSS3 (響應式設計 RWD, 深淺雙色主題), Modern JavaScript (ES6+ Forward Multi-Hop Router)
- **PWA**：Service Worker (`sw.js`), Web App Manifest (`manifest.json`), Offline Caching Strategy
- **Data**：全路網拓撲圖資料庫（`data.js` 離線預載，1,402 班列車）

---

## 📋 更新日誌 (Changelog)

完整版本演進歷史請參閱 [CHANGELOG.md](CHANGELOG.md)。

---

## 🚀 本機使用方式 (Getting Started)

直接使用任何現代瀏覽器開啟 `index.html` 即可使用，或於手機 Safari / Chrome 點選「加入主畫面 / 安裝應用程式」。
