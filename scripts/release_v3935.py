# -*- coding: utf-8 -*-
import json
import shutil
import os
import re

VERSION = "v3.9.35"
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
### ⚡ 全面過濾直達車已到卻中途換乘更慢車次的冗餘方案（Direct Train Dominance Filter）
- **直達更優則嚴禁轉乘（Pareto 直達絕對優勢剪枝）**：
  - 若已搭乘直達目的地之列車，嚴禁推薦中途下車、長時間等候並轉乘抵達時間更晚之班次（例如搭乘區間車 4224 直達 19:51 到，卻推薦於雙溪下車等 78 分鐘轉搭 4046 至 20:57 到之負效益轉乘）。
  - 若存在同時間或更晚出發且更早抵達之「直達列車」，所有劣勢轉乘方案自動全數剔除，介面僅呈現最具實用性之優質方案。
- **100% 精準淨化轉乘結果清單**。

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
            "title": f"{VERSION} - 全面剔除直達更優卻中途換乘更慢班次之冗餘方案",
            "path": f"versions/{VERSION}/index.html"
        })
        with open(v_json_path, 'w', encoding='utf-8') as f:
            json.dump(v_data, f, ensure_ascii=False, indent=2)

print(f"Successfully released {VERSION}!")
