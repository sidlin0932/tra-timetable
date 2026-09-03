# -*- coding: utf-8 -*-
import json
import shutil
import os
import re

VERSION = "v3.9.33"
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
### 🔄 完美支援多站往返/環島行程（如 板橋 ➔ 宜蘭 ➔ 板橋、一日遊與自由停留接駁）
- **解除起訖站相同（Round-Trip / 環島 / 折返）的誤判限制**：
  - 修正多站行程在起點與終點相同（如 `板橋 ➔ 宜蘭 ➔ 板橋` 或 `台北 ➔ 台中 ➔ 台北`）時，因原先起訖相同判定導致直接回傳 0 個方案的問題。
  - 調整多站檢驗邏輯為「僅相鄰站點不可相同」，完全支援任意多段折返、環島及中途停靠觀光行程。
- **優化中繼站停留時間接駁運算**：
  - 各段列車皆依前一段列車抵達時間＋使用者設定之自訂停留時間（X 分鐘），精準匹配並推薦最佳後續班次。
- **防止 Pareto 剪枝誤殺折返車次**：
  - 多站行程繞過單段換乘剪枝（Detour Elimination），完整保留返程列車與多元主力車種。

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
            "title": f"{VERSION} - 支援多站折返往返（板橋➔宜蘭➔板橋）與自訂停留時間接駁",
            "path": f"versions/{VERSION}/index.html"
        })
        with open(v_json_path, 'w', encoding='utf-8') as f:
            json.dump(v_data, f, ensure_ascii=False, indent=2)

print(f"Successfully released {VERSION}!")
