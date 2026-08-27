# -*- coding: utf-8 -*-
import json
import re

print("Integrating Favorites and Recent Searches into lite.html...")

with open('lite.html', 'r', encoding='utf-8') as f:
    lite = f.read()

lite_fav_css = """
        /* Favorites and Recent Searches */
        .fav-bar {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            padding: 10px 12px;
            margin-bottom: 12px;
        }
        .fav-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        .fav-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        .fav-chip {
            background: var(--bg-subtle);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 4px 10px;
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--text-color);
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .fav-chip:hover {
            border-color: var(--primary);
            color: var(--primary);
        }
        .btn-add-fav-lite {
            background: #f59e0b;
            color: #fff;
            border: none;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            cursor: pointer;
        }
"""

if '.fav-bar' not in lite:
    lite = lite.replace('</style>', lite_fav_css + '\n    </style>')

lite_fav_html = """        <!-- Favorites Bar -->
        <div class="fav-bar">
            <div class="fav-header">
                <span style="font-size:0.8rem; font-weight:700; color:var(--primary);">⭐ 常用路線快速切換</span>
                <button class="btn-add-fav-lite" onclick="saveCurrentFavLite()">⭐ 收藏目前路線</button>
            </div>
            <div class="fav-chips" id="liteFavChips"></div>
        </div>
"""

if 'id="liteFavChips"' not in lite:
    lite = lite.replace('<div class="quick-preset-bar">', lite_fav_html + '\n        <div class="quick-preset-bar">')

lite_fav_js = """
        const DEFAULT_FAVS_LITE = [
            { orig: '板橋', dest: '台北' },
            { orig: '台北', dest: '台中' },
            { orig: '板橋', dest: '車埕' },
            { orig: '集集', dest: '板橋' },
            { orig: '內灣', dest: '六家' }
        ];

        function renderLiteFavs() {
            const container = document.getElementById('liteFavChips');
            if (!container) return;
            let favs = [];
            try {
                const raw = localStorage.getItem('tra_pwa_favorite_routes_v1');
                if (raw) favs = JSON.parse(raw);
            } catch (e) {}
            if (!favs || favs.length === 0) favs = DEFAULT_FAVS_LITE;

            container.innerHTML = favs.map((f, idx) => {
                const sts = f.stations || [f.orig, f.dest];
                const routeStr = sts.join(' ➔ ');
                return `
                    <div class="fav-chip" onclick="applyFavLite(${idx})">
                        ⭐ ${routeStr}
                    </div>
                `;
            }).join('');
        }

        function saveCurrentFavLite() {
            if (!waypoints || waypoints.length < 2) return;
            const sts = waypoints.map(w => w.station).filter(Boolean);
            if (sts.length < 2) return;
            let favs = [];
            try {
                const raw = localStorage.getItem('tra_pwa_favorite_routes_v1');
                if (raw) favs = JSON.parse(raw);
            } catch (e) {}
            if (!favs) favs = [];
            favs.unshift({ stations: sts });
            try {
                localStorage.setItem('tra_pwa_favorite_routes_v1', JSON.stringify(favs.slice(0, 10)));
            } catch (e) {}
            renderLiteFavs();
        }

        function applyFavLite(idx) {
            let favs = [];
            try {
                const raw = localStorage.getItem('tra_pwa_favorite_routes_v1');
                if (raw) favs = JSON.parse(raw);
            } catch (e) {}
            if (!favs || favs.length === 0) favs = DEFAULT_FAVS_LITE;
            const f = favs[idx];
            if (!f) return;
            const sts = f.stations || [f.orig, f.dest];
            waypoints = sts.map(s => ({ station: s, minStay: 0 }));
            renderWaypointsUI();
            runSearch();
        }
"""

if 'function renderLiteFavs' not in lite:
    lite = lite.replace('window.addEventListener(\'DOMContentLoaded\', () => {', lite_fav_js + '\n        window.addEventListener(\'DOMContentLoaded\', () => {')
    lite = lite.replace('renderWaypointsUI();', 'renderWaypointsUI();\n            renderLiteFavs();')

with open('lite.html', 'w', encoding='utf-8') as f:
    f.write(lite)

print("lite.html updated with Favorites successfully!")
