# -*- coding: utf-8 -*-
"""
Generates a mobile-first, ultra-clear interactive Taiwan Railway Transit Map System:
1. High-contrast, clean modern Metro/Geographic Hybrid layout.
2. Huge touch hitboxes (r=24 / 48px touch targets) for effortless tapping on mobile.
3. Region Fast Tabs: [🗺️ 全台總覽] [🚄 北部] [🚄 中部] [🚄 南部] [🌊 東部/南迴] [🌿 觀光支線]
   Allows instant 1-tap zooming and clear spacing of stations without visual overlap.
4. Floating Quick Action Sheet upon tap: [🚩 設為出發] [🏁 設為抵達] [🔀 指定轉乘].
"""

import json

# Region definitions with focused viewport coords & station subsets
REGIONS_CONFIG = {
    "all": {
        "name": "🗺️ 全島總覽",
        "viewBox": "40 10 440 700"
    },
    "north": {
        "name": "🚄 北部 (北北基桃竹)",
        "viewBox": "80 20 380 280"
    },
    "central": {
        "name": "🚄 中部 (苗中彰投)",
        "viewBox": "60 240 220 280"
    },
    "south": {
        "name": "🚄 南部 (雲嘉南高屏)",
        "viewBox": "60 460 220 260"
    },
    "east": {
        "name": "🌊 東部 & 南迴 (宜花東)",
        "viewBox": "210 50 250 660"
    },
    "branch": {
        "name": "🌿 觀光支線 (平溪/內灣/集集/沙崙)",
        "viewBox": "90 50 360 450"
    }
}

# Stations with optimized positions for zero overlap and high legibility
MAP_STATIONS = [
    # Keelung & North Coast
    {"x": 370, "y": 45, "name": "基隆", "hub": True, "line": "north", "align": "top"},
    {"x": 396, "y": 45, "name": "八斗子", "hub": False, "branch": True, "line": "branch", "align": "right"},
    {"x": 350, "y": 60, "name": "八堵", "hub": True, "line": "north", "align": "left"},
    {"x": 335, "y": 72, "name": "七堵", "hub": True, "line": "north", "align": "left"},
    {"x": 315, "y": 86, "name": "汐止", "hub": True, "line": "north", "align": "left"},
    
    # Taipei Metro Core (Spread out nicely so no overlap)
    {"x": 295, "y": 98, "name": "南港", "hub": True, "line": "north", "align": "top"},
    {"x": 275, "y": 108, "name": "松山", "hub": True, "line": "north", "align": "top"},
    {"x": 252, "y": 118, "name": "台北", "hub": True, "line": "north", "align": "top"},
    {"x": 230, "y": 130, "name": "板橋", "hub": True, "line": "north", "align": "left"},
    {"x": 210, "y": 144, "name": "樹林", "hub": True, "line": "north", "align": "left"},
    {"x": 192, "y": 158, "name": "鶯歌", "hub": True, "line": "north", "align": "left"},
    
    # Pingxi Branch
    {"x": 372, "y": 72, "name": "瑞芳", "hub": True, "line": "north", "align": "right"},
    {"x": 386, "y": 90, "name": "猴硐", "hub": False, "branch": True, "line": "branch", "align": "right"},
    {"x": 396, "y": 105, "name": "十分", "hub": False, "branch": True, "line": "branch", "align": "right"},
    {"x": 375, "y": 115, "name": "平溪", "hub": False, "branch": True, "line": "branch", "align": "left"},
    {"x": 355, "y": 120, "name": "菁桐", "hub": False, "branch": True, "line": "branch", "align": "bottom"},
    {"x": 410, "y": 105, "name": "雙溪", "hub": True, "line": "north", "align": "right"},
    {"x": 425, "y": 118, "name": "福隆", "hub": True, "line": "north", "align": "right"},

    # Taoyuan & Hsinchu
    {"x": 178, "y": 174, "name": "桃園", "hub": True, "line": "north", "align": "left"},
    {"x": 162, "y": 194, "name": "中壢", "hub": True, "line": "north", "align": "left"},
    {"x": 148, "y": 214, "name": "楊梅", "hub": True, "line": "north", "align": "left"},
    {"x": 136, "y": 234, "name": "竹北", "hub": True, "line": "north", "align": "left"},
    {"x": 122, "y": 252, "name": "新竹", "hub": True, "line": "north", "align": "left"},
    
    # Neiwan Branch
    {"x": 138, "y": 254, "name": "竹中", "hub": True, "branch": True, "line": "branch", "align": "bottom"},
    {"x": 150, "y": 242, "name": "六家", "hub": True, "branch": True, "line": "branch", "align": "top"},
    {"x": 158, "y": 262, "name": "竹東", "hub": False, "branch": True, "line": "branch", "align": "right"},
    {"x": 176, "y": 272, "name": "內灣", "hub": True, "branch": True, "line": "branch", "align": "right"},

    # Miaoli (Mountain & Coast)
    {"x": 108, "y": 274, "name": "竹南", "hub": True, "line": "central", "align": "left"},
    # Mountain
    {"x": 122, "y": 296, "name": "苗栗", "hub": True, "line": "central", "align": "right"},
    {"x": 126, "y": 320, "name": "三義", "hub": True, "line": "central", "align": "right"},
    # Coast
    {"x": 88, "y": 296, "name": "白沙屯", "hub": True, "line": "central", "align": "left"},
    {"x": 84, "y": 320, "name": "通霄", "hub": True, "line": "central", "align": "left"},

    # Taichung
    # Coast
    {"x": 88, "y": 348, "name": "大甲", "hub": True, "line": "central", "align": "left"},
    {"x": 96, "y": 378, "name": "沙鹿", "hub": True, "line": "central", "align": "left"},
    # Mountain
    {"x": 132, "y": 344, "name": "豐原", "hub": True, "line": "central", "align": "right"},
    {"x": 138, "y": 374, "name": "台中", "hub": True, "line": "central", "align": "right"},
    {"x": 132, "y": 396, "name": "新烏日", "hub": True, "line": "central", "align": "right"},

    # Changhua & Jiji Branch
    {"x": 118, "y": 415, "name": "彰化", "hub": True, "line": "central", "align": "left"},
    {"x": 124, "y": 438, "name": "員林", "hub": True, "line": "central", "align": "left"},
    {"x": 128, "y": 460, "name": "田中", "hub": True, "line": "central", "align": "left"},
    {"x": 134, "y": 476, "name": "二水", "hub": True, "line": "central", "align": "left"},
    # Jiji
    {"x": 154, "y": 478, "name": "濁水", "hub": True, "branch": True, "line": "branch", "align": "bottom"},
    {"x": 172, "y": 478, "name": "集集", "hub": True, "branch": True, "line": "branch", "align": "top"},
    {"x": 192, "y": 478, "name": "水里", "hub": False, "branch": True, "line": "branch", "align": "bottom"},
    {"x": 210, "y": 478, "name": "車埕", "hub": True, "branch": True, "line": "branch", "align": "right"},

    # Yunlin & Chiayi
    {"x": 130, "y": 498, "name": "斗六", "hub": True, "line": "south", "align": "left"},
    {"x": 124, "y": 516, "name": "斗南", "hub": True, "line": "south", "align": "left"},
    {"x": 118, "y": 540, "name": "嘉義", "hub": True, "line": "south", "align": "left"},

    # Tainan & Shalun Branch
    {"x": 112, "y": 564, "name": "新營", "hub": True, "line": "south", "align": "left"},
    {"x": 106, "y": 586, "name": "善化", "hub": True, "line": "south", "align": "left"},
    {"x": 100, "y": 612, "name": "台南", "hub": True, "line": "south", "align": "left"},
    {"x": 112, "y": 622, "name": "中洲", "hub": False, "line": "south", "align": "left"},
    {"x": 128, "y": 624, "name": "沙崙", "hub": True, "branch": True, "line": "branch", "align": "right"},

    # Kaohsiung & Pingtung
    {"x": 104, "y": 638, "name": "岡山", "hub": True, "line": "south", "align": "left"},
    {"x": 108, "y": 654, "name": "新左營", "hub": True, "line": "south", "align": "left"},
    {"x": 114, "y": 668, "name": "高雄", "hub": True, "line": "south", "align": "left"},
    {"x": 128, "y": 674, "name": "鳳山", "hub": True, "line": "south", "align": "bottom"},
    {"x": 148, "y": 678, "name": "屏東", "hub": True, "line": "south", "align": "top"},
    {"x": 164, "y": 684, "name": "潮州", "hub": True, "line": "south", "align": "bottom"},
    {"x": 188, "y": 692, "name": "枋寮", "hub": True, "line": "south", "align": "bottom"},

    # South Link Line
    {"x": 222, "y": 670, "name": "大武", "hub": True, "line": "east", "align": "bottom"},
    {"x": 258, "y": 638, "name": "金崙", "hub": False, "line": "east", "align": "right"},
    {"x": 278, "y": 614, "name": "太麻里", "hub": True, "line": "east", "align": "right"},
    {"x": 292, "y": 590, "name": "知本", "hub": True, "line": "east", "align": "right"},
    {"x": 302, "y": 566, "name": "台東", "hub": True, "line": "east", "align": "right"},

    # Eastern Taitung Line
    {"x": 314, "y": 538, "name": "鹿野", "hub": True, "line": "east", "align": "right"},
    {"x": 324, "y": 512, "name": "關山", "hub": True, "line": "east", "align": "right"},
    {"x": 336, "y": 486, "name": "池上", "hub": True, "line": "east", "align": "right"},
    {"x": 348, "y": 458, "name": "玉里", "hub": True, "line": "east", "align": "right"},
    {"x": 360, "y": 428, "name": "瑞穗", "hub": True, "line": "east", "align": "right"},
    {"x": 370, "y": 398, "name": "光復", "hub": True, "line": "east", "align": "right"},
    {"x": 380, "y": 368, "name": "鳳林", "hub": True, "line": "east", "align": "right"},
    {"x": 390, "y": 338, "name": "壽豐", "hub": True, "line": "east", "align": "right"},
    {"x": 402, "y": 310, "name": "花蓮", "hub": True, "line": "east", "align": "right"},

    # North Link Line & Yilan Line
    {"x": 408, "y": 276, "name": "新城(太魯閣)", "hub": True, "line": "east", "align": "right"},
    {"x": 416, "y": 238, "name": "和平", "hub": False, "line": "east", "align": "right"},
    {"x": 422, "y": 208, "name": "南澳", "hub": True, "line": "east", "align": "right"},
    {"x": 426, "y": 184, "name": "蘇澳新", "hub": True, "line": "east", "align": "right"},
    {"x": 438, "y": 184, "name": "蘇澳", "hub": True, "branch": True, "line": "east", "align": "bottom"},
    {"x": 428, "y": 162, "name": "羅東", "hub": True, "line": "east", "align": "right"},
    {"x": 426, "y": 142, "name": "宜蘭", "hub": True, "line": "east", "align": "right"},
    {"x": 424, "y": 126, "name": "礁溪", "hub": True, "line": "east", "align": "right"},
    {"x": 420, "y": 112, "name": "頭城", "hub": True, "line": "east", "align": "right"},
]

def build_map_component():
    # Stations markup
    station_nodes = []
    for s in MAP_STATIONS:
        x, y, name = s["x"], s["y"], s["name"]
        is_hub = s.get("hub", False)
        is_branch = s.get("branch", False)
        align = s.get("align", "right")

        dot_fill = "#ef4444" if is_hub else ("#10b981" if is_branch else "#0284c7")
        dot_r = 6.5 if is_hub else 5.0
        
        # Text label offset
        if align == "left":
            lx, ly, anchor = x - 10, y + 4, "end"
        elif align == "right":
            lx, ly, anchor = x + 10, y + 4, "start"
        elif align == "top":
            lx, ly, anchor = x, y - 10, "middle"
        elif align == "bottom":
            lx, ly, anchor = x, y + 16, "middle"
        else:
            lx, ly, anchor = x + 10, y + 4, "start"

        star = "★ " if is_hub else ""
        text_color = "#991b1b" if is_hub else ("#065f46" if is_branch else "#0f172a")
        
        station_nodes.append(f'''
        <g class="map-station-node" data-station="{name}" onclick="openMapStationAction('{name}', event)" ontouchstart="openMapStationAction('{name}', event)">
            <!-- Huge invisible touch target (r=24 / 48px) for effortless mobile tapping -->
            <circle cx="{x}" cy="{y}" r="22" fill="transparent" stroke="none" class="station-touch-hitbox" />
            <!-- Visual Station Pin -->
            <circle cx="{x}" cy="{y}" r="{dot_r + 2.5}" fill="#ffffff" opacity="0.9" />
            <circle cx="{x}" cy="{y}" r="{dot_r}" fill="{dot_fill}" stroke="#ffffff" stroke-width="2" class="station-dot" />
            <!-- Label Badge with high readability -->
            <text x="{lx}" y="{ly}" text-anchor="{anchor}" font-size="11.5px" font-weight="800" fill="{text_color}" class="map-station-name">{star}{name}</text>
        </g>''')

    stations_svg = "\n".join(station_nodes)

    html_code = f'''
    <div class="taiwan-map-wrapper" id="taiwanMapWrapper">
        <!-- Region Filter Bar (Mobile-first Quick Zoom) -->
        <div class="map-region-tabs" id="mapRegionTabs">
            <button class="region-tab-btn active" onclick="zoomMapRegion('all', this)">🗺️ 全島總覽</button>
            <button class="region-tab-btn" onclick="zoomMapRegion('north', this)">🚄 北部幹線</button>
            <button class="region-tab-btn" onclick="zoomMapRegion('central', this)">🚄 中部山海</button>
            <button class="region-tab-btn" onclick="zoomMapRegion('south', this)">🚄 南部高屏</button>
            <button class="region-tab-btn" onclick="zoomMapRegion('east', this)">🌊 東部南迴</button>
            <button class="region-tab-btn" onclick="zoomMapRegion('branch', this)">🌿 觀光支線</button>
        </div>

        <div class="map-instruction-banner">
            👉 <strong>點選地圖上的車站</strong> 可直接設為出發／抵達站（點擊即選定）
        </div>

        <!-- SVG Map Container -->
        <div class="map-svg-container">
            <svg id="taiwanRailSvg" viewBox="40 10 440 700" class="taiwan-rail-svg" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <filter id="islandGlow" x="-10%" y="-10%" width="120%" height="120%">
                        <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.15" flood-color="#0f172a" />
                    </filter>
                </defs>

                <!-- Taiwan Island Mainland Geography Outline -->
                <path class="taiwan-island-bg" d="
                    M 370,45 C 405,48 440,95 435,155
                    C 430,195 425,270 410,345
                    C 395,420 350,530 315,600
                    C 285,650 235,695 200,700
                    C 185,700 160,690 140,680
                    C 105,660 95,610 100,560
                    C 105,510 115,440 110,380
                    C 100,310 115,240 145,190
                    C 175,140 230,105 295,80
                    C 340,55 355,42 370,45 Z
                " fill="#eef7e6" stroke="#86efac" stroke-width="3" filter="url(#islandGlow)" />

                <!-- Railway Tracks -->
                <!-- 1. Western Trunk North -->
                <path d="M 370,45 L 350,60 L 335,72 L 315,86 L 295,98 L 275,108 L 252,118 L 230,130 L 210,144 L 192,158 L 178,174 L 162,194 L 148,214 L 136,234 L 122,252 L 108,274" fill="none" stroke="#1e293b" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M 370,45 L 350,60 L 335,72 L 315,86 L 295,98 L 275,108 L 252,118 L 230,130 L 210,144 L 192,158 L 178,174 L 162,194 L 148,214 L 136,234 L 122,252 L 108,274" fill="none" stroke="#ffffff" stroke-width="2.4" stroke-dasharray="6 5" stroke-linecap="butt" />

                <!-- 2. Mountain Line -->
                <path d="M 108,274 L 122,296 L 126,320 L 132,344 L 138,374 L 132,396 L 118,415" fill="none" stroke="#1e293b" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M 108,274 L 122,296 L 126,320 L 132,344 L 138,374 L 132,396 L 118,415" fill="none" stroke="#ffffff" stroke-width="2.4" stroke-dasharray="6 5" stroke-linecap="butt" />

                <!-- 3. Coast Line -->
                <path d="M 108,274 L 88,296 L 84,320 L 88,348 L 96,378 L 118,415" fill="none" stroke="#1e293b" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M 108,274 L 88,296 L 84,320 L 88,348 L 96,378 L 118,415" fill="none" stroke="#ffffff" stroke-width="2.4" stroke-dasharray="6 5" stroke-linecap="butt" />

                <!-- 4. Western Trunk South -->
                <path d="M 118,415 L 124,438 L 128,460 L 134,476 L 130,498 L 124,516 L 118,540 L 112,564 L 106,586 L 100,612 L 112,622 L 104,638 L 108,654 L 114,668 L 128,674 L 148,678 L 164,684 L 188,692" fill="none" stroke="#1e293b" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M 118,415 L 124,438 L 128,460 L 134,476 L 130,498 L 124,516 L 118,540 L 112,564 L 106,586 L 100,612 L 112,622 L 104,638 L 108,654 L 114,668 L 128,674 L 148,678 L 164,684 L 188,692" fill="none" stroke="#ffffff" stroke-width="2.4" stroke-dasharray="6 5" stroke-linecap="butt" />

                <!-- 5. South Link Line -->
                <path d="M 188,692 L 222,670 L 258,638 L 278,614 L 292,590 L 302,566" fill="none" stroke="#1e293b" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M 188,692 L 222,670 L 258,638 L 278,614 L 292,590 L 302,566" fill="none" stroke="#ffffff" stroke-width="2.4" stroke-dasharray="6 5" stroke-linecap="butt" />

                <!-- 6. Eastern Trunk Line -->
                <path d="M 302,566 L 314,538 L 324,512 L 336,486 L 348,458 L 360,428 L 370,398 L 380,368 L 390,338 L 402,310" fill="none" stroke="#1e293b" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M 302,566 L 314,538 L 324,512 L 336,486 L 348,458 L 360,428 L 370,398 L 380,368 L 390,338 L 402,310" fill="none" stroke="#ffffff" stroke-width="2.4" stroke-dasharray="6 5" stroke-linecap="butt" />

                <!-- 7. North Link Line & Yilan Line -->
                <path d="M 402,310 L 408,276 L 416,238 L 422,208 L 426,184 L 428,162 L 426,142 L 424,126 L 420,112 L 425,118 L 410,105 L 372,72 L 350,60" fill="none" stroke="#1e293b" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M 402,310 L 408,276 L 416,238 L 422,208 L 426,184 L 428,162 L 426,142 L 424,126 L 420,112 L 425,118 L 410,105 L 372,72 L 350,60" fill="none" stroke="#ffffff" stroke-width="2.4" stroke-dasharray="6 5" stroke-linecap="butt" />

                <!-- 8. Branch Lines (Amber Orange) -->
                <!-- Shenao -->
                <path d="M 350,60 L 370,45 L 396,45" fill="none" stroke="#d97706" stroke-width="3.5" stroke-dasharray="5 4" stroke-linecap="round" />
                <!-- Pingxi -->
                <path d="M 372,72 L 386,90 L 396,105 L 375,115 L 355,120" fill="none" stroke="#d97706" stroke-width="3.5" stroke-dasharray="5 4" stroke-linecap="round" />
                <!-- Neiwan & Liujia -->
                <path d="M 122,252 L 138,254 L 150,242" fill="none" stroke="#d97706" stroke-width="3.5" stroke-dasharray="5 4" stroke-linecap="round" />
                <path d="M 138,254 L 158,262 L 176,272" fill="none" stroke="#d97706" stroke-width="3.5" stroke-dasharray="5 4" stroke-linecap="round" />
                <!-- Jiji -->
                <path d="M 134,476 L 154,478 L 172,478 L 192,478 L 210,478" fill="none" stroke="#d97706" stroke-width="3.5" stroke-dasharray="5 4" stroke-linecap="round" />
                <!-- Shalun -->
                <path d="M 112,622 L 128,624" fill="none" stroke="#d97706" stroke-width="3.5" stroke-dasharray="5 4" stroke-linecap="round" />
                <!-- Suao Branch -->
                <path d="M 426,184 L 438,184" fill="none" stroke="#d97706" stroke-width="3.5" stroke-dasharray="5 4" stroke-linecap="round" />

                <!-- Station Nodes Layer -->
                <g class="map-stations-layer">
                    {stations_svg}
                </g>
            </svg>
        </div>

        <!-- Floating Station Action Sheet upon tap -->
        <div id="mapStationActionSheet" class="map-action-sheet" style="display:none;">
            <div class="action-sheet-header">
                <span class="action-station-badge" id="actionStationName">台北</span>
                <button class="action-sheet-close" onclick="closeMapActionSheet()">✕</button>
            </div>
            <div class="action-sheet-buttons">
                <button class="btn-sheet-action dep" onclick="confirmMapStationPick('origin')">🚩 設為出發站</button>
                <button class="btn-sheet-action arr" onclick="confirmMapStationPick('dest')">🏁 設為抵達站</button>
                <button class="btn-sheet-action via" onclick="confirmMapStationPick('via')">🔀 指定為轉乘站</button>
            </div>
        </div>
    </div>
    '''
    return html_code

print("Ultra-clear Mobile-first Taiwan Map Generator ready.")
