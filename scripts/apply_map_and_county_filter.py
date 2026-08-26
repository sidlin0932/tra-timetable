# -*- coding: utf-8 -*-
"""
Applies Taiwan Rail SVG Map & Multi-Checkbox County Filter into index.html for v3.9.0
"""

import re
from pathlib import Path
from build_taiwan_map_component import generate_svg_markup

BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML = BASE_DIR / "index.html"

with open(INDEX_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Add CSS for View Switcher, County Checkboxes, and SVG Map
NEW_CSS = """
        /* ==========================================
           v3.9.0 Multi-County Checkbox & Map Styles
           ========================================== */
        .modal-view-mode-bar {
            display: flex;
            background: var(--bg-subtle);
            border-bottom: 1px solid var(--border-color);
            padding: 8px 24px;
            gap: 12px;
            align-items: center;
        }
        .modal-view-btn {
            background: var(--bg-card);
            border: 1.5px solid var(--border-color);
            color: var(--text-main);
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
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
            box-shadow: 0 2px 6px rgba(2, 132, 199, 0.3);
        }

        .county-filter-panel {
            padding: 10px 24px;
            background: var(--bg-subtle);
            border-bottom: 1px solid var(--border-color);
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
            font-size: 0.85rem;
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
            padding: 3px 8px;
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
            max-height: 110px;
            overflow-y: auto;
            scrollbar-width: thin;
        }
        .county-check-label {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background: var(--bg-card);
            border: 1.5px solid var(--border-color);
            padding: 4px 10px;
            border-radius: 14px;
            font-size: 0.78rem;
            font-weight: 700;
            color: var(--text-muted);
            cursor: pointer;
            user-select: none;
            transition: all 0.15s ease;
        }
        .county-check-label:hover {
            border-color: var(--primary);
            color: var(--text-main);
        }
        .county-check-label.checked {
            background: var(--primary-light);
            border-color: var(--primary);
            color: var(--primary);
            box-shadow: 0 1px 3px rgba(2, 132, 199, 0.15);
        }
        .county-check-label input[type="checkbox"] {
            accent-color: var(--primary);
            cursor: pointer;
        }

        /* SVG Map Container */
        .taiwan-map-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 12px 16px 24px;
            max-height: 68vh;
            overflow-y: auto;
            background: var(--bg-page);
        }
        .map-toolbar {
            width: 100%;
            max-width: 780px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 10px;
            padding: 8px 14px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
        }
        .map-hint {
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--primary);
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
            gap: 4px;
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
            max-width: 680px;
            display: flex;
            justify-content: center;
        }
        .taiwan-rail-svg {
            width: 100%;
            height: auto;
            max-height: 560px;
            background: transparent;
            user-select: none;
        }
        .taiwan-island-bg {
            transition: fill 0.3s;
        }
        [data-theme="dark"] .taiwan-island-bg {
            fill: #14281d !important;
            stroke: #2d5a3f !important;
        }
        .county-shape {
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .county-shape:hover {
            fill: #bae6fd !important;
            opacity: 0.9;
        }
        .map-label-pill {
            cursor: pointer;
            transition: all 0.2s ease;
            text-shadow: 0 1px 2px rgba(255,255,255,0.8);
        }
        [data-theme="dark"] .map-label-pill {
            fill: #86efac !important;
            text-shadow: 0 1px 2px rgba(0,0,0,0.8);
        }
        .map-label-pill:hover {
            fill: #0284c7 !important;
            font-size: 13px;
        }

        /* Tracks */
        .rail-track-base {
            fill: none;
            stroke: #1e293b;
            stroke-width: 4.5;
            stroke-linecap: round;
            stroke-linejoin: round;
        }
        .rail-track-dashed {
            fill: none;
            stroke: #ffffff;
            stroke-width: 2.2;
            stroke-dasharray: 5 4;
            stroke-linecap: butt;
        }
        .rail-branch-base {
            fill: none;
            stroke: #d97706;
            stroke-width: 3.5;
            stroke-dasharray: 4 3;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        /* Station nodes on map */
        .map-station-node {
            cursor: pointer;
            transition: transform 0.15s ease;
        }
        .map-station-node:hover .station-dot {
            transform: scale(1.35);
            transform-origin: center;
            filter: drop-shadow(0 0 4px #0284c7);
        }
        .map-station-node:hover .station-label {
            font-size: 12.5px;
            font-weight: 900;
            fill: #0284c7 !important;
        }
        .station-hitbox {
            fill: transparent;
            cursor: pointer;
        }
        .station-dot {
            transition: transform 0.15s ease;
        }
        .station-label {
            pointer-events: none;
            transition: all 0.15s ease;
            text-shadow: 0 1px 2px rgba(255,255,255,0.95), 0 -1px 2px rgba(255,255,255,0.95);
        }
        [data-theme="dark"] .station-label {
            text-shadow: 0 1px 2px rgba(0,0,0,0.95), 0 -1px 2px rgba(0,0,0,0.95);
            fill: #f1f5f9;
        }
"""

# Insert CSS before </style>
html = html.replace("    </style>", NEW_CSS + "\n    </style>")

# 2. Update Station Modal HTML Structure
svg_map_html = generate_svg_markup()

MODAL_HTML_REPLACEMENT = f"""    <!-- County-classified Station Modal -->
    <div class="modal-backdrop" id="stationModal" onclick="closeStationModal(event)">
        <div class="modal-dialog" onclick="event.stopPropagation()">
            <div class="modal-header">
                <div>
                    <h3 id="modalTitle">🗺️ 快速選站（全台 17 縣市 & 鐵路地圖）</h3>
                    <div class="modal-trip-stepper" id="modalTripStepper">
                        <button class="modal-step-btn active" id="modalStep-0" onclick="setModalTarget('waypoint-0')">
                            <span class="step-icon">🚩</span>
                            <span class="step-label">出發:</span>
                            <strong id="modalOriginVal">板橋</strong>
                        </button>
                        <span class="modal-step-arrow">➔</span>
                        <button class="modal-step-btn" id="modalStep-1" onclick="setModalTarget('waypoint-1')">
                            <span class="step-icon">🏁</span>
                            <span class="step-label">抵達:</span>
                            <strong id="modalDestVal">台北</strong>
                        </button>
                    </div>
                </div>
                <button class="btn-modal-close" onclick="closeStationModal()">&times;</button>
            </div>

            <!-- View Mode Switcher -->
            <div class="modal-view-mode-bar">
                <button class="modal-view-btn active" id="btnViewList" onclick="setModalViewMode('list')">
                    <span>📋 縣市勾選清單</span>
                </button>
                <button class="modal-view-btn" id="btnViewMap" onclick="setModalViewMode('map')">
                    <span>🗺️ 台灣鐵路地圖模式</span>
                </button>
            </div>
            
            <div class="modal-search-box">
                <input type="text" id="modalSearchInput" class="modal-filter-input" placeholder="🔍 快速搜尋站名 (如: 台北、新竹、台中、花蓮、車埕)..." oninput="filterModalStations()">
            </div>

            <!-- Mode 1: List with Multi-County Checkbox Filter -->
            <div id="modalListView">
                <div class="county-filter-panel">
                    <div class="county-filter-header">
                        <div class="county-filter-title">
                            <span>📍 勾選縣市過濾 (未勾選自動隱藏):</span>
                            <span id="selectedCountiesCount" style="font-size:0.75rem; color:var(--primary); font-weight:700;">(已選 17 縣市)</span>
                        </div>
                        <div class="county-batch-actions">
                            <button class="btn-batch-county" onclick="toggleAllCounties(true)">全選</button>
                            <button class="btn-batch-county" onclick="toggleAllCounties(false)">全清</button>
                            <button class="btn-batch-county" onclick="invertCountiesSelection()">反選</button>
                        </div>
                    </div>
                    <div class="county-checkbox-grid" id="modalCountyTabs"></div>
                </div>

                <div class="hub-legend-bar">
                    <span>圖例說明：</span>
                    <span class="hub-legend-tag" style="background:#ffe4e6; border:1px solid #f43f5e; color:#be123c;">⭐ 紅色為自強號大站</span>
                    <span class="hub-legend-tag" style="background:#f0fdf4; border:1px solid #86efac; color:#166534;">🌿 淺綠為觀光支線小站</span>
                    <span class="hub-legend-tag" style="background:var(--bg-subtle); border:1px solid var(--border-color); color:var(--text-main);">一般幹線車站</span>
                </div>

                <div class="modal-body" id="modalStationList"></div>
            </div>

            <!-- Mode 2: Interactive SVG Map Mode -->
            <div id="modalMapView" style="display: none;">
                {svg_map_html}
            </div>
        </div>
    </div>"""

# Replace stationModal section in HTML
modal_pattern = re.compile(r'<!-- County-classified Station Modal -->[\s\S]*?</div>\s*</div>\s*(?=<script)', re.MULTILINE)
html = modal_pattern.sub(MODAL_HTML_REPLACEMENT + "\n", html)

# 3. Update JavaScript logic for modal view modes and county multi-checkboxes
JS_LOGIC = """
        // ==========================================
        // v3.9.0 Multi-County Checkbox & Map System
        // ==========================================
        let modalViewMode = 'list'; // 'list' | 'map'
        let selectedCounties = new Set(COUNTY_GROUPS.map(g => g.county));

        function setModalViewMode(mode) {
            modalViewMode = mode;
            const btnList = document.getElementById('btnViewList');
            const btnMap = document.getElementById('btnViewMap');
            const listView = document.getElementById('modalListView');
            const mapView = document.getElementById('modalMapView');

            if (mode === 'list') {
                if (btnList) btnList.classList.add('active');
                if (btnMap) btnMap.classList.remove('active');
                if (listView) listView.style.display = 'block';
                if (mapView) mapView.style.display = 'none';
            } else {
                if (btnList) btnList.classList.remove('active');
                if (btnMap) btnMap.classList.add('active');
                if (listView) listView.style.display = 'none';
                if (mapView) mapView.style.display = 'block';
            }
        }

        function toggleCountyCheckbox(county, isChecked) {
            if (isChecked) {
                selectedCounties.add(county);
            } else {
                selectedCounties.delete(county);
            }
            updateCountyCheckboxesUI();
            filterModalStations();
        }

        function toggleAllCounties(state) {
            if (state) {
                selectedCounties = new Set(COUNTY_GROUPS.map(g => g.county));
            } else {
                selectedCounties.clear();
            }
            updateCountyCheckboxesUI();
            filterModalStations();
        }

        function invertCountiesSelection() {
            const newSet = new Set();
            COUNTY_GROUPS.forEach(g => {
                if (!selectedCounties.has(g.county)) {
                    newSet.add(g.county);
                }
            });
            selectedCounties = newSet;
            updateCountyCheckboxesUI();
            filterModalStations();
        }

        function filterByCountyFromMap(county) {
            selectedCounties = new Set([county]);
            setModalViewMode('list');
            updateCountyCheckboxesUI();
            filterModalStations();
            const sec = document.getElementById(`county-sec-${county}`);
            if (sec) {
                const container = document.getElementById('modalStationList');
                if (container) {
                    container.scrollTo({ top: sec.offsetTop - 6, behavior: 'smooth' });
                }
            }
        }

        function updateCountyCheckboxesUI() {
            const countLabel = document.getElementById('selectedCountiesCount');
            if (countLabel) {
                countLabel.textContent = `(已選 ${selectedCounties.size} / ${COUNTY_GROUPS.length} 縣市)`;
            }
            const labels = document.querySelectorAll('.county-check-label');
            labels.forEach(lbl => {
                const county = lbl.getAttribute('data-county');
                const cb = lbl.querySelector('input[type="checkbox"]');
                const isChecked = selectedCounties.has(county);
                if (cb) cb.checked = isChecked;
                if (isChecked) {
                    lbl.classList.add('checked');
                } else {
                    lbl.classList.remove('checked');
                }
            });
        }

        function renderStationModal() {
            const tabsContainer = document.getElementById('modalCountyTabs');
            const body = document.getElementById('modalStationList');

            if (tabsContainer) {
                tabsContainer.innerHTML = COUNTY_GROUPS.map((group) => {
                    const isChecked = selectedCounties.has(group.county);
                    const checkedClass = isChecked ? 'checked' : '';
                    return `
                        <label class="county-check-label ${checkedClass}" data-county="${group.county}">
                            <input type="checkbox" ${isChecked ? 'checked' : ''} onchange="toggleCountyCheckbox('${group.county}', this.checked)">
                            <span>${group.county}</span>
                        </label>
                    `;
                }).join('');
            }

            if (body) {
                body.innerHTML = COUNTY_GROUPS.map((group) => `
                    <div class="county-section" id="county-sec-${group.county}" data-county="${group.county}">
                        <div class="county-section-title">📍 ${group.county} (${group.stations.length} 站)</div>
                        <div class="station-grid">
                            ${group.stations.map(st => {
                                const isHub = EXPRESS_MAJOR_STATIONS.has(st);
                                const isBranch = BRANCH_LINE_STATIONS.has(st);
                                
                                let btnClass = '';
                                let iconPrefix = '';
                                let titleTip = '';

                                if (isHub) {
                                    btnClass = 'express-hub';
                                    iconPrefix = '⭐ ';
                                    titleTip = '自強號特快停靠核心大站';
                                } else if (isBranch) {
                                    btnClass = 'branch-station';
                                    iconPrefix = '🌿 ';
                                    titleTip = '台鐵觀光支線車站 (平溪/深澳/內灣/六家/集集/沙崙線)';
                                }

                                return `<button class="station-btn ${btnClass}" onclick="modalPickStation('${st}')" title="${titleTip}">${iconPrefix}${st}</button>`;
                            }).join('')}
                        </div>
                    </div>
                `).join('');
            }

            updateCountyCheckboxesUI();
        }

        function filterModalStations() {
            const query = (document.getElementById('modalSearchInput').value || '').trim().toLowerCase();
            const sections = document.querySelectorAll('.county-section');

            sections.forEach(sec => {
                const county = sec.getAttribute('data-county');
                const isCountySelected = selectedCounties.has(county);

                if (!isCountySelected) {
                    sec.style.display = 'none';
                    return;
                }

                const btns = sec.querySelectorAll('.station-btn');
                let hasMatch = false;
                btns.forEach(btn => {
                    const st = btn.textContent.replace(/[⭐🌿 ]/g, '').toLowerCase();
                    if (!query || st.includes(query)) {
                        btn.style.display = 'block';
                        hasMatch = true;
                    } else {
                        btn.style.display = 'none';
                    }
                });
                sec.style.display = hasMatch ? 'block' : 'none';
            });
        }
"""

# Replace old renderStationModal / filterModalStations
old_render_match = re.search(r'function renderStationModal\(\)[\s\S]*?function filterModalStations\(\)[\s\S]*?\}\s*\}', html)
if old_render_match:
    html = html[:old_render_match.start()] + JS_LOGIC + html[old_render_match.end():]
else:
    print("Warning: old renderStationModal regex not matched directly, appending logic.")

# 4. Bump version to v3.9.0
html = html.replace("v3.8.15", "v3.9.0")
html = html.replace("v3815", "v390")

# Update Version selector options in index.html
html = html.replace(
    '<option value="latest" selected>v3.8.15 (最新穩定版)</option>',
    '<option value="latest" selected>v3.9.0 (鐵路地圖 & 縣市過濾版)</option>\n                                <option value="v3.8.15">v3.8.15 (0ms首屏預渲染版)</option>'
)

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully injected Taiwan Rail SVG Map and Multi-County Checkbox Filter into index.html!")
