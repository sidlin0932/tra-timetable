# -*- coding: utf-8 -*-
"""
Releases v3.9.1 Patch with Neiwan line fix, modal scrolling fix, and SVG visual cleanup.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# 1. Update index.html
index_path = BASE_DIR / "index.html"
with open(index_path, "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("v3.9.0", "v3.9.1")
html = html.replace("v390", "v391")

# Update Version selector
html = html.replace(
    '<option value="latest" selected>v3.9.0 (鐵路地圖 & 縣市過濾版)</option>',
    '<option value="latest" selected>v3.9.1 (內灣線修復 & 滾動美化版)</option>\n                                <option value="v3.9.0">v3.9.0 (鐵路地圖 & 縣市過濾版)</option>'
)

with open(index_path, "w", encoding="utf-8") as f:
    f.write(html)

# 2. Update sw.js
sw_path = BASE_DIR / "sw.js"
with open(sw_path, "r", encoding="utf-8") as f:
    sw = f.read()

sw = sw.replace("v3.9.0", "v3.9.1")
sw = sw.replace("v390", "v391")

with open(sw_path, "w", encoding="utf-8") as f:
    f.write(sw)

# 3. Update CHANGELOG.md
changelog_path = BASE_DIR / "CHANGELOG.md"
with open(changelog_path, "r", encoding="utf-8") as f:
    cl = f.read()

CHANGELOG_ENTRY = """## [v3.9.1] - 2026-08-25

### 🔧 內灣線車次全量補齊、選站彈窗滾動修復與地圖視覺精緻化 (Neiwan Branch & Modal Scroll Fix)
- **1. 解決「內灣 ➔ 六家」查詢為 0 個方案之重大資料庫問題**：
  - 根因分析：原本解析 `Neiwan20260701.ods` 時僅讀取前 68 行南下車次，忽略了第 71 至 134 行之北上/返程車次（1801、1803、1805 等車次）。
  - 修復後全數收錄內灣線與六家線 125 班車次，「內灣 ➔ 六家」成功產出 **69 個順暢接駁方案**（於竹中站無縫轉乘）！
- **2. 徹底修復車站選擇彈窗「無法往下滑動 (Scroll Locked)」問題**：
  - 重構 Modal 彈窗之 Flex 容器層級，為 `#modalListView`、`#modalStationList` 與 `#modalMapView` 注入 `flex: 1; min-height: 0; overflow-y: auto;` 規範，確保手機與桌面端在清單模式與地圖模式均可 100% 順暢滑動。
- **3. 全面剔除地圖黑色大圈重疊破版，回歸晶透 Transit Map 質感**：
  - 修正 SVG `<circle>` 預設黑底問題，改為輕量透明 Hitbox 與白邊彩點，車站名稱採精確對齊與抗光影襯底，呈現清爽現代風格。

---

"""

cl = cl.replace("## [v3.9.0] - 2026-08-25", CHANGELOG_ENTRY + "## [v3.9.0] - 2026-08-25")

with open(changelog_path, "w", encoding="utf-8") as f:
    f.write(cl)

# 4. Update README.md
readme_path = BASE_DIR / "README.md"
with open(readme_path, "r", encoding="utf-8") as f:
    rm = f.read()

rm = rm.replace("v3.9.0", "v3.9.1")

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(rm)

# 5. Update build_multi_version_system.py
builder_path = BASE_DIR / "build_multi_version_system.py"
with open(builder_path, "r", encoding="utf-8") as f:
    builder = f.read()

builder = builder.replace(
    '{"version": "v3.9.0",  "commit": "HEAD", "date": "2026-08-25", "desc": "台灣鐵路地理地圖模式 & 全台 17 縣市多選勾選過濾系統 (Minor 大版升級)"},',
    '{"version": "v3.9.1",  "commit": "HEAD", "date": "2026-08-25", "desc": "內灣線全班次補齊 (69方案) & 車站彈窗雙模式滾動修復"},'
)

with open(builder_path, "w", encoding="utf-8") as f:
    f.write(builder)

print("v3.9.1 release files updated!")
