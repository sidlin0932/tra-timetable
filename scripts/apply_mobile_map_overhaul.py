# -*- coding: utf-8 -*-
"""
Applies mobile-first, ultra-clear interactive Taiwan Railway Transit Map to index.html.
"""

import re
from pathlib import Path
from build_mobile_first_map import build_map_component, REGIONS_CONFIG

BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML = BASE_DIR / "index.html"

with open(INDEX_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# 1. CSS for Mobile-First Map
MOBILE_MAP_CSS = """
        /* =========================================================
           v3.9.2 Mobile-First Interactive Taiwan Railway Transit Map
           ========================================================= */
        .taiwan-map-wrapper {
            display: flex;
            flex-direction: column;
            width: 100%;
            height: 100%;
            flex: 1;
            min-height: 0;
            position: relative;
            background: var(--bg-page);
        }
        .map-region-tabs {
            display: flex;
            gap: 6px;
            padding: 8px 16px;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            background: var(--bg-subtle);
            border-bottom: 1px solid var(--border-color);
            flex-shrink: 0;
        }
        .map-region-tabs::-webkit-scrollbar { display: none; }
        .region-tab-btn {
            padding: 7px 15px;
            border-radius: 20px;
            border: 1.5px solid var(--border-color);
            background: var(--bg-card);
            font-size: 0.82rem;
            font-weight: 700;
            color: var(--text-main);
            white-space: nowrap;
            cursor: pointer;
            transition: all 0.2s ease;
            -webkit-tap-highlight-color: transparent;
        }
        .region-tab-btn:hover {
            border-color: var(--primary);
            color: var(--primary);
        }
        .region-tab-btn.active {
            background: var(--primary);
            color: #ffffff;
            border-color: var(--primary);
            box-shadow: 0 2px 8px rgba(2, 132, 199, 0.35);
        }
        .map-instruction-banner {
            padding: 7px 16px;
            background: #f0f9ff;
            color: #0369a1;
            font-size: 0.8rem;
            font-weight: 700;
            text-align: center;
            border-bottom: 1px solid #bae6fd;
            flex-shrink: 0;
        }
        [data-theme="dark"] .map-instruction-banner {
            background: #082f49;
            color: #7dd3fc;
            border-bottom-color: #0369a1;
        }

        .map-svg-container {
            flex: 1;
            min-height: 0;
            overflow: auto;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 12px;
            -webkit-overflow-scrolling: touch;
        }
        .taiwan-rail-svg {
            width: 100%;
            max-width: 600px;
            height: auto;
            max-height: 520px;
            display: block;
            user-select: none;
            transition: all 0.35s ease;
        }
        .taiwan-island-bg {
            transition: fill 0.3s ease;
        }
        [data-theme="dark"] .taiwan-island-bg {
            fill: #14281d !important;
            stroke: #166534 !important;
        }

        .map-station-node {
            cursor: pointer;
            -webkit-tap-highlight-color: transparent;
            touch-action: manipulation;
        }
        .station-touch-hitbox {
            cursor: pointer;
            pointer-events: all;
            fill: transparent !important;
        }
        .map-station-node:hover .station-dot,
        .map-station-node:active .station-dot {
            transform: scale(1.45);
            transform-origin: center;
            filter: drop-shadow(0 0 6px #0284c7);
        }
        .map-station-node:hover .map-station-name,
        .map-station-node:active .map-station-name {
            font-size: 13.5px;
            font-weight: 900;
            fill: #0284c7 !important;
        }
        .map-station-name {
            pointer-events: none;
            user-select: none;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang TC", "Microsoft JhengHei", sans-serif;
            text-shadow: 
                0 0 3px #ffffff, 0 0 3px #ffffff, 
                0 0 5px #ffffff, 0 0 5px #ffffff,
                1px 1px 2px rgba(255,255,255,0.9);
        }
        [data-theme="dark"] .map-station-name {
            text-shadow: 
                0 0 3px #0f172a, 0 0 3px #0f172a, 
                0 0 5px #0f172a, 0 0 5px #0f172a;
            fill: #f8fafc !important;
        }

        .map-action-sheet {
            position: absolute;
            bottom: 14px;
            left: 16px;
            right: 16px;
            background: var(--bg-card);
            border: 2px solid var(--primary);
            border-radius: 16px;
            padding: 12px 16px;
            box-shadow: 0 16px 36px rgba(0,0,0,0.35);
            z-index: 20;
            display: flex;
            flex-direction: column;
            gap: 8px;
            animation: sheetSlideUp 0.2s ease;
        }
        @keyframes sheetSlideUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .action-sheet-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .action-station-badge {
            font-size: 1.1rem;
            font-weight: 900;
            color: var(--primary);
        }
        .action-sheet-close {
            background: none;
            border: none;
            font-size: 1.2rem;
            color: var(--text-muted);
            cursor: pointer;
            padding: 4px;
        }
        .action-sheet-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 8px;
        }
        .btn-sheet-action {
            padding: 10px 4px;
            border-radius: 10px;
            font-weight: 800;
            font-size: 0.85rem;
            border: none;
            cursor: pointer;
            text-align: center;
            transition: all 0.15s;
        }
        .btn-sheet-action.dep {
            background: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
        }
        .btn-sheet-action.arr {
            background: #f0fdf4;
            color: #15803d;
            border: 1px solid #bbf7d0;
        }
        .btn-sheet-action.via {
            background: #fefce8;
            color: #a16207;
            border: 1px solid #fef08a;
        }
        .btn-sheet-action:active {
            transform: scale(0.96);
        }
"""

# Replace old map CSS
html = re.sub(r'/\* ==========================================\s*v3\.9\.0 High-End SVG Map Aesthetics[\s\S]*?</style>', MOBILE_MAP_CSS + "\n    </style>", html)

# Replace #modalMapView with new mobile-first map component
map_component_html = build_map_component()
map_pattern = re.compile(r'<div id="modalMapView"[^>]*>[\s\S]*?</div>\s*</div>\s*</div>\s*(?=<script)', re.MULTILINE)
replacement = f'''<div id="modalMapView" style="display: none;">
                {map_component_html}
            </div>
        </div>
    </div>'''

html = map_pattern.sub(replacement + "\n", html)

# Add JS functions for Region Zoom and Map Actions
MAP_JS = """
        // ==========================================
        // Mobile-First Map Interaction System
        // ==========================================
        let selectedMapStation = '';
        const MAP_REGIONS = {
            'all': '40 10 440 700',
            'north': '80 20 380 280',
            'central': '60 240 220 280',
            'south': '60 460 220 260',
            'east': '210 50 250 660',
            'branch': '90 50 360 450'
        };

        function zoomMapRegion(regionKey, btnEl) {
            const svg = document.getElementById('taiwanRailSvg');
            if (svg && MAP_REGIONS[regionKey]) {
                svg.setAttribute('viewBox', MAP_REGIONS[regionKey]);
            }
            const tabs = document.querySelectorAll('#mapRegionTabs .region-tab-btn');
            tabs.forEach(t => t.classList.remove('active'));
            if (btnEl) btnEl.classList.add('active');
        }

        function openMapStationAction(stName, e) {
            if (e) {
                e.preventDefault();
                e.stopPropagation();
            }
            selectedMapStation = stName;
            
            // If user opened modal to pick a specific waypoint or via, pick directly for 1-tap experience!
            modalPickStation(stName);
        }

        function closeMapActionSheet() {
            const sheet = document.getElementById('mapStationActionSheet');
            if (sheet) sheet.style.display = 'none';
        }

        function confirmMapStationPick(targetRole) {
            if (!selectedMapStation) return;
            if (targetRole === 'origin') {
                waypoints[0].station = selectedMapStation;
            } else if (targetRole === 'dest') {
                waypoints[waypoints.length - 1].station = selectedMapStation;
            } else if (targetRole === 'via') {
                const viaInput = document.getElementById('viaInput');
                if (viaInput) viaInput.value = selectedMapStation;
            }
            closeMapActionSheet();
            closeStationModal();
            renderWaypointsUI();
            executeSearch();
        }
"""

if "zoomMapRegion" not in html:
    html = html.replace("    </script>", MAP_JS + "\n    </script>")

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Mobile-first map overhaul successfully applied!")
