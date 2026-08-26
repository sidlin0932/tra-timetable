# -*- coding: utf-8 -*-
"""
Release v3.9.19:
1. Default time: All-Day (00:00 全日方案).
2. Default origin station: 板橋 (Banqiao).
3. Synchronized across index.html (Flagship) and lite.html (SuperLite).
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

# 1. Update lite.html
with open(LITE_HTML, "r", encoding="utf-8") as f:
    lite = f.read()

# Change default waypoints to 板橋 -> 新竹
lite = lite.replace("{ station: '台北', minStay: 0 },\n            { station: '新竹', minStay: 0 }", "{ station: '板橋', minStay: 0 },\n            { station: '新竹', minStay: 0 }")
lite = lite.replace("{ station: '台北', minStay: 0 }, { station: '新竹', minStay: 0 }", "{ station: '板橋', minStay: 0 }, { station: '新竹', minStay: 0 }")

# Change DOMContentLoaded from setTimeVal('now') to setTimeVal('00:00')
lite = lite.replace("setTimeVal('now');", "setTimeVal('00:00');")

# Version bump
lite = re.sub(r'v3\.9\.\d+', 'v3.9.19', lite)
lite = lite.replace('data.js?v=3.9.18', 'data.js?v=3.9.19')

with open(LITE_HTML, "w", encoding="utf-8") as f:
    f.write(lite)

# 2. Update index.html
with open(INDEX_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# Make sure index.html default origin is 板橋 and default time 00:00
html = html.replace('value="台北" id="originInput"', 'value="板橋" id="originInput"')
html = html.replace('value="台北" id="origin"', 'value="板橋" id="origin"')
html = html.replace('value="台北" placeholder="出發站"', 'value="板橋" placeholder="出發站"')

html = re.sub(r'v3\.9\.\d+', 'v3.9.19', html)
html = html.replace('data.js?v=3.9.18', 'data.js?v=3.9.19')

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html)

# 3. Update sw.js
with open(SW_JS, "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r'v3\.9\.\d+', 'v3.9.19', sw)
sw = re.sub(r'tra-timetable-pwa-v\d+', 'tra-timetable-pwa-v3919', sw)
sw = re.sub(r'tra-runtime-v\d+', 'tra-runtime-v3919', sw)
with open(SW_JS, "w", encoding="utf-8") as f:
    f.write(sw)

# 4. Update CHANGELOG.md
with open(CHANGELOG, "r", encoding="utf-8") as f:
    cl = f.read()

V3919_CHANGELOG = """## [v3.9.19] - 2026-08-25

### 📍 預設起點調整為【板橋】＆ 預設查詢時段設定為【全日 00:00 起】
- **1. 起點車站預設變更**：
  - 進入時刻表首頁與 SuperLite 版，起發站點預設為 **`板橋`**（預設行程：板橋 ➔ 新竹）。
- **2. 查詢時段預設全日**：
  - 預設載入全日 00:00 起全部班次，並維持 6 大時段快捷鍵隨時一鍵切換。

---

"""

if "## [v3.9.19]" not in cl:
    cl = cl.replace("# 更新日誌 (Changelog)\n\n---\n\n", "# 更新日誌 (Changelog)\n\n---\n\n" + V3919_CHANGELOG)
    with open(CHANGELOG, "w", encoding="utf-8") as f:
        f.write(cl)

# 5. Update README.md
with open(README, "r", encoding="utf-8") as f:
    rm = f.read()
rm = re.sub(r'v3\.9\.\d+', 'v3.9.19', rm)
with open(README, "w", encoding="utf-8") as f:
    f.write(rm)

# 6. Update build_multi_version_system.py
with open(BUILD_SCRIPT, "r", encoding="utf-8") as f:
    bld = f.read()
if '{"version": "v3.9.19"' not in bld:
    bld = bld.replace('HISTORICAL_COMMITS = [', 'HISTORICAL_COMMITS = [\n    {"version": "v3.9.19", "commit": "HEAD",    "date": "2026-08-25", "desc": "起點預設板橋 ＆ 時段預設全日 00:00 起"},')
    with open(BUILD_SCRIPT, "w", encoding="utf-8") as f:
        f.write(bld)

# Snapshot versions/lite/
LITE_SNAP_DIR = VERSIONS_DIR / "lite"
LITE_SNAP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(LITE_HTML, LITE_SNAP_DIR / "index.html")
shutil.copy2(BASE_DIR / "data.js", LITE_SNAP_DIR / "data.js")
shutil.copy2(BASE_DIR / "manifest.json", LITE_SNAP_DIR / "manifest.json")

print("v3.9.19 applied successfully!")
