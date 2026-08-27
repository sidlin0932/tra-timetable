# -*- coding: utf-8 -*-
import json
import shutil
import os
import re

VERSION = "v3.9.32"
DATE = "2026-08-28"

print(f"Releasing {VERSION}...")

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

sw = re.sub(r'v3\.9\.\d+', VERSION, sw)
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
### 🚀 消除原始 ODS 英文重複停靠站（如 Taipei/Kaohsiung）＆ 確保幹線直達一車到底
- **根除英文重複停靠站問題**：
  - 修正原始官方 ODS 雙語表格中夾雜的英文重複站名（如 `Taipei`、`Kaohsiung`、`Hualien`、`Taitung` 等）。
  - 解決自強號 138 次（屏東➔七堵）等幹線列車在經過台北後因英文站名造成路徑中斷、無法一車到底繼續搭至松山/七堵的重大路徑規劃問題。
- **全路網直達方案與轉乘拓撲 100% 滿分暢通**。

"""

with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
    changelog = f.read()

if f"## [{VERSION}]" not in changelog:
    changelog = changelog_entry + changelog
    with open('CHANGELOG.md', 'w', encoding='utf-8') as f:
        f.write(changelog)

# 6. Create version snapshot
snapshot_dir = os.path.join('versions', VERSION)
os.makedirs(snapshot_dir, exist_ok=True)
shutil.copy('index.html', os.path.join(snapshot_dir, 'index.html'))
shutil.copy('lite.html', os.path.join(snapshot_dir, 'lite.html'))
shutil.copy('data.js', os.path.join(snapshot_dir, 'data.js'))
shutil.copy('full_network_timetable.json', os.path.join(snapshot_dir, 'full_network_timetable.json'))

# 7. Update versions.json
v_json_path = os.path.join('versions', 'versions.json')
if os.path.exists(v_json_path):
    with open(v_json_path, 'r', encoding='utf-8') as f:
        v_data = json.load(f)
    
    if not any(item['version'] == VERSION for item in v_data):
        v_data.insert(0, {
            "version": VERSION,
            "date": DATE,
            "title": f"{VERSION} - 消除英文重複站名，確保幹線列車一車到底直達",
            "path": f"versions/{VERSION}/index.html"
        })
        with open(v_json_path, 'w', encoding='utf-8') as f:
            json.dump(v_data, f, ensure_ascii=False, indent=2)

print(f"Successfully released {VERSION}!")
