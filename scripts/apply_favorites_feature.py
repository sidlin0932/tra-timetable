# -*- coding: utf-8 -*-
import json
import re

print("Integrating Feature 3: Favorites and Recent Searches...")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

fav_css = """
        /* ==========================================
           Favorites and Recent Searches Component CSS
           ========================================== */
        .fav-recent-bar {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 12px 16px;
            margin-bottom: 16px;
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
        }

        .fav-recent-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 10px;
        }

        .fav-tabs {
            display: inline-flex;
            background: var(--bg-subtle);
            padding: 3px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
            gap: 4px;
        }

        .fav-tab-btn {
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-size: 0.82rem;
            font-weight: 700;
            padding: 5px 12px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.15s ease;
        }

        .fav-tab-btn.active {
            background: var(--bg-card);
            color: var(--primary);
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }

        .btn-add-fav {
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: #ffffff;
            border: none;
            padding: 6px 14px;
            border-radius: var(--radius-sm);
            font-size: 0.82rem;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            box-shadow: 0 2px 4px rgba(245, 158, 11, 0.25);
            transition: all 0.2s ease;
        }

        .btn-add-fav:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(245, 158, 11, 0.35);
        }

        .fav-recent-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
        }

        .fav-chip {
            background: var(--bg-subtle);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 5px 12px;
            font-size: 0.84rem;
            font-weight: 700;
            color: var(--text-color);
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s ease;
        }

        .fav-chip:hover {
            background: var(--primary-light);
            border-color: var(--primary);
            color: var(--primary);
            transform: translateY(-1px);
        }

        .fav-chip .chip-route {
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }

        .fav-chip .chip-del {
            color: var(--text-muted);
            font-size: 0.75rem;
            padding: 2px 4px;
            border-radius: 50%;
            margin-left: 2px;
            transition: color 0.15s ease;
        }

        .fav-chip .chip-del:hover {
            color: #ef4444;
            background: rgba(239, 68, 68, 0.1);
        }

        .fav-empty-hint {
            font-size: 0.82rem;
            color: var(--text-muted);
            padding: 6px 4px;
        }
"""

if '.fav-recent-bar' not in html:
    html = html.replace('</style>', fav_css + '\n    </style>')

fav_html = """            <!-- Favorites & Recent Searches Bar -->
            <div class="fav-recent-bar" id="favRecentBar">
                <div class="fav-recent-header">
                    <div class="fav-tabs">
                        <button class="fav-tab-btn active" id="btnFavTab" onclick="switchFavTab('favorites')">⭐ 我的常用路線</button>
                        <button class="fav-tab-btn" id="btnRecentTab" onclick="switchFavTab('recent')">🕒 最近查詢紀錄</button>
                    </div>
                    <button class="btn-add-fav" id="btnAddFav" onclick="saveCurrentAsFavorite()" title="將目前起訖路線加入常用收藏">
                        <span>⭐ 收藏目前路線</span>
                    </button>
                </div>
                <div class="fav-recent-chips" id="favRecentChips">
                    <!-- Dynamic Favorite / Recent Chips -->
                </div>
            </div>
"""

if 'id="favRecentBar"' not in html:
    html = html.replace('<!-- Row 3: Quick Hubs Bar (Full Width) -->', fav_html + '\n            <!-- Row 3: Quick Hubs Bar (Full Width) -->')

fav_js = """
        // ==========================================
        // Favorites & Recent Search History Engine
        // ==========================================
        const STORAGE_KEY_FAVS = 'tra_pwa_favorite_routes_v1';
        const STORAGE_KEY_RECENT = 'tra_pwa_recent_search_history_v1';

        const DEFAULT_FAVORITES = [
            { stations: ['板橋', '台北'], desc: '雙北主幹線' },
            { stations: ['台北', '台中'], desc: '西部山線' },
            { stations: ['板橋', '車埕'], desc: '集集線去程' },
            { stations: ['集集', '板橋'], desc: '集集線回程' },
            { stations: ['內灣', '六家'], desc: '竹中跨支線' },
            { stations: ['台北', '花蓮'], desc: '東部幹線' }
        ];

        let currentFavTab = 'favorites'; // 'favorites' | 'recent'

        function getStoredFavorites() {
            try {
                const raw = localStorage.getItem(STORAGE_KEY_FAVS);
                if (raw) {
                    const parsed = JSON.parse(raw);
                    if (Array.isArray(parsed) && parsed.length > 0) return parsed;
                }
            } catch (e) {}
            return DEFAULT_FAVORITES;
        }

        function saveStoredFavorites(favs) {
            try {
                localStorage.setItem(STORAGE_KEY_FAVS, JSON.stringify(favs));
            } catch (e) {}
        }

        function getStoredRecent() {
            try {
                const raw = localStorage.getItem(STORAGE_KEY_RECENT);
                if (raw) {
                    const parsed = JSON.parse(raw);
                    if (Array.isArray(parsed)) return parsed;
                }
            } catch (e) {}
            return [];
        }

        function saveStoredRecent(recentList) {
            try {
                localStorage.setItem(STORAGE_KEY_RECENT, JSON.stringify(recentList.slice(0, 10)));
            } catch (e) {}
        }

        function switchFavTab(tab) {
            currentFavTab = tab;
            const btnFav = document.getElementById('btnFavTab');
            const btnRecent = document.getElementById('btnRecentTab');
            if (btnFav) btnFav.classList.toggle('active', tab === 'favorites');
            if (btnRecent) btnRecent.classList.toggle('active', tab === 'recent');
            renderFavRecentChips();
        }
        window.switchFavTab = switchFavTab;

        function renderFavRecentChips() {
            const container = document.getElementById('favRecentChips');
            if (!container) return;

            if (currentFavTab === 'favorites') {
                const favs = getStoredFavorites();
                if (favs.length === 0) {
                    container.innerHTML = '<span class="fav-empty-hint">尚未加入自訂常用路線，點擊右上角「⭐ 收藏目前路線」即可儲存！</span>';
                    return;
                }
                container.innerHTML = favs.map((fav, idx) => {
                    const routeStr = (fav.stations || [fav.orig, fav.dest]).filter(Boolean).join(' ➔ ');
                    return `
                        <div class="fav-chip" onclick="applyFavoriteRoute(${idx})" title="點擊立即查詢【${routeStr}】">
                            <span class="chip-route">⭐ ${routeStr}</span>
                            <span class="chip-del" onclick="removeFavoriteRoute(${idx}, event)" title="移除此收藏">✕</span>
                        </div>
                    `;
                }).join('');
            } else {
                const recents = getStoredRecent();
                if (recents.length === 0) {
                    container.innerHTML = '<span class="fav-empty-hint">尚無最近查詢紀錄。</span>';
                    return;
                }
                container.innerHTML = recents.map((rec, idx) => {
                    const routeStr = (rec.stations || [rec.orig, rec.dest]).filter(Boolean).join(' ➔ ');
                    return `
                        <div class="fav-chip" onclick="applyRecentRoute(${idx})" title="點擊立即重查【${routeStr}】">
                            <span class="chip-route">🕒 ${routeStr}</span>
                            <span class="chip-del" onclick="removeRecentRoute(${idx}, event)" title="刪除此紀錄">✕</span>
                        </div>
                    `;
                }).join('') + '<button class="quick-hub-btn" style="padding:4px 8px; font-size:0.75rem; margin-left:4px;" onclick="clearAllRecentRoutes()">🗑️ 清除紀錄</button>';
            }
        }
        window.renderFavRecentChips = renderFavRecentChips;

        function saveCurrentAsFavorite() {
            if (!waypoints || waypoints.length < 2) return;
            const stations = waypoints.map(w => w.station).filter(Boolean);
            if (stations.length < 2) {
                alert('請先選擇有效的起訖站！');
                return;
            }
            const favs = getStoredFavorites();
            const key = stations.join('__');
            if (favs.some(f => (f.stations || [f.orig, f.dest]).join('__') === key)) {
                alert(`路線【${stations.join(' ➔ ')}】已經在您的常用路線中了！`);
                return;
            }
            favs.unshift({ stations, date: new Date().toISOString() });
            saveStoredFavorites(favs);
            if (currentFavTab !== 'favorites') switchFavTab('favorites');
            else renderFavRecentChips();
        }
        window.saveCurrentAsFavorite = saveCurrentAsFavorite;

        function removeFavoriteRoute(idx, e) {
            if (e) e.stopPropagation();
            const favs = getStoredFavorites();
            favs.splice(idx, 1);
            saveStoredFavorites(favs);
            renderFavRecentChips();
        }
        window.removeFavoriteRoute = removeFavoriteRoute;

        function applyFavoriteRoute(idx) {
            const favs = getStoredFavorites();
            const fav = favs[idx];
            if (!fav) return;
            const sts = fav.stations || [fav.orig, fav.dest];
            waypoints = sts.map(s => ({ station: s, minStay: 0 }));
            renderWaypointsUI();
            executeSearch();
        }
        window.applyFavoriteRoute = applyFavoriteRoute;

        function applyRecentRoute(idx) {
            const recents = getStoredRecent();
            const rec = recents[idx];
            if (!rec) return;
            const sts = rec.stations || [rec.orig, rec.dest];
            waypoints = sts.map(s => ({ station: s, minStay: 0 }));
            renderWaypointsUI();
            executeSearch();
        }
        window.applyRecentRoute = applyRecentRoute;

        function removeRecentRoute(idx, e) {
            if (e) e.stopPropagation();
            const recents = getStoredRecent();
            recents.splice(idx, 1);
            saveStoredRecent(recents);
            renderFavRecentChips();
        }
        window.removeRecentRoute = removeRecentRoute;

        function clearAllRecentRoutes() {
            saveStoredRecent([]);
            renderFavRecentChips();
        }
        window.clearAllRecentRoutes = clearAllRecentRoutes;

        function recordRecentSearchAction() {
            if (!waypoints || waypoints.length < 2) return;
            const sts = waypoints.map(w => w.station).filter(Boolean);
            if (sts.length < 2) return;
            const recents = getStoredRecent();
            const key = sts.join('__');
            const filtered = recents.filter(r => (r.stations || [r.orig, r.dest]).join('__') !== key);
            filtered.unshift({ stations: sts, time: new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' }) });
            saveStoredRecent(filtered);
            if (currentFavTab === 'recent') renderFavRecentChips();
        }
"""

if 'function saveCurrentAsFavorite' not in html:
    html = html.replace('window.addEventListener(\'DOMContentLoaded\', () => {', fav_js + '\n        window.addEventListener(\'DOMContentLoaded\', () => {')
    html = html.replace('renderWaypointsUI();', 'renderWaypointsUI();\n            renderFavRecentChips();')
    html = html.replace('function executeSearch() {', 'function executeSearch() {\n            recordRecentSearchAction();')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated with Favorites and Recent Searches successfully!")
