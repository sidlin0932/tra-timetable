# -*- coding: utf-8 -*-
"""
Fixes Station Modal vertical scrolling and SVG map rendering to look ultra-clean and spacious.
"""

import re
from pathlib import Path
from build_perfect_taiwan_map import generate_clean_svg

BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML = BASE_DIR / "index.html"

with open(INDEX_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update CSS in index.html to ensure 100% smooth scrolling on both List & Map
PERFECT_MODAL_CSS = """
        /* =========================================================
           v3.9.0 Station Modal Layout & Guaranteed Smooth Scrolling
           ========================================================= */
        .modal-backdrop {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(15, 23, 42, 0.65);
            backdrop-filter: blur(6px);
            -webkit-backdrop-filter: blur(6px);
            z-index: 1000;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 16px;
        }
        .modal-backdrop.open { display: flex; }

        .modal-dialog {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            max-width: 960px;
            width: 100%;
            height: 86vh;
            max-height: 86vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.35);
            overflow: hidden;
        }

        .modal-header {
            padding: 14px 20px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--bg-card);
            flex-shrink: 0;
        }

        .modal-view-mode-bar {
            display: flex;
            background: var(--bg-subtle);
            border-bottom: 1px solid var(--border-color);
            padding: 8px 20px;
            gap: 10px;
            align-items: center;
            flex-shrink: 0;
        }
        .modal-view-btn {
            background: var(--bg-card);
            border: 1.5px solid var(--border-color);
            color: var(--text-muted);
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .modal-view-btn:hover {
            border-color: var(--primary);
            color: var(--primary);
        }
        .modal-view-btn.active {
            background: var(--primary);
            color: #ffffff;
            border-color: var(--primary);
            box-shadow: 0 2px 6px rgba(2, 132, 199, 0.35);
        }

        .modal-search-box {
            padding: 10px 20px 6px;
            background: var(--bg-card);
            flex-shrink: 0;
        }
        .modal-filter-input {
            width: 100%;
            padding: 9px 14px;
            border: 1.5px solid var(--border-color);
            border-radius: 10px;
            background: var(--bg-subtle);
            color: var(--text-main);
            font-size: 0.92rem;
            outline: none;
            box-sizing: border-box;
        }
        .modal-filter-input:focus {
            border-color: var(--primary);
            background: var(--bg-card);
        }

        /* --- List View Container & Scroll Area --- */
        #modalListView {
            display: flex;
            flex-direction: column;
            flex: 1;
            min-height: 0;
            overflow: hidden;
        }

        .county-filter-panel {
            padding: 8px 20px 10px;
            background: var(--bg-subtle);
            border-bottom: 1px solid var(--border-color);
            flex-shrink: 0;
        }
        .county-filter-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 8px;
        }
        .county-filter-title {
            font-size: 0.82rem;
            font-weight: 800;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .county-batch-actions {
            display: flex;
            gap: 6px;
        }
        .btn-batch-county {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 0.75rem;
            font-weight: 700;
            padding: 3px 9px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.15s;
        }
        .btn-batch-county:hover {
            background: var(--primary);
            color: #fff;
            border-color: var(--primary);
        }

        .county-checkbox-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            max-height: none !important;
            overflow: visible !important;
        }
        .county-check-label {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: var(--bg-card);
            border: 1.5px solid var(--border-color);
            padding: 5px 11px;
            border-radius: 16px;
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--text-muted);
            cursor: pointer;
            user-select: none;
            transition: all 0.15s ease;
            line-height: 1.2;
        }
        .county-check-label:hover {
            border-color: var(--primary);
            color: var(--text-main);
        }
        .county-check-label.checked {
            background: var(--primary-light);
            border-color: var(--primary);
            color: var(--primary);
            font-weight: 800;
        }
        .county-check-label input[type="checkbox"] {
            margin: 0;
            accent-color: var(--primary);
            cursor: pointer;
        }

        .hub-legend-bar {
            padding: 6px 20px;
            background: var(--bg-card);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
            font-size: 0.76rem;
            color: var(--text-muted);
            flex-shrink: 0;
        }
        .hub-legend-tag {
            padding: 2px 8px;
            border-radius: 6px;
            font-weight: 700;
        }

        /* The scrollable station grid body */
        #modalStationList {
            padding: 16px 20px 32px;
            overflow-y: auto !important;
            flex: 1 !important;
            min-height: 0 !important;
            -webkit-overflow-scrolling: touch;
        }

        .county-section {
            margin-bottom: 24px;
        }
        .county-section-title {
            font-size: 0.95rem;
            font-weight: 800;
            color: var(--primary);
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 6px;
            border-bottom: 2px solid var(--primary-light);
            padding-bottom: 4px;
        }
        .station-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(92px, 1fr));
            gap: 8px;
        }
        .station-btn {
            background: var(--bg-subtle);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 9px 6px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 700;
            cursor: pointer;
            text-align: center;
            transition: all 0.15s;
        }
        .station-btn:hover {
            background: var(--primary);
            color: #fff;
            border-color: var(--primary);
            transform: translateY(-1px);
            box-shadow: 0 3px 6px rgba(2, 132, 199, 0.25);
        }
        .station-btn.express-hub {
            background: #fff1f2;
            border: 1.5px solid #f43f5e;
            color: #be123c;
            font-weight: 800;
        }
        .station-btn.express-hub:hover {
            background: #e11d48;
            color: #fff;
            border-color: #e11d48;
        }
        .station-btn.branch-station {
            background: #f0fdf4;
            border: 1.5px solid #86efac;
            color: #166534;
        }
        .station-btn.branch-station:hover {
            background: #16a34a;
            color: #fff;
            border-color: #16a34a;
        }

        /* --- Map View Container & Scroll Area --- */
        #modalMapView {
            display: none;
            flex-direction: column;
            flex: 1;
            min-height: 0;
            overflow-y: auto !important;
            -webkit-overflow-scrolling: touch;
            background: var(--bg-page);
        }
        .taiwan-map-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 12px 16px 36px;
            width: 100%;
            box-sizing: border-box;
        }
        .map-toolbar {
            width: 100%;
            max-width: 640px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 12px;
            padding: 8px 14px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            box-sizing: border-box;
        }
        .map-hint-box {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.78rem;
            color: var(--text-main);
        }
        .map-hint-icon { font-size: 1rem; }
        .map-legend {
            display: flex;
            gap: 12px;
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-muted);
        }
        .legend-item { display: inline-flex; align-items: center; gap: 5px; }
        .legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
        .legend-dot.hub { background: #ef4444; border: 1.5px solid #fff; }
        .legend-dot.branch { background: #10b981; border: 1.5px solid #fff; }
        .legend-dot.main { background: #3b82f6; border: 1.5px solid #fff; }

        .map-viewport {
            width: 100%;
            max-width: 580px;
            display: flex;
            justify-content: center;
        }
        .taiwan-rail-svg {
            width: 100%;
            height: auto;
            max-height: 600px;
            display: block;
            user-select: none;
        }
        .taiwan-island-bg { transition: fill 0.3s ease; }
        [data-theme="dark"] .taiwan-island-bg {
            fill: #16281e !important;
            stroke: #2e553c !important;
        }
        .county-shape {
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .county-shape:hover {
            fill: #bae6fd !important;
            opacity: 0.85;
        }
        .map-label-pill {
            cursor: pointer;
            transition: all 0.2s ease;
            text-shadow: 0 1px 2px rgba(255,255,255,0.85);
        }
        [data-theme="dark"] .map-label-pill {
            fill: #86efac !important;
            text-shadow: 0 1px 2px rgba(0,0,0,0.85);
        }
        .map-label-pill:hover {
            fill: #0284c7 !important;
            font-weight: 900;
        }

        .map-station-node {
            cursor: pointer;
            transition: transform 0.15s ease;
        }
        .station-hitbox {
            cursor: pointer;
            pointer-events: all;
            fill: transparent !important;
            stroke: none !important;
        }
        .map-station-node:hover .station-dot {
            transform: scale(1.4);
            transform-origin: center;
            filter: drop-shadow(0 0 5px #0284c7);
        }
        .map-station-node:hover .map-station-name {
            font-size: 12px;
            font-weight: 900;
            fill: #0284c7 !important;
        }
        .map-station-name {
            pointer-events: none;
            user-select: none;
            transition: all 0.15s ease;
            text-shadow: 
                0 1px 3px rgba(255,255,255,0.95), 
                0 -1px 3px rgba(255,255,255,0.95), 
                1px 0 3px rgba(255,255,255,0.95), 
                -1px 0 3px rgba(255,255,255,0.95);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang TC", "Microsoft JhengHei", sans-serif;
        }
        [data-theme="dark"] .map-station-name {
            text-shadow: 
                0 1px 3px rgba(0,0,0,0.95), 
                0 -1px 3px rgba(0,0,0,0.95), 
                1px 0 3px rgba(0,0,0,0.95), 
                -1px 0 3px rgba(0,0,0,0.95);
            fill: #f8fafc;
        }
"""

# Replace in index.html
html = re.sub(r'/\* ==========================================\s*v3\.9\.0 Network Status & Station Modal UI[\s\S]*?</style>', PERFECT_MODAL_CSS + "\n    </style>", html)

# Inject clean SVG
svg_code = generate_clean_svg()
modal_map_pattern = re.compile(r'<div id="modalMapView"[^>]*>[\s\S]*?</div>\s*</div>\s*</div>\s*(?=<script)', re.MULTILINE)
replacement = f'''<div id="modalMapView" style="display: none;">
                {svg_code}
            </div>
        </div>
    </div>'''

html = modal_map_pattern.sub(replacement + "\n", html)

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Modal scrolling and SVG styling successfully perfected in index.html!")
