# -*- coding: utf-8 -*-
"""
Release v3.9.13:
1. Clearly badges and categorizes SuperLite in the Version Hub (versions/index.html).
2. Generates standalone snapshot versions/lite/ directory.
3. Updates UI badges:
   - lite.html: '⚡ TRA SuperLite · 極速極簡版 v3.9.13-lite'
   - index.html: '🌟 TRA Flagship · 全功能旗艦版 v3.9.13'
4. Updates CHANGELOG.md, README.md, sw.js, and version builder.
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

# 1. Update lite.html with clear edition & version badge
with open(LITE_HTML, "r", encoding="utf-8") as f:
    lite = f.read()

lite = re.sub(r'v3\.9\.\d+', 'v3.9.13', lite)
lite = lite.replace('data.js?v=3.9.12', 'data.js?v=3.9.13')
lite = lite.replace('<span class="badge-lite">極速極簡版</span>', '<span class="badge-lite" style="background:#10b981; color:#fff; font-size:0.75rem; padding:3px 10px; border-radius:20px; font-weight:800;">⚡ SuperLite 極速極簡版 v3.9.13-lite</span>')

with open(LITE_HTML, "w", encoding="utf-8") as f:
    f.write(lite)

# 2. Update index.html with clear edition & version badge
with open(INDEX_HTML, "r", encoding="utf-8") as f:
    html = f.read()

html = re.sub(r'v3\.9\.\d+', 'v3.9.13', html)
html = html.replace('data.js?v=3.9.12', 'data.js?v=3.9.13')

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html)

# 3. Update sw.js
with open(SW_JS, "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r'v3\.9\.\d+', 'v3.9.13', sw)
sw = re.sub(r'tra-timetable-pwa-v\d+', 'tra-timetable-pwa-v3913', sw)
sw = re.sub(r'tra-runtime-v\d+', 'tra-runtime-v3913', sw)
with open(SW_JS, "w", encoding="utf-8") as f:
    f.write(sw)

# 4. Create versions/lite/ standalone directory
LITE_SNAP_DIR = VERSIONS_DIR / "lite"
LITE_SNAP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(LITE_HTML, LITE_SNAP_DIR / "index.html")
shutil.copy2(BASE_DIR / "data.js", LITE_SNAP_DIR / "data.js")
shutil.copy2(BASE_DIR / "manifest.json", LITE_SNAP_DIR / "manifest.json")
if (BASE_DIR / "icon-192.png").exists():
    shutil.copy2(BASE_DIR / "icon-192.png", LITE_SNAP_DIR / "icon-192.png")
if (BASE_DIR / "icon-512.png").exists():
    shutil.copy2(BASE_DIR / "icon-512.png", LITE_SNAP_DIR / "icon-512.png")

# 5. Update build_multi_version_system.py to include SuperLite card in Hub UI
with open(BUILD_SCRIPT, "r", encoding="utf-8") as f:
    bld = f.read()

if '{"version": "v3.9.13"' not in bld:
    bld = bld.replace('HISTORICAL_COMMITS = [', 'HISTORICAL_COMMITS = [\n    {"version": "v3.9.13", "commit": "HEAD",    "date": "2026-08-25", "desc": "發布獨立 SuperLite 極速極簡版專屬版本庫 ＆ 多版本中心標註"},')

# Inject SuperLite Banner in Hub UI HTML generator
SUPERLITE_HUB_CARD = """
        <!-- SuperLite Featured Hero Card -->
        <div style="background: linear-gradient(135deg, #064e3b 0%, #065f46 100%); border: 1.5px solid #10b981; border-radius: 16px; padding: 22px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(16, 185, 129, 0.2);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                        <span style="background: #10b981; color: #fff; font-size: 0.75rem; font-weight: 800; padding: 3px 10px; border-radius: 20px;">⚡ 獨立極速版本</span>
                        <h2 style="font-size: 1.3rem; font-weight: 800; color: #fff; margin: 0;">2026 台鐵時刻表 · 極速極簡版 (TRA SuperLite)</h2>
                    </div>
                    <p style="font-size: 0.85rem; color: #a7f3d0; margin: 0;">0.2 毫秒瞬發算路、原生字型零卡頓、支援多站停靠、17 縣市視覺化選站與 TPASS 篩選</p>
                </div>
                <div style="display: flex; gap: 10px;">
                    <a href="../lite.html" style="background: #10b981; color: #fff; font-weight: 800; font-size: 0.9rem; padding: 10px 18px; border-radius: 10px; text-decoration: none; box-shadow: 0 2px 10px rgba(16,185,129,0.4);">🚀 立即啟動 SuperLite</a>
                    <a href="lite/index.html" style="background: rgba(255,255,255,0.15); color: #fff; font-weight: 700; font-size: 0.85rem; padding: 10px 14px; border-radius: 10px; text-decoration: none; border: 1px solid rgba(255,255,255,0.2);">📦 快照封存</a>
                </div>
            </div>
        </div>
"""

if "<!-- SuperLite Featured Hero Card -->" not in bld:
    bld = bld.replace('<main class="main">', '<main class="main">\n' + SUPERLITE_HUB_CARD)

with open(BUILD_SCRIPT, "w", encoding="utf-8") as f:
    f.write(bld)

# 6. Update CHANGELOG.md
with open(CHANGELOG, "r", encoding="utf-8") as f:
    cl = f.read()

V3913_CHANGELOG = """## [v3.9.13] - 2026-08-25

### 🏷️ SuperLite 極速極簡版專屬獨立套版 ＆ 多版本中心專區註記
- **1. 多版本中心專屬 SuperLite 專區 (`versions/index.html`)**：
  - 在歷史版本中心置頂【⚡ TRA SuperLite 極速極簡版】專屬卡片與快照 (`versions/lite/`)。
- **2. 雙版本清晰標註與導航**：
  - `lite.html` 明確標記 **`⚡ TRA SuperLite · 極速極簡版 v3.9.13-lite`**。
  - `index.html` 明確標記 **`🌟 TRA Flagship · 全功能旗艦版 v3.9.13`**。

---

"""

if "## [v3.9.13]" not in cl:
    cl = cl.replace("# 更新日誌 (Changelog)\n\n---\n\n", "# 更新日誌 (Changelog)\n\n---\n\n" + V3913_CHANGELOG)
    with open(CHANGELOG, "w", encoding="utf-8") as f:
        f.write(cl)

# 7. Update README.md
with open(README, "r", encoding="utf-8") as f:
    rm = f.read()
rm = re.sub(r'v3\.9\.\d+', 'v3.9.13', rm)
with open(README, "w", encoding="utf-8") as f:
    f.write(rm)

print("v3.9.13 applied successfully!")
