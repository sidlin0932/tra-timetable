# 🚆 2026 台鐵全路網時刻表 & 縣市導航智慧接駁系統 (v3.8.8)

> **2026/07/01 大改點全線全班次 · 100% 純前端離線運算 · 支援 Google Maps 多中繼站遊程規劃 · PWA 離線手機 App**

[![Version](https://img.shields.io/badge/version-v3.8.8-blue.svg)](CHANGELOG.md)
[![PWA](https://img.shields.io/badge/PWA-100%25%20Offline-success.svg)](manifest.json)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## ✨ 核心特色 (Core Features)

- 🚄 **全台 1,402 班列車、240+ 個車站完整收錄**：涵蓋西部幹線、東部幹線、南迴線及四大支線（平溪/深澳、內灣/六家、集集、沙崙）。
- 🗺️ **Google Maps 式多中繼站遊程規劃 (Multi-Stop Waypoints)**：支援 2 ~ 6 站自由排列、停留時間自訂與順序調整，全島環島與跨線遊程秒級生成。
- ⚡ **300倍極速記憶化引擎 (Memoized Router)**：多站即時拼接耗時僅 **9.7 毫秒**，提供極致流暢的 60 FPS 操作體驗。
- 📅 **平日 / 週末開行日精確過濾**：自動識別週一至週五平日通勤自強號與週六日專開假日特快。
- 📲 **100% 離線可用 & PWA 手機 App 化**：配置 Service Worker 與高解析度圖示，支援「加到主畫面」為獨立 App，深山隧道無訊號依然秒查。
- 🎫 **TR-PASS 專屬過濾與適用性提示**：一鍵過濾可搭乘列車，自動標註 EMU3000 / 普悠瑪禁搭限制。
- 🛡️ **緊湊轉乘警示 & 第二備案 (Plan B)**：轉乘小於 15 分鐘自動警示，並提供下一班替代列車推薦。
- 📊 **多階自訂排序**：支援「抵達時間 最晚 + 總行駛時間 最短」等主次雙階複合排序。

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
