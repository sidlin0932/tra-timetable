# -*- coding: utf-8 -*-
"""
Overhauls Station Modal UI with pristine aesthetics, responsive SVG Taiwan map, and unsquished county filters.
"""

import json
import re
from pathlib import Path
from generate_map_svg import STATION_COORDS

BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML = BASE_DIR / "index.html"

with open(INDEX_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# Build Station SVG nodes
stations_svg = []
for (x, y, name, is_hub, is_branch, county, line) in STATION_COORDS:
    r = 6.5 if is_hub else (5.2 if is_branch else 4.2)
    fill = "#ef4444" if is_hub else ("#059669" if is_branch else "#0284c7")
    stroke = "#ffffff"
    
    text_anchor = "start" if x < 280 else "end"
    text_dx = 10 if x < 280 else -10
    
    if name in ["台北", "松山", "南港", "基隆", "八堵", "七堵", "汐止", "瑞芳"]:
        text_anchor = "start"
        text_dx = 9
    elif name in ["板橋", "樹林", "桃園", "中壢", "楊梅", "新竹", "竹北"]:
        text_anchor = "end"
        text_dx = -9
    elif name in ["苗栗", "台中", "彰化", "員林", "斗六", "嘉義", "台南", "高雄", "新左營", "鳳山"]:
        text_anchor = "end"
        text_dx = -9
    elif name in ["花蓮", "宜蘭", "羅東", "礁溪", "台東", "玉里", "池上", "關山", "瑞穗"]:
        text_anchor = "start"
        text_dx = 9
    elif name in ["屏東", "潮州", "枋寮"]:
        text_anchor = "start"
        text_dx = 9

    star = "★ " if is_hub else ""
    font_weight = "800" if is_hub else "600"
    font_size = "11.5px" if is_hub else "10px"
    text_fill = "#991b1b" if is_hub else ("#065f46" if is_branch else "#1e293b")

    stations_svg.append(f'''
        <g class="map-station-node" data-station="{name}" data-county="{county}" data-line="{line}" onclick="modalPickStation('{name}')">
            <circle cx="{x}" cy="{y}" r="{r + 6}" class="station-hitbox" />
            <circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2" class="station-dot" />
            <text x="{x + text_dx}" y="{y + 3.5}" text-anchor="{text_anchor}" font-size="{font_size}" font-weight="{font_weight}" fill="{text_fill}" class="station-label">{star}{name}</text>
        </g>''')

stations_svg_str = "\n".join(stations_svg)

SVG_MAP_HTML = f'''
    <div class="taiwan-map-container" id="taiwanMapContainer">
        <div class="map-toolbar">
            <div class="map-hint-box">
                <span class="map-hint-icon">💡</span>
                <span class="map-hint-text">點擊地圖上的<strong>【車站紅/藍點】</strong>或<strong>【站名】</strong>直接選定；點擊<strong>【綠色縣市區塊】</strong>可快速切換清單！</span>
            </div>
            <div class="map-legend">
                <span class="legend-item"><span class="legend-dot hub"></span> 自強特快大站</span>
                <span class="legend-item"><span class="legend-dot branch"></span> 觀光支線站</span>
                <span class="legend-item"><span class="legend-dot main"></span> 幹線一般站</span>
            </div>
        </div>

        <div class="map-viewport">
            <svg viewBox="80 30 420 740" class="taiwan-rail-svg" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <filter id="mapShadow" x="-10%" y="-10%" width="120%" height="120%">
                        <feDropShadow dx="0" dy="2" stdDeviation="4" flood-opacity="0.12"/>
                    </filter>
                </defs>

                <!-- Taiwan Island Mainland Silhouette -->
                <path class="taiwan-island-bg" d="
                    M 410,45 C 435,50 480,100 470,160
                    C 465,200 450,280 435,360
                    C 420,440 370,560 330,640
                    C 300,700 240,755 210,760
                    C 195,762 170,750 150,740
                    C 115,720 105,660 110,610
                    C 115,560 125,480 120,410
                    C 110,330 130,250 160,200
                    C 190,150 250,110 320,80
                    C 370,55 390,42 410,45 Z
                " fill="#e2f0d9" stroke="#9bc778" stroke-width="2.5" filter="url(#mapShadow)" />

                <!-- County Region Division Soft Highlights -->
                <g class="county-zones" opacity="0.65">
                    <path d="M 370,55 Q 410,50 430,70 Q 390,80 370,55 Z" fill="#cbe6be" class="county-shape" data-county="基隆市" onclick="filterByCountyFromMap('基隆市')" />
                    <path d="M 300,90 Q 340,85 350,115 Q 310,120 300,90 Z" fill="#bfdfb0" class="county-shape" data-county="台北市" onclick="filterByCountyFromMap('台北市')" />
                    <path d="M 245,130 Q 300,100 370,105 Q 460,120 460,150 Q 380,140 245,130 Z" fill="#cce8bf" class="county-shape" data-county="新北市" onclick="filterByCountyFromMap('新北市')" />
                    <path d="M 190,180 Q 250,150 260,195 Q 200,215 190,180 Z" fill="#d9eed0" class="county-shape" data-county="桃園市" onclick="filterByCountyFromMap('桃園市')" />
                    <path d="M 145,230 Q 200,210 210,255 Q 155,265 145,230 Z" fill="#c7e4b9" class="county-shape" data-county="新竹縣市" onclick="filterByCountyFromMap('新竹縣市')" />
                    <path d="M 115,280 Q 170,260 175,330 Q 120,345 115,280 Z" fill="#dbeef2" class="county-shape" data-county="苗栗縣" onclick="filterByCountyFromMap('苗栗縣')" />
                    <path d="M 115,350 Q 185,340 185,430 Q 130,440 115,350 Z" fill="#c3e1b4" class="county-shape" data-county="台中市" onclick="filterByCountyFromMap('台中市')" />
                    <path d="M 135,445 Q 175,440 175,510 Q 140,515 135,445 Z" fill="#d5edd0" class="county-shape" data-county="彰化縣" onclick="filterByCountyFromMap('彰化縣')" />
                    <path d="M 175,450 Q 260,450 250,530 Q 175,525 175,450 Z" fill="#c9e7bc" class="county-shape" data-county="南投縣" onclick="filterByCountyFromMap('南投縣')" />
                    <path d="M 135,520 Q 170,518 165,555 Q 135,555 135,520 Z" fill="#d7eed0" class="county-shape" data-county="雲林縣" onclick="filterByCountyFromMap('雲林縣')" />
                    <path d="M 125,560 Q 165,558 160,600 Q 125,600 125,560 Z" fill="#cbe7bf" class="county-shape" data-county="嘉義縣市" onclick="filterByCountyFromMap('嘉義縣市')" />
                    <path d="M 110,605 Q 155,602 155,680 Q 110,680 110,605 Z" fill="#d5ebd0" class="county-shape" data-county="台南市" onclick="filterByCountyFromMap('台南市')" />
                    <path d="M 115,685 Q 165,682 170,740 Q 120,740 115,685 Z" fill="#c5e3b7" class="county-shape" data-county="高雄市" onclick="filterByCountyFromMap('高雄市')" />
                    <path d="M 160,735 Q 215,735 210,760 Q 160,755 160,735 Z" fill="#d9eed0" class="county-shape" data-county="屏東縣" onclick="filterByCountyFromMap('屏東縣')" />
                    <path d="M 420,150 Q 465,160 450,280 Q 410,270 420,150 Z" fill="#cbe7bf" class="county-shape" data-county="宜蘭縣" onclick="filterByCountyFromMap('宜蘭縣')" />
                    <path d="M 360,330 Q 435,320 395,570 Q 340,560 360,330 Z" fill="#c1dfb1" class="county-shape" data-county="花蓮縣" onclick="filterByCountyFromMap('花蓮縣')" />
                    <path d="M 270,590 Q 350,580 290,730 Q 240,730 270,590 Z" fill="#d0ebd0" class="county-shape" data-county="台東縣" onclick="filterByCountyFromMap('台東縣')" />
                </g>

                <!-- County Name Labels on Map -->
                <g class="county-map-labels" font-size="11.5px" font-weight="900" fill="#365314" pointer-events="all">
                    <text x="395" y="42" class="map-label-pill" onclick="filterByCountyFromMap('基隆市')">基隆</text>
                    <text x="325" y="85" class="map-label-pill" onclick="filterByCountyFromMap('台北市')">台北市</text>
                    <text x="375" y="115" class="map-label-pill" onclick="filterByCountyFromMap('新北市')">新北市</text>
                    <text x="252" y="148" class="map-label-pill" onclick="filterByCountyFromMap('桃園市')">桃園</text>
                    <text x="200" y="222" class="map-label-pill" onclick="filterByCountyFromMap('新竹縣市')">新竹</text>
                    <text x="180" y="295" class="map-label-pill" onclick="filterByCountyFromMap('苗栗縣')">苗栗</text>
                    <text x="195" y="375" class="map-label-pill" onclick="filterByCountyFromMap('台中市')">台中</text>
                    <text x="125" y="475" class="map-label-pill" onclick="filterByCountyFromMap('彰化縣')">彰化</text>
                    <text x="215" y="495" class="map-label-pill" onclick="filterByCountyFromMap('南投縣')">南投(集集線)</text>
                    <text x="125" y="535" class="map-label-pill" onclick="filterByCountyFromMap('雲林縣')">雲林</text>
                    <text x="175" y="580" class="map-label-pill" onclick="filterByCountyFromMap('嘉義縣市')">嘉義</text>
                    <text x="165" y="640" class="map-label-pill" onclick="filterByCountyFromMap('台南市')">台南</text>
                    <text x="165" y="700" class="map-label-pill" onclick="filterByCountyFromMap('高雄市')">高雄</text>
                    <text x="195" y="735" class="map-label-pill" onclick="filterByCountyFromMap('屏東縣')">屏東</text>
                    <text x="445" y="200" class="map-label-pill" onclick="filterByCountyFromMap('宜蘭縣')">宜蘭</text>
                    <text x="390" y="360" class="map-label-pill" onclick="filterByCountyFromMap('花蓮縣')">花蓮</text>
                    <text x="320" y="670" class="map-label-pill" onclick="filterByCountyFromMap('台東縣')">台東</text>
                </g>

                <!-- Railway Tracks (Base & Dashed) -->
                <!-- Western Trunk North -->
                <path d="M 410,48 L 402,54 L 394,60 L 384,66 L 374,72 L 364,78 L 354,84 L 346,88 L 336,94 L 324,98 L 312,104 L 300,110 L 288,118 L 278,126 L 268,134 L 258,142 L 250,148 L 240,156 L 230,166 L 220,176 L 210,186 L 200,196 L 192,204 L 184,212 L 176,220 L 168,228 L 160,236 L 152,246 L 146,254 L 140,264" class="rail-track-base" />
                <path d="M 410,48 L 402,54 L 394,60 L 384,66 L 374,72 L 364,78 L 354,84 L 346,88 L 336,94 L 324,98 L 312,104 L 300,110 L 288,118 L 278,126 L 268,134 L 258,142 L 250,148 L 240,156 L 230,166 L 220,176 L 210,186 L 200,196 L 192,204 L 184,212 L 176,220 L 168,228 L 160,236 L 152,246 L 146,254 L 140,264" class="rail-track-dashed" />

                <!-- Mountain Line -->
                <path d="M 140,264 L 150,276 L 154,288 L 158,300 L 160,314 L 162,328 L 164,344 L 166,356 L 168,370 L 170,384 L 172,396 L 174,408 L 172,420 L 168,430 L 164,436 L 158,442 L 152,450" class="rail-track-base" />
                <path d="M 140,264 L 150,276 L 154,288 L 158,300 L 160,314 L 162,328 L 164,344 L 166,356 L 168,370 L 170,384 L 172,396 L 174,408 L 172,420 L 168,430 L 164,436 L 158,442 L 152,450" class="rail-track-dashed" />

                <!-- Coast Line -->
                <path d="M 140,264 L 128,274 L 122,286 L 118,298 L 114,310 L 112,322 L 110,334 L 112,346 L 116,358 L 120,370 L 124,382 L 128,394 L 134,408 L 140,420 L 146,432 L 152,450" class="rail-track-base" />
                <path d="M 140,264 L 128,274 L 122,286 L 118,298 L 114,310 L 112,322 L 110,334 L 112,346 L 116,358 L 120,370 L 124,382 L 128,394 L 134,408 L 140,420 L 146,432 L 152,450" class="rail-track-dashed" />

                <!-- Western Trunk South -->
                <path d="M 152,450 L 154,462 L 156,474 L 158,486 L 160,498 L 162,510 L 158,522 L 156,534 L 152,546 L 148,558 L 144,570 L 140,582 L 136,594 L 132,606 L 128,618 L 126,628 L 124,638 L 122,648 L 120,658 L 118,668 L 124,676 L 124,688 L 126,698 L 128,708 L 130,718 L 132,728 L 138,732 L 146,734 L 154,736 L 164,738 L 172,742 L 180,746 L 186,750 L 192,752 L 200,754" class="rail-track-base" />
                <path d="M 152,450 L 154,462 L 156,474 L 158,486 L 160,498 L 162,510 L 158,522 L 156,534 L 152,546 L 148,558 L 144,570 L 140,582 L 136,594 L 132,606 L 128,618 L 126,628 L 124,638 L 122,648 L 120,658 L 118,668 L 124,676 L 124,688 L 126,698 L 128,708 L 130,718 L 132,728 L 138,732 L 146,734 L 154,736 L 164,738 L 172,742 L 180,746 L 186,750 L 192,752 L 200,754" class="rail-track-dashed" />

                <!-- South Link Line -->
                <path d="M 200,754 L 208,750 L 216,744 L 240,726 L 260,706 L 274,686 L 288,666 L 300,646" class="rail-track-base" />
                <path d="M 200,754 L 208,750 L 216,744 L 240,726 L 260,706 L 274,686 L 288,666 L 300,646" class="rail-track-dashed" />

                <!-- Eastern Trunk (Taitung -> Hualien) -->
                <path d="M 300,646 L 312,626 L 322,606 L 332,586 L 342,566 L 352,546 L 362,526 L 370,506 L 378,486 L 386,466 L 394,446 L 402,426" class="rail-track-base" />
                <path d="M 300,646 L 312,626 L 322,606 L 332,586 L 342,566 L 352,546 L 362,526 L 370,506 L 378,486 L 386,466 L 394,446 L 402,426" class="rail-track-dashed" />

                <!-- North Link & Yilan Line -->
                <path d="M 402,426 L 410,396 L 418,366 L 426,336 L 434,306 L 440,276 L 444,252 L 448,232 L 452,212 L 456,192 L 458,174 L 460,156 L 462,144 L 464,134 L 456,126 L 450,116 L 444,106 L 436,96 L 432,88 L 426,78 L 414,74 L 404,68 L 394,60" class="rail-track-base" />
                <path d="M 402,426 L 410,396 L 418,366 L 426,336 L 434,306 L 440,276 L 444,252 L 448,232 L 452,212 L 456,192 L 458,174 L 460,156 L 462,144 L 464,134 L 456,126 L 450,116 L 444,106 L 436,96 L 432,88 L 426,78 L 414,74 L 404,68 L 394,60" class="rail-track-dashed" />

                <!-- Branch Lines (Amber) -->
                <path d="M 426,78 L 420,42 L 428,44" class="rail-branch-base" />
                <path d="M 436,96 L 422,102 L 410,108 L 400,114 L 390,118" class="rail-branch-base" />
                <path d="M 160,236 L 172,240 L 182,234" class="rail-branch-base" />
                <path d="M 172,240 L 184,246 L 194,252" class="rail-branch-base" />
                <path d="M 162,510 L 176,512 L 190,514 L 204,516 L 216,518" class="rail-branch-base" />
                <path d="M 124,676 L 134,678 L 144,680" class="rail-branch-base" />
                <path d="M 440,276 L 448,278" class="rail-branch-base" />

                <!-- Stations Layer -->
                <g class="map-stations-layer">
                    {stations_svg_str}
                </g>
            </svg>
        </div>
    </div>
'''

COMPLETE_MODAL_HTML = f'''    <!-- County-classified Station Modal -->
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
                {SVG_MAP_HTML}
            </div>
        </div>
    </div>'''

# Replace modal in HTML
modal_pattern = re.compile(r'<!-- County-classified Station Modal -->[\s\S]*?</div>\s*</div>\s*(?=<script)', re.MULTILINE)
html = modal_pattern.sub(COMPLETE_MODAL_HTML + "\n", html)

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Modal overhaul template applied!")
