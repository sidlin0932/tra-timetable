# -*- coding: utf-8 -*-
"""
Release v3.9.13:
1. Major stations special border outline styling (特等/一等/重要樞紐大站外框加強，不填滿底色，高雅清晰).
2. SuperLite edition standalone category in Version Hub & clear labeling.
3. Synchronizes v3.9.13 across all files.
"""

import re
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LITE_HTML = BASE_DIR / "lite.html"
INDEX_HTML = BASE_DIR / "index.html"
SW_JS = BASE_DIR / "sw.js"
CHANGELOG = BASE_DIR / "CHANGELOG.md"
README = BASE_DIR / "README.md"
BUILD_SCRIPT = BASE_DIR / "build_multi_version_system.py"
VERSIONS_DIR = BASE_DIR / "versions"

MAJOR_STATIONS_JS = """
        const MAJOR_STATIONS = new Set([
            '基隆', '七堵', '八堵', '南港', '松山', '台北', '萬華', '板橋', '樹林',
            '桃園', '中壢', '新竹', '竹南', '苗栗', '豐原', '台中', '彰化', '員林',
            '斗六', '嘉義', '新營', '台南', '新左營', '高雄', '鳳山', '屏東', '潮州',
            '枋寮', '台東', '玉里', '花蓮', '蘇澳新', '羅東', '宜蘭', '瑞芳'
        ]);
"""

# Update lite.html
with open(LITE_HTML, "r", encoding="utf-8") as f:
    lite = f.read()

# Add MAJOR_STATIONS set
if "const MAJOR_STATIONS" not in lite:
    lite = lite.replace("const ALL_STATIONS = [];", MAJOR_STATIONS_JS + "\n        const ALL_STATIONS = [];")

# Add CSS for major station border outline
MAJOR_STATION_CSS = """
        /* Major Station Border Outline */
        .modal-station-chip.major-station {
            border: 1.5px solid #0284c7 !important;
            color: #0369a1 !important;
            font-weight: 800 !important;
            background: #ffffff !important;
            box-shadow: 0 1px 3px rgba(2, 132, 199, 0.12);
        }
        .modal-station-chip.major-station:hover {
            background: #e0f2fe !important;
            border-color: #0369a1 !important;
        }
        .chip.major-station {
            border: 1.5px solid #0284c7 !important;
            color: #0369a1 !important;
            font-weight: 800 !important;
            background: #ffffff !important;
        }
"""

if ".modal-station-chip.major-station" not in lite:
    lite = lite.replace("</style>", MAJOR_STATION_CSS + "\n    </style>")

# Update modal station chip rendering in lite.html
lite = re.sub(
    r'<button class="modal-station-chip" onclick="modalPick\(\'(\$\{st\})\'\)">\$\{st\}</button>',
    r'<button class="modal-station-chip ${MAJOR_STATIONS.has(st)?\'major-station\':\'\'}" onclick="modalPick(\'\1\')">${MAJOR_STATIONS.has(st)?\'★ \':\'\'}${st}</button>',
    lite
)

# Update version in lite.html
lite = re.sub(r'v3\.9\.\d+', 'v3.9.13', lite)
lite = lite.replace('data.js?v=3.9.12', 'data.js?v=3.9.13')

with open(LITE_HTML, "w", encoding="utf-8") as f:
    f.write(lite)

# Update index.html
with open(INDEX_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# Add CSS in index.html
if ".station-chip.major-station" not in html:
    INDEX_MAJOR_CSS = """
        /* Major Stations Special Border (No heavy fill) */
        .station-chip.major-station, .modal-station-chip.major-station {
            border: 1.5px solid #0284c7 !important;
            color: #0369a1 !important;
            font-weight: 800 !important;
            background: #ffffff !important;
            box-shadow: 0 1px 3px rgba(2, 132, 199, 0.12);
        }
        .station-chip.major-station:hover, .modal-station-chip.major-station:hover {
            background: #e0f2fe !important;
            border-color: #0369a1 !important;
        }
    """
    html = html.replace("</style>", INDEX_MAJOR_CSS + "\n    </style>")

if "const MAJOR_STATIONS = new Set" not in html:
    html = html.replace("const TAIWAN_COUNTIES =", MAJOR_STATIONS_JS + "\n        const TAIWAN_COUNTIES =")

# Update station modal rendering in index.html
html = re.sub(
    r'<button class="station-chip" onclick="selectModalStation\(\'(\$\{st\})\'\)">\$\{st\}</button>',
    r'<button class="station-chip ${typeof MAJOR_STATIONS !== \'undefined\' && MAJOR_STATIONS.has(st)?\'major-station\':\'\'}" onclick="selectModalStation(\'\1\')">${typeof MAJOR_STATIONS !== \'undefined\' && MAJOR_STATIONS.has(st)?\'★ \':\'\'}${st}</button>',
    html
)

html = re.sub(r'v3\.9\.\d+', 'v3.9.13', html)
html = html.replace('data.js?v=3.9.12', 'data.js?v=3.9.13')

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html)

# Update sw.js
with open(SW_JS, "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r'v3\.9\.\d+', 'v3.9.13', sw)
sw = re.sub(r'tra-timetable-pwa-v\d+', 'tra-timetable-pwa-v3913', sw)
sw = re.sub(r'tra-runtime-v\d+', 'tra-runtime-v3913', sw)
with open(SW_JS, "w", encoding="utf-8") as f:
    f.write(sw)

# Update CHANGELOG.md
with open(CHANGELOG, "r", encoding="utf-8") as f:
    cl = f.read()

V3913_CHANGELOG = """## [v3.9.13] - 2026-08-25

### 🌟 特等／一等主要大站精緻外框標示 ＆ SuperLite 專屬版本庫註記
- **1. 主要大站專屬外框識別（高雅邊框，不滿版填色）**：
  - 台北、台中、高雄、花蓮、台東、新竹、板橋、台南、員林等 35 個樞紐大站加上精緻 **`★ 藍色質感邊框`**，視覺一秒鎖定大站，保持介面清爽高雅。
- **2. 多版本中心專屬 SuperLite 專區 (`versions/index.html` / `versions/lite/`)**：
  - 置頂【⚡ TRA SuperLite 極速極簡版】專屬卡片與獨立封存快照。
- **3. 全功能旗艦版與極速極簡版同步支援**。

---

"""

if "## [v3.9.13]" not in cl:
    cl = cl.replace("# 更新日誌 (Changelog)\n\n---\n\n", "# 更新日誌 (Changelog)\n\n---\n\n" + V3913_CHANGELOG)
    with open(CHANGELOG, "w", encoding="utf-8") as f:
        f.write(cl)

# Update README.md
with open(README, "r", encoding="utf-8") as f:
    rm = f.read()
rm = re.sub(r'v3\.9\.\d+', 'v3.9.13', rm)
with open(README, "w", encoding="utf-8") as f:
    f.write(rm)

# Update build_multi_version_system.py
with open(BUILD_SCRIPT, "r", encoding="utf-8") as f:
    bld = f.read()
if '{"version": "v3.9.13"' not in bld:
    bld = bld.replace('HISTORICAL_COMMITS = [', 'HISTORICAL_COMMITS = [\n    {"version": "v3.9.13", "commit": "HEAD",    "date": "2026-08-25", "desc": "主要大站質感邊框標示 ＆ SuperLite 專區獨立註記"},')
    with open(BUILD_SCRIPT, "w", encoding="utf-8") as f:
        f.write(bld)

# Snapshot versions/lite/
LITE_SNAP_DIR = VERSIONS_DIR / "lite"
LITE_SNAP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(LITE_HTML, LITE_SNAP_DIR / "index.html")
shutil.copy2(BASE_DIR / "data.js", LITE_SNAP_DIR / "data.js")
shutil.copy2(BASE_DIR / "manifest.json", LITE_SNAP_DIR / "manifest.json")
if (BASE_DIR / "icon-192.png").exists():
    shutil.copy2(BASE_DIR / "icon-192.png", LITE_SNAP_DIR / "icon-192.png")
if (BASE_DIR / "icon-512.png").exists():
    shutil.copy2(BASE_DIR / "icon-512.png", LITE_SNAP_DIR / "icon-512.png")

print("v3.9.13 applied successfully!")
