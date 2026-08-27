# -*- coding: utf-8 -*-

with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
    c = f.read()

entry = """## [v3.9.27] - 2026-08-28
### 🚀 核心升級與修復
- **全方位多站點接力規劃引擎 (Multi-Stop Waypoint Engine)**：
  - 完整實作 `planMultiStopRoutes`，支援 3 站、4 站甚至任意多站點接力查詢（如 `社頭 ➔ 百福 ➔ 暖暖`）。
  - 修復旗艦版 3 站以上查詢時拋錯導致畫面殘留上一次查詢舊資料之問題。
- **多轉乘備選廣度擴充**：
  - 轉乘中繼站支援多組不同抵達車次並行向下探索，完整列出 2 次以上轉乘的所有中繼列車組合。
- **全方位系統深度檢測 (Full System Audit)**：
  - 926 班列車資料庫單調性、Pareto 去慢保優、零折返防搭過頭、視覺標籤與 Service Worker 快取 100% 通過檢測。

"""

if "## [v3.9.27]" not in c:
    c = entry + c

with open('CHANGELOG.md', 'w', encoding='utf-8') as f:
    f.write(c)

print("CHANGELOG.md updated with v3.9.27!")
