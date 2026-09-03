# -*- coding: utf-8 -*-
import json
import shutil
import os
import re

VERSION = "v3.9.36"
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
### 🎯 全面引進全域 Pareto 絕對劣解剪枝引擎（Strict Generalized Pareto Dominance Engine）
- **絕對劣解全面封殺剔除**：
  - 嚴格實作數學 Pareto 支配判定：凡存在任一方案 A「出發時間 $\\ge$ 方案 B、抵達時間 $\\le$ 方案 B、轉乘次數 $\\le$ 方案 B」，則方案 B 屬於時間與換車全輸之絕對劣解，毫不留情直接從清單剔除。
  - 徹底消除任何「搭乘直達車卻中途下車換乘更慢車次」與「先搭慢車去前面車站換同一班快車」等一切贅步與非理性轉乘。
- **全路網轉乘查詢品質達到頂級純淨與高效**。

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
            "title": f"{VERSION} - 全面引進全域 Pareto 絕對劣解剪枝引擎，極致純淨乘車方案",
            "path": f"versions/{VERSION}/index.html"
        })
        with open(v_json_path, 'w', encoding='utf-8') as f:
            json.dump(v_data, f, ensure_ascii=False, indent=2)

print(f"Successfully released {VERSION}!")
