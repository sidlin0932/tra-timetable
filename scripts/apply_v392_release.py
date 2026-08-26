# -*- coding: utf-8 -*-
"""
Releases v3.9.2 Patch: Mobile-first Railway Map with 48px touch targets, region focus tabs, and crisp high-contrast layout.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# 1. Update index.html
index_path = BASE_DIR / "index.html"
with open(index_path, "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("v3.9.1", "v3.9.2")
html = html.replace("v391", "v392")

# Update Version selector
html = html.replace(
    '<option value="latest" selected>v3.9.1 (內灣線修復 & 滾動美化版)</option>',
    '<option value="latest" selected>v3.9.2 (手機優先極速地圖 & 48px觸控區)</option>\n                                <option value="v3.9.1">v3.9.1 (內灣線修復 & 滾動美化版)</option>'
)

with open(index_path, "w", encoding="utf-8") as f:
    f.write(html)

# 2. Update sw.js
sw_path = BASE_DIR / "sw.js"
with open(sw_path, "r", encoding="utf-8") as f:
    sw = f.read()

sw = sw.replace("v3.9.1", "v3.9.2")
sw = sw.replace("v391", "v392")

with open(sw_path, "w", encoding="utf-8") as f:
    f.write(sw)

# 3. Update CHANGELOG.md
changelog_path = BASE_DIR / "CHANGELOG.md"
with open(changelog_path, "r", encoding="utf-8") as f:
    cl = f.read()

CHANGELOG_ENTRY = """## [v3.9.2] - 2026-08-25

### 📱 手機優先極速地圖重構、48px 觸控熱區與分區聚焦 (Mobile-First Map Overhaul)
- **1. 擴大車站觸控熱區至 48px (Apple HIG & Material Design 規範)**：
  - 每個車站增加 `r=22` (44~48px 直徑) 之透明觸控熱區，手機手指隨手一點即可 100% 精準命中選站，徹底解決「點不到」的問題！
- **2. 導入「分區即時聚焦切換鈕 (Region Fast Zoom Tabs)」**：
  - 提供 `[🗺️ 全島總覽]`、`[🚄 北部幹線]`、`[🚄 中部山海]`、`[🚄 南部高屏]`、`[🌊 東部南迴]`、`[🌿 觀光支線]` 快速切換。
  - 切換後自動放大局部路網並展開車站間距，台北、松山、南港等密集大站完全拉開距離，字體高清晰、站名 100% 不重疊！
- **3. 抗光暈雙層白邊站名與醒目高對比配色**：
  - 移除干擾性的底層色塊，採用清新雙色軌道與白邊抗眩光站名，強光或夜間均清晰易讀。
- **4. 支援觸控即選 (1-Tap Fast Pick) 與 Action Sheet 動作面板**。

---

"""

cl = cl.replace("## [v3.9.1] - 2026-08-25", CHANGELOG_ENTRY + "## [v3.9.1] - 2026-08-25")

with open(changelog_path, "w", encoding="utf-8") as f:
    f.write(cl)

# 4. Update README.md
readme_path = BASE_DIR / "README.md"
with open(readme_path, "r", encoding="utf-8") as f:
    rm = f.read()

rm = rm.replace("v3.9.1", "v3.9.2")

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(rm)

# 5. Update build_multi_version_system.py
builder_path = BASE_DIR / "build_multi_version_system.py"
with open(builder_path, "r", encoding="utf-8") as f:
    builder = f.read()

builder = builder.replace(
    '{"version": "v3.9.1",  "commit": "HEAD", "date": "2026-08-25", "desc": "內灣線全班次補齊 (69方案) & 車站彈窗雙模式滾動修復"},',
    '{"version": "v3.9.2",  "commit": "HEAD", "date": "2026-08-25", "desc": "手機優先極速地圖、48px超大觸控熱區 & 分區即時聚焦切換"},'
)

with open(builder_path, "w", encoding="utf-8") as f:
    f.write(builder)

print("v3.9.2 release files updated!")
