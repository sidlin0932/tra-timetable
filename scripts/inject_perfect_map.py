# -*- coding: utf-8 -*-
"""
Injects the refined SVG map into index.html and cleans up styling.
"""

import re
from pathlib import Path
from build_perfect_taiwan_map import generate_clean_svg

BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML = BASE_DIR / "index.html"

with open(INDEX_HTML, "r", encoding="utf-8") as f:
    html = f.read()

svg_code = generate_clean_svg()

# Replace #modalMapView
pattern = re.compile(r'<div id="modalMapView"[^>]*>[\s\S]*?</div>\s*</div>\s*</div>\s*(?=<script)', re.MULTILINE)
replacement = f'''<div id="modalMapView" style="display: none;">
                {svg_code}
            </div>
        </div>
    </div>'''

if pattern.search(html):
    html = pattern.sub(replacement + "\n", html)
else:
    print("Direct replace fallback for modalMapView")

# Ensure CSS has perfect map styles
CLEAN_MAP_CSS = """
        /* ==========================================
           v3.9.0 High-End SVG Map Aesthetics
           ========================================== */
        .taiwan-map-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 10px 16px 20px;
            max-height: 68vh;
            overflow-y: auto;
            background: var(--bg-card);
        }
        .map-toolbar {
            width: 100%;
            max-width: 640px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 10px;
            padding: 8px 14px;
            background: var(--bg-subtle);
            border: 1px solid var(--border-color);
            border-radius: 10px;
        }
        .map-hint-box {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.78rem;
            color: var(--text-main);
        }
        .map-hint-icon {
            font-size: 1rem;
        }
        .map-legend {
            display: flex;
            gap: 12px;
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-muted);
        }
        .legend-item {
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }
        .legend-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }
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
            max-height: 560px;
            display: block;
            user-select: none;
        }
        .taiwan-island-bg {
            transition: fill 0.3s ease;
        }
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

        /* Stations on Map */
        .map-station-node {
            cursor: pointer;
            transition: transform 0.15s ease;
        }
        .station-hitbox {
            cursor: pointer;
            pointer-events: all;
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

# Replace map CSS
if "v3.9.0 High-End SVG Map Aesthetics" not in html:
    html = html.replace("    </style>", CLEAN_MAP_CSS + "\n    </style>")

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Perfect map applied to index.html!")
