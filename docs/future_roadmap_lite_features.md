# 🚆 2026 台鐵時刻表 · 極速極簡版 (SuperLite) 未來演進與架構研究方案

本文檔針對使用者反饋之三大關鍵功能進行架構設計與程式碼藍圖規劃，供後續版本升級即時引用。

---

## 📌 一、 出發時間與全天候查詢優化 (Time & All-Day Filter)

### 1. 現狀分析
- 目前 `lite.html` 預設時間欄位值為 `00:00`，因此預設顯示清晨首班車。
- 點擊「🕒 現在」按鈕可填入當前時間，但對使用者而言應**預設為當前時間**或提供**全天 (00:00~23:59)** 快捷切換。

### 2. 演進方案
```javascript
// 頁面載入時預設以目前時間（或選擇全日查詢）
function initDefaultTime() {
    const d = new Date();
    const h = String(d.getHours()).padStart(2, '0');
    const m = String(d.getMinutes()).padStart(2, '0');
    document.getElementById('timeInput').value = `${h}:${m}`;
}
```
- 加入「全天」核取方塊／按鈕：當勾選「全天查詢」時，`startMin = 0`，列出全日所有班次。

---

## 📌 二、 多維度排序系統 (Multi-Criteria Sorting)

### 1. 現狀分析
- 目前預設依「最早抵達時間 (`arrMin`) ➔ 最短車程 (`duration`)」自動排序。
- 使用者需要自訂排序選項（最快到達、最早出發、耗時最短、最少轉乘）。

### 2. 演進方案
在篩選控制列新增 `<select id="sortFilter">`：
- `arrAsc`: 🏁 最早抵達（預設，趕時間首選）
- `depAsc`: 🚩 最早出發（依序發車）
- `durAsc`: ⏱️ 行車時間最短（直達特快優先）
- `transAsc`: 🔄 轉乘次數最少（直達優先）

```javascript
function sortRoutes(routes, sortMode) {
    if (sortMode === 'arrAsc') {
        return routes.sort((a, b) => a.arrMin - b.arrMin || a.duration - b.duration);
    } else if (sortMode === 'depAsc') {
        return routes.sort((a, b) => a.depMin - b.depMin || a.arrMin - b.arrMin);
    } else if (sortMode === 'durAsc') {
        return routes.sort((a, b) => a.duration - b.duration || a.arrMin - b.arrMin);
    } else if (sortMode === 'transAsc') {
        return routes.sort((a, b) => a.transfers - b.transfers || a.arrMin - b.arrMin);
    }
    return routes;
}
```

---

## 📌 三、 車次直查系統 (Search by Train Number)

### 1. 功能定義
- 使用者可在頂部或專屬輸入框輸入車次代號（例如 `4154`、`229`、`154`、`EMU3000`）。
- 0.1ms 內立即調出該車次的：
  1. 車種名稱（自強號、區間快、普悠瑪...）
  2. 起訖起終點與行駛方向（順行/逆行）
  3. 開行日備註（每日行駛、週五至日行駛...）
  4. 完整沿途停靠站與各站到發時刻表

### 2. 核心查表演算法
```javascript
// 車次字典快速索引（初始化建置 O(N)，查詢 O(1) 0.05ms）
let trainByNumber = {};
function indexTrainsByNumber() {
    trainByNumber = {};
    timetableData.forEach(t => {
        trainByNumber[String(t.train_number)] = t;
    });
}

function lookupTrain(trainNo) {
    const t = trainByNumber[String(trainNo).trim()];
    if (!t) return null;
    return {
        trainNo: t.train_number,
        trainType: t.train_type,
        startStation: t.start_station,
        endStation: t.end_station,
        dir: t.direction,
        notes: t.notes || '每日行駛',
        stops: t.stops // [{station: '樹林', time: '05:30'}, ...]
    };
}
```

---

## 📌 四、 下階段實裝效益評估

| 功能 | 運算時間 | 記憶體增量 | 使用者體驗躍升 |
| :--- | :--- | :--- | :--- |
| **預設當前時間 + 全日切換** | 0ms | 0 KB | 避免清晨出發誤解，一鍵切換全天時刻 |
| **4 種維度排序選單** | < 0.1ms | < 1 KB | 滿足直達控、省時控與最快接駁各類需求 |
| **車次快速反查時刻** | < 0.05ms | ~50 KB (索引) | 支援鐵道迷、通勤族即時查驗特定車次沿途停靠 |
