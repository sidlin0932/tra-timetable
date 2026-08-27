# -*- coding: utf-8 -*-
import json
import shutil
import os
import re

VERSION = "v3.9.31"
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
### 🚀 縱貫線南段區間車全量多欄動態提取 ＆ 全日班次完備補齊
- **修復區間車多欄位交錯跳列漏抓問題**：
  - 修正縱貫線南段（彰化↔嘉義、嘉義↔高雄、高雄↔枋寮等）因原始 ODS 車次編號散落於 Col 1/2/3 導致 80% 區間車被跳過的重大缺陷。
  - 二水 ➔ 彰化 全日方案由原本殘缺的 6 班瞬間擴充至 **121 班（49 班直達區間快/區間車）**，19:00 後晚班車完整補齊 2264、2072、3238、2274、3248 等直達班次！
- **全路網 924 班列車時間單調性 100% 滿分維持**。

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
            "title": f"{VERSION} - 縱貫線南段區間車全量完備補齊（二水➔彰化擴充至121方案）",
            "path": f"versions/{VERSION}/index.html"
        })
        with open(v_json_path, 'w', encoding='utf-8') as f:
            json.dump(v_data, f, ensure_ascii=False, indent=2)

print(f"Successfully released {VERSION}!")
