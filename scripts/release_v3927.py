# -*- coding: utf-8 -*-
import json
import shutil
import os
import re

VERSION = "v3.9.27"
DATE = "2026-08-28"

print(f"Bumping version to {VERSION}...")

# 1. Update index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'v3\.9\.\d+', VERSION, html)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 2. Update lite.html
with open('lite.html', 'r', encoding='utf-8') as f:
    lite = f.read()

lite = re.sub(r'v3\.9\.\d+', VERSION, lite)
with open('lite.html', 'w', encoding='utf-8') as f:
    f.write(lite)

# 3. Update sw.js
with open('sw.js', 'r', encoding='utf-8') as f:
    sw = f.read()

sw = re.sub(r'tra-timetable-cache-v3\.9\.\d+', f'tra-timetable-cache-{VERSION}', sw)
with open('sw.js', 'w', encoding='utf-8') as f:
    f.write(sw)

# 4. Update README.md
with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

readme = re.sub(r'v3\.9\.\d+', VERSION, readme)
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme)

# 5. Update CHANGELOG.md
changelog_entry = f"""## [{VERSION}] - {DATE}

### 🚀 核心升級與修復
- **全方位多站點接力規劃引擎 (Multi-Stop Waypoint Engine)**：
  - 完整實作 `planMultiStopRoutes`，支援 3 站、4 站甚至任意多站點接力查詢（如 `社頭 ➔ 百福 ➔ 暖暖`）。
  - 修復旗艦版 3 站以上查詢時拋錯導致畫面殘留上一次查詢舊資料之問題。
- **多轉乘備選廣度擴充**：
  - 轉乘中繼站支援多組不同抵達車次並行向下探索，完整列出 2 次以上轉乘的所有中繼列車組合。
- **全方位系統深度檢測 (Full System Audit)**：
  - 926 班列車資料庫單調性、Pareto 去慢保優、零折返防搭過頭、視覺標籤與 Service Worker 快取 100% 通過檢測。

"""

with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
    changelog = f.read()

if f"## [{VERSION}]" not in changelog:
    changelog = changelog.replace("# 📋 更新日誌 (Changelog)\n\n", f"# 📋 更新日誌 (Changelog)\n\n{changelog_entry}")
    with open('CHANGELOG.md', 'w', encoding='utf-8') as f:
        f.write(changelog)

# 6. Create version snapshot
snapshot_dir = os.path.join('versions', VERSION)
os.makedirs(snapshot_dir, exist_ok=True)
shutil.copy('index.html', os.path.join(snapshot_dir, 'index.html'))
if os.path.exists('lite.html'):
    shutil.copy('lite.html', os.path.join(snapshot_dir, 'lite.html'))

# 7. Update versions.json
v_json_path = os.path.join('versions', 'versions.json')
if os.path.exists(v_json_path):
    with open(v_json_path, 'r', encoding='utf-8') as f:
        v_data = json.load(f)
    
    if not any(item['version'] == VERSION for item in v_data):
        v_data.insert(0, {
            "version": VERSION,
            "date": DATE,
            "title": f"{VERSION} - 多站點接力引擎與全方位深度檢測通過",
            "path": f"versions/{VERSION}/index.html"
        })
        with open(v_json_path, 'w', encoding='utf-8') as f:
            json.dump(v_data, f, ensure_ascii=False, indent=2)

print(f"Successfully released {VERSION}!")
