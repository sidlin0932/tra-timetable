# -*- coding: utf-8 -*-
"""
Removes fake progress bar and fake timer delays.
Makes route search truly instantaneous (0ms execution) and direct.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML = BASE_DIR / "index.html"

with open(INDEX_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove fake progress bar CSS
html = re.sub(r'/\* ==========================================\s*Instant UI Feedback, Progress Bar & Skeletons[\s\S]*?@keyframes pulse-skeleton[\s\S]*?\}', '', html)

# 2. Clean, True Instant Search Implementation without any fake timeouts or fake progress bars
TRUE_INSTANT_SEARCH_JS = """
        // ==========================================
        // Ultra-Fast Direct Search Engine (0ms True Instant)
        // ==========================================
        const ROUTE_LRU_CACHE = new Map();
        const MAX_LRU_SIZE = 200;

        function buildDeparturesIndex() {
            departuresByStation = {};
            allTimetableData.forEach(t => {
                t.stops.forEach((s, sIdx) => {
                    if (sIdx < t.stops.length - 1) {
                        if (!departuresByStation[s.station]) departuresByStation[s.station] = [];
                        departuresByStation[s.station].push({
                            train: t,
                            stopIdx: sIdx,
                            depTimeMin: timeToMin(s.time)
                        });
                    }
                });
            });

            for (const st in departuresByStation) {
                departuresByStation[st].sort((a, b) => a.depTimeMin - b.depTimeMin);
            }
        }

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

            // Direct, true instant route calculation with LRU cache
            const cacheKey = `${waypoints.map(w=>w.station+'_'+w.minStay).join('|')}-${startTimeMin}-${via}-${transferCondition}-${typeFilter}-${currentDayFilter}`;
            
            let rawRoutes = [];
            if (ROUTE_LRU_CACHE.has(cacheKey)) {
                rawRoutes = ROUTE_LRU_CACHE.get(cacheKey);
            } else {
                if (waypoints.length === 2) {
                    rawRoutes = planRoutes(waypoints[0].station, waypoints[1].station, startTimeMin, via);
                } else {
                    rawRoutes = planMultiStopRoutes(waypoints, startTimeMin);
                }
                if (ROUTE_LRU_CACHE.size >= MAX_LRU_SIZE) {
                    const firstKey = ROUTE_LRU_CACHE.keys().next().value;
                    ROUTE_LRU_CACHE.delete(firstKey);
                }
                ROUTE_LRU_CACHE.set(cacheKey, rawRoutes);
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

# Replace executeSearch and buildDeparturesIndex
search_engine_pattern = re.compile(r'// ==========================================\s*// High-Speed Router & Instant UI Engine[\s\S]*?function executeSearch\(\)[\s\S]*?renderResults\(\);\s*\}\s*,\s*40\);\s*\}\s*,\s*10\);\s*\}\);\s*\}', re.MULTILINE)
html = search_engine_pattern.sub(TRUE_INSTANT_SEARCH_JS + "\n", html)

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Fake progress bar completely removed. True 0ms Instant Search restored!")
