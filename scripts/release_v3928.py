# -*- coding: utf-8 -*-
import json
import shutil
import os
import re

VERSION = "v3.9.28"
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
### 🚀 乘車規劃演算法全面升級：多元主力平替車次保留 ＆ 杜絕無意義前贅步
- **打破 EMU3000 單一壟斷，全面保留合法平替主力車次 (152, 150, 105, 103等)**：
  - 以 `(始發車次 ➔ 幹線主力車次)` 雙核心分群，為每一班合法主力車次（PP自強、EMU3000、普悠瑪、區間快）找出前往目的地的最佳接力方案。
  - 成功保留夜間北上 **末班自強號 152 次**（集集 18:48 ➔ 彰化等57分 ➔ 板橋 23:53），不再被提早到的 EMU3000 武斷刪除。
- **徹底清除所有無意義前贅步 (No Redundant Pre-leg Detours)**：
  - 若後續快車在出發站即有停靠，100% 自動過濾所有「叫旅客起早先搭慢車去前站等同一班快車」的怪異路線。
- **選站與車站時刻表 0ms 極速響應**：
  - 移除選站時的人為計時器延遲，並採用預建雜湊索引，點選車站與全日發車時刻表彈窗秒開零卡頓。

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

# 7. Update versions.json
v_json_path = os.path.join('versions', 'versions.json')
if os.path.exists(v_json_path):
    with open(v_json_path, 'r', encoding='utf-8') as f:
        v_data = json.load(f)
    
    if not any(item['version'] == VERSION for item in v_data):
        v_data.insert(0, {
            "version": VERSION,
            "date": DATE,
            "title": f"{VERSION} - 多元主力平替保留與杜絕無效前贅步",
            "path": f"versions/{VERSION}/index.html"
        })
        with open(v_json_path, 'w', encoding='utf-8') as f:
            json.dump(v_data, f, ensure_ascii=False, indent=2)

print(f"Successfully released {VERSION}!")
