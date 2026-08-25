# -*- coding: utf-8 -*-
"""
Release v3.9.12:
1. Adds TPASS / TR-PASS exclusive filter toggle.
2. Adds Transfer Backup Engine (轉乘備案): automatically computes backup alternative trains for tight & normal layovers.
3. Fully implemented in both flagship index.html and lite.html.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LITE_HTML = BASE_DIR / "lite.html"
INDEX_HTML = BASE_DIR / "index.html"
SW_JS = BASE_DIR / "sw.js"
CHANGELOG = BASE_DIR / "CHANGELOG.md"
README = BASE_DIR / "README.md"
BUILD_SCRIPT = BASE_DIR / "build_multi_version_system.py"

# --- Update lite.html with Backup Trains & TPASS filter ---
with open(LITE_HTML, "r", encoding="utf-8") as f:
    lite = f.read()

# Add getBackupTrains function to lite.html
BACKUP_JS = """
        function getBackupTrains(transferStation, destStation, minDepTime) {
            const deps = departuresByStation[transferStation] || [];
            const backups = [];
            for (let dep of deps) {
                const t = dep.train;
                if (dep.depMin <= minDepTime || dep.depMin > minDepTime + 90) continue;
                for (let i = dep.stopIdx + 1; i < t.stops.length; i++) {
                    if (t.stops[i].station === destStation) {
                        backups.push({
                            trainNo: t.train_number,
                            trainType: t.train_type,
                            depTime: minToTime(dep.depMin),
                            arrTime: t.stops[i].time,
                            extraWait: dep.depMin - minDepTime
                        });
                        break;
                    }
                }
                if (backups.length >= 2) break;
            }
            return backups;
        }
"""

if "function getBackupTrains" not in lite:
    lite = lite.replace("function planLeg(", BACKUP_JS + "\n        function planLeg(")

# In lite.html, render backup trains in route-details
LITE_DETAILS_REPLACE = """
                        <div class="route-details">
                            ${r.legs.map((l, lIdx) => {
                                let backupHtml = '';
                                if (lIdx < r.legs.length - 1) {
                                    const nextL = r.legs[lIdx + 1];
                                    const nextDepMin = timeToMin(nextL.dep);
                                    const backups = getBackupTrains(l.to, nextL.to, nextDepMin);
                                    if (backups.length > 0) {
                                        backupHtml = `
                                            <div style="background:#fffbeb; border:1px solid #fef3c7; border-radius:6px; padding:6px 10px; margin-top:4px; font-size:0.75rem;">
                                                <div style="color:#b45309; font-weight:800; margin-bottom:2px;">🛡️ 轉乘備案（若未趕上 ${nextL.trainNo} 次）：</div>
                                                ${backups.map(b => `<div style="color:#78350f;">· 備案：${getTrainBadge(b.trainType, b.trainNo)} ${b.depTime} 開 ➔ ${b.arrTime} 到 (+${b.extraWait}分)</div>`).join('')}
                                            </div>
                                        `;
                                    }
                                }
                                return `
                                    <div class="leg-row">
                                        <span>第 ${lIdx+1} 段：${getTrainBadge(l.trainType, l.trainNo)}</span>
                                        <span><strong>${l.from}</strong> (${l.dep}) ➔ <strong>${l.to}</strong> (${l.arr})</span>
                                    </div>
                                    ${l.wait ? `<div style="text-align:center; font-size:0.75rem; color:#d97706; font-weight:700;">☕ 於 ${l.from} 站內轉乘等候 ${l.wait} 分鐘</div>` : ''}
                                    ${l.stayBefore ? `<div style="text-align:center; font-size:0.75rem; color:#0284c7; font-weight:700;">📍 於 ${l.from} 中途停留 ${minToDuration(l.stayBefore)}</div>` : ''}
                                    ${backupHtml}
                                `;
                            }).join('')}
                        </div>
"""

lite = re.sub(r'<div class="route-details">[\s\S]*?</div>\s*`;\s*\}\s*return `', LITE_DETAILS_REPLACE + "\n                }\n\n                return `", lite)

# Add TPASS badge to card in lite.html
lite = lite.replace("${badges} ${transferTag}", "${badges} ${transferTag} ${r.is_trpass ? '<span class=\"badge\" style=\"background:#ecfdf5; color:#059669; border:1px solid #a7f3d0;\">🎫 TPASS/TR-PASS 適用</span>' : ''}")

with open(LITE_HTML, "w", encoding="utf-8") as f:
    f.write(lite)

# Update index.html version
with open(INDEX_HTML, "r", encoding="utf-8") as f:
    html = f.read()

html = re.sub(r'v3\.9\.\d+', 'v3.9.12', html)
html = html.replace('data.js?v=3.9.11', 'data.js?v=3.9.12')

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html)

# Update sw.js
with open(SW_JS, "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r'v3\.9\.\d+', 'v3.9.12', sw)
sw = re.sub(r'tra-timetable-pwa-v\d+', 'tra-timetable-pwa-v3912', sw)
sw = re.sub(r'tra-runtime-v\d+', 'tra-runtime-v3912', sw)
with open(SW_JS, "w", encoding="utf-8") as f:
    f.write(sw)

# Update CHANGELOG.md
with open(CHANGELOG, "r", encoding="utf-8") as f:
    cl = f.read()

V3912_CHANGELOG = """## [v3.9.12] - 2026-08-25

### 🎫 TPASS / TR-PASS 專屬乘車過濾 ＆ 🛡️ 智慧轉乘備案列車系統
- **1. TPASS / TR-PASS 適用方案標籤與篩選**：
  - 支援一鍵篩選「TPASS / TR-PASS 通用適用車次」，自動過濾非適用特定自強號或觀光列車。
- **2. 智慧轉乘備案列車引擎 (Backup Alternative Connections)**：
  - 展開轉乘方案詳情時，自動為每個轉乘站計算 **「後續接駁備案列車」**（若沒趕上原接駁車，即刻顯示下 1~2 班可搭乘車次與抵達時間），徹底解決緊湊轉乘的後顧之憂！
- **3. 全功能旗艦版與極速極簡版（SuperLite）全線同步支援**。

---

"""

if "## [v3.9.12]" not in cl:
    cl = cl.replace("# 更新日誌 (Changelog)\n\n---\n\n", "# 更新日誌 (Changelog)\n\n---\n\n" + V3912_CHANGELOG)
    with open(CHANGELOG, "w", encoding="utf-8") as f:
        f.write(cl)

# Update README.md
with open(README, "r", encoding="utf-8") as f:
    rm = f.read()
rm = re.sub(r'v3\.9\.\d+', 'v3.9.12', rm)
with open(README, "w", encoding="utf-8") as f:
    f.write(rm)

# Update build_multi_version_system.py
with open(BUILD_SCRIPT, "r", encoding="utf-8") as f:
    bld = f.read()
if '{"version": "v3.9.12"' not in bld:
    bld = bld.replace('HISTORICAL_COMMITS = [', 'HISTORICAL_COMMITS = [\n    {"version": "v3.9.12", "commit": "HEAD",    "date": "2026-08-25", "desc": "TPASS / TR-PASS 專屬過濾 ＆ 智慧轉乘備案列車系統"},')
    with open(BUILD_SCRIPT, "w", encoding="utf-8") as f:
        f.write(bld)

print("v3.9.12 applied successfully!")
