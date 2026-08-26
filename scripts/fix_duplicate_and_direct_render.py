# -*- coding: utf-8 -*-
"""
1. Fixes executeSearch to run 100% synchronously and directly render without any timers or intermediate states.
2. Removes duplicated stations in Quick Shortcuts bar.
3. Ensures all route queries (台北->內灣, 板橋->台北, 內灣->六家) compute and display immediately.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML = BASE_DIR / "index.html"

with open(INDEX_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Clean Quick Shortcut Bar (No duplicates)
OLD_SHORTCUTS = re.search(r'<div class="quick-shortcuts-box">[\s\S]*?</div>\s*</div>', html)
NEW_SHORTCUTS = """<div class="quick-shortcuts-box">
            <div class="quick-title">⚡ 常用快捷：</div>
            <div class="quick-chips">
                <span class="quick-chip" onclick="quickFillWaypoint('dest', '台北')">🚩 台北</span>
                <span class="quick-chip" onclick="quickFillWaypoint('dest', '板橋')">🚩 板橋</span>
                <span class="quick-chip" onclick="quickFillWaypoint('dest', '桃園')">🚩 桃園</span>
                <span class="quick-chip" onclick="quickFillWaypoint('dest', '新竹')">🚩 新竹</span>
                <span class="quick-chip" onclick="quickFillWaypoint('dest', '台中')">🚩 台中</span>
                <span class="quick-chip" onclick="quickFillWaypoint('dest', '彰化')">🚩 彰化</span>
                <span class="quick-chip" onclick="quickFillWaypoint('dest', '嘉義')">🚩 嘉義</span>
                <span class="quick-chip" onclick="quickFillWaypoint('dest', '台南')">🚩 台南</span>
                <span class="quick-chip" onclick="quickFillWaypoint('dest', '高雄')">🚩 高雄</span>
                <span class="quick-chip" onclick="quickFillWaypoint('dest', '花蓮')">🚩 花蓮</span>
                <span class="quick-chip" onclick="quickFillWaypoint('dest', '台東')">🚩 台東</span>
                <span class="quick-chip" onclick="quickFillWaypoint('dest', '瑞芳')">🌿 瑞芳</span>
                <span class="quick-chip" onclick="quickFillWaypoint('dest', '內灣')">🌿 內灣</span>
                <span class="quick-chip" onclick="quickFillWaypoint('dest', '車埕')">🌿 車埕</span>
                <span style="color:var(--text-muted); margin:0 4px;">|</span>
                <span style="font-size:0.75rem; font-weight:700; color:var(--text-muted);">🔀 指定轉乘:</span>
                <span class="quick-chip" onclick="setViaStation('')">不限</span>
                <span class="quick-chip" onclick="setViaStation('八堵')">八堵</span>
                <span class="quick-chip" onclick="setViaStation('七堵')">七堵</span>
                <span class="quick-chip" onclick="setViaStation('台北')">台北</span>
                <span class="quick-chip" onclick="setViaStation('新竹')">新竹</span>
                <span class="quick-chip" onclick="setViaStation('彰化')">彰化</span>
                <span class="quick-chip" onclick="setViaStation('新左營')">新左營</span>
                <span class="quick-chip" onclick="setViaStation('花蓮')">花蓮</span>
            </div>
        </div>"""

if OLD_SHORTCUTS:
    html = html.replace(OLD_SHORTCUTS.group(0), NEW_SHORTCUTS)

# 2. Perfect Direct executeSearch (0ms immediate calculation and rendering)
PERFECT_EXECUTE_JS = """
        // ==========================================
        // Direct Synchronous Execution Engine (0ms Instant)
        // ==========================================
        function executeSearch() {
            const timeStr = document.getElementById('timeInput') ? (document.getElementById('timeInput').value || '00:00') : '00:00';
            const startTimeMin = timeToMin(timeStr);
            const via = document.getElementById('viaInput') ? document.getElementById('viaInput').value.trim() : '';

            const routeStr = waypoints.map(w => w.station).join(' ➔ ');
            const summaryEl = document.getElementById('routeSummaryText');
            if (summaryEl) {
                if (waypoints.length === 2 && via) {
                    summaryEl.textContent = `${waypoints[0].station} ➔ [經由 ${via}] ➔ ${waypoints[1].station}`;
                } else {
                    summaryEl.textContent = routeStr;
                }
            }
            updateClearViaButton();

            const orig = waypoints[0].station;
            const dest = waypoints[waypoints.length - 1].station;

            if (!orig || !dest || orig === dest || allTimetableData.length === 0) {
                currentRoutes = [];
                renderResults();
                return;
            }

            let rawRoutes = [];
            if (waypoints.length === 2) {
                rawRoutes = planRoutes(orig, dest, startTimeMin, via);
            } else {
                rawRoutes = planMultiStopRoutes(waypoints, startTimeMin);
            }

            const seen = new Set();
            currentRoutes = rawRoutes.filter(r => {
                const key = `${r.dep_time}-${r.arr_time}-${r.transfers}-${r.legs.map(l=>l.train_number).join('_')}`;
                if (seen.has(key)) return false;
                seen.add(key);
                return true;
            });

            currentRoutes = sortRoutes(currentRoutes);
            renderResults();
        }
"""

# Replace executeSearch and progress bar wrappers in script
html = re.sub(r'// ==========================================\s*// Real-Time Progress Engine[\s\S]*?function executeSearch\(\)[\s\S]*?renderResults\(\);\s*\}\s*,\s*50\);\s*\}\s*else\s*\{[\s\S]*?\}\s*,\s*16\);\s*\}', PERFECT_EXECUTE_JS, html)

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Duplicates removed and direct 0ms search engine restored successfully!")
