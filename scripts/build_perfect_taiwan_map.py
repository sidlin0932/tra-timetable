# -*- coding: utf-8 -*-
"""
Generates an ultra-premium, crystal-clear Taiwan Railway SVG Transit Map
matching the user's reference aesthetic (Soft green county geography, 
clean dashed tracks, Apple/Google Maps style transit station nodes & badges).
"""

import json
from pathlib import Path

# Mapped Geographic Station Coordinates (500 x 700 canvas)
# Format: (x, y, name, is_hub, is_branch, county, label_pos)
# label_pos: 'left', 'right', 'top', 'bottom', 'none'

STATIONS_DATA = [
    # Keelung & North Coast
    (385, 52, "基隆", True, False, "基隆市", "top"),
    (375, 62, "三坑", False, False, "基隆市", "none"),
    (365, 70, "八堵", True, False, "基隆市", "left"),
    (355, 78, "七堵", True, False, "基隆市", "left"),
    (345, 86, "百福", False, False, "基隆市", "none"),
    (398, 48, "海科館", False, True, "基隆市", "none"),
    (408, 50, "八斗子", False, True, "基隆市", "right"),

    # Taipei / New Taipei Metro
    (335, 92, "五堵", False, False, "新北市", "none"),
    (325, 98, "汐止", True, False, "新北市", "left"),
    (318, 102, "汐科", False, False, "新北市", "none"),
    (308, 108, "南港", True, False, "台北市", "top"),
    (296, 112, "松山", True, False, "台北市", "top"),
    (282, 118, "台北", True, False, "台北市", "top"),
    (270, 124, "萬華", True, False, "台北市", "none"),
    (256, 132, "板橋", True, False, "新北市", "left"),
    (245, 140, "浮洲", False, False, "新北市", "none"),
    (235, 148, "樹林", True, False, "新北市", "left"),
    (225, 156, "山佳", False, False, "新北市", "none"),
    (216, 164, "鶯歌", True, False, "新北市", "left"),

    # Pingxi & Northeast Coast
    (375, 78, "瑞芳", True, False, "新北市", "right"),
    (382, 88, "猴硐", False, False, "新北市", "none"),
    (388, 96, "三貂嶺", False, False, "新北市", "none"),
    (376, 102, "十分", False, True, "新北市", "none"),
    (364, 108, "平溪", False, True, "新北市", "none"),
    (352, 112, "菁桐", False, True, "新北市", "bottom"),
    (400, 108, "雙溪", True, False, "新北市", "right"),
    (412, 118, "福隆", True, False, "新北市", "right"),

    # Taoyuan
    (204, 174, "桃園", True, False, "桃園市", "left"),
    (194, 184, "內壢", False, False, "桃園市", "none"),
    (184, 194, "中壢", True, False, "桃園市", "left"),
    (174, 204, "埔心", False, False, "桃園市", "none"),
    (164, 214, "楊梅", True, False, "桃園市", "left"),
    (154, 222, "富岡", False, False, "桃園市", "none"),

    # Hsinchu
    (146, 230, "湖口", False, False, "新竹縣市", "none"),
    (138, 238, "新豐", False, False, "新竹縣市", "none"),
    (130, 246, "竹北", True, False, "新竹縣市", "left"),
    (122, 254, "新竹", True, False, "新竹縣市", "left"),
    (134, 258, "竹中", False, True, "新竹縣市", "none"),
    (144, 252, "六家", True, True, "新竹縣市", "top"),
    (148, 266, "竹東", False, True, "新竹縣市", "none"),
    (158, 274, "內灣", True, True, "新竹縣市", "right"),

    # Miaoli (Mountain & Coast Line split at Zhunan)
    (110, 272, "竹南", True, False, "苗栗縣", "left"),
    # Mountain Line (Miaoli)
    (124, 286, "苗栗", True, False, "苗栗縣", "left"),
    (128, 302, "三義", True, False, "苗栗縣", "left"),
    # Coast Line (Miaoli)
    (96, 284, "後龍", True, False, "苗栗縣", "none"),
    (90, 300, "白沙屯", True, False, "苗栗縣", "left"),
    (88, 318, "通霄", True, False, "苗栗縣", "left"),
    (92, 334, "苑裡", True, False, "苗栗縣", "none"),

    # Taichung
    # Coast Line (Taichung)
    (96, 348, "大甲", True, False, "台中市", "left"),
    (104, 368, "清水", True, False, "台中市", "none"),
    (110, 384, "沙鹿", True, False, "台中市", "left"),
    # Mountain Line (Taichung)
    (132, 320, "后里", True, False, "台中市", "none"),
    (136, 338, "豐原", True, False, "台中市", "right"),
    (140, 358, "潭子", False, False, "台中市", "none"),
    (144, 378, "台中", True, False, "台中市", "right"),
    (140, 396, "新烏日", True, False, "台中市", "right"),

    # Changhua & Jiji Line (Mountain and Coast join at Changhua)
    (126, 412, "彰化", True, False, "彰化縣", "left"),
    (130, 432, "員林", True, False, "彰化縣", "left"),
    (134, 452, "田中", True, False, "彰化縣", "none"),
    (138, 468, "二水", True, False, "彰化縣", "left"),
    # Jiji Line (Nantou)
    (152, 470, "濁水", False, True, "南投縣", "none"),
    (168, 472, "集集", True, True, "南投縣", "top"),
    (184, 474, "水里", False, True, "南投縣", "none"),
    (198, 476, "車埕", True, True, "南投縣", "right"),

    # Yunlin & Chiayi
    (134, 488, "斗六", True, False, "雲林縣", "left"),
    (130, 504, "斗南", True, False, "雲林縣", "left"),
    (126, 522, "民雄", False, False, "嘉義縣市", "none"),
    (122, 540, "嘉義", True, False, "嘉義縣市", "left"),

    # Tainan & Shalun Line
    (116, 562, "新營", True, False, "台南市", "left"),
    (112, 580, "善化", True, False, "台南市", "left"),
    (108, 598, "永康", False, False, "台南市", "none"),
    (104, 614, "台南", True, False, "台南市", "left"),
    (112, 624, "中洲", False, False, "台南市", "none"),
    (124, 626, "沙崙", True, True, "台南市", "bottom"),

    # Kaohsiung & Pingtung
    (108, 636, "岡山", True, False, "高雄市", "left"),
    (112, 650, "新左營", True, False, "高雄市", "left"),
    (116, 664, "高雄", True, False, "高雄市", "left"),
    (126, 668, "鳳山", True, False, "高雄市", "bottom"),
    (144, 672, "屏東", True, False, "屏東縣", "top"),
    (158, 678, "潮州", True, False, "屏東縣", "bottom"),
    (174, 684, "林邊", False, False, "屏東縣", "none"),
    (188, 688, "枋寮", True, False, "屏東縣", "bottom"),

    # South Link Line to Taitung
    (222, 664, "大武", True, False, "台東縣", "bottom"),
    (248, 642, "金崙", False, False, "台東縣", "none"),
    (268, 620, "太麻里", True, False, "台東縣", "right"),
    (284, 598, "知本", True, False, "台東縣", "right"),
    (296, 574, "台東", True, False, "台東縣", "right"),

    # Eastern Trunk Line (Taitung -> Hualien)
    (306, 550, "鹿野", False, False, "台東縣", "none"),
    (316, 528, "關山", True, False, "台東縣", "right"),
    (326, 506, "池上", True, False, "台東縣", "right"),
    (338, 480, "富里", False, False, "花蓮縣", "none"),
    (350, 456, "玉里", True, False, "花蓮縣", "right"),
    (360, 432, "瑞穗", True, False, "花蓮縣", "right"),
    (368, 410, "光復", False, False, "花蓮縣", "none"),
    (376, 386, "鳳林", False, False, "花蓮縣", "none"),
    (384, 362, "壽豐", False, False, "花蓮縣", "none"),
    (392, 338, "吉安", False, False, "花蓮縣", "none"),
    (400, 314, "花蓮", True, False, "花蓮縣", "right"),

    # North Link Line & Yilan Line (Hualien -> Yilan -> Badu)
    (406, 284, "新城", True, False, "花蓮縣", "right"),
    (414, 252, "和平", False, False, "花蓮縣", "none"),
    (420, 222, "南澳", True, False, "宜蘭縣", "right"),
    (424, 194, "蘇澳新", True, False, "宜蘭縣", "right"),
    (434, 196, "蘇澳", True, True, "宜蘭縣", "bottom"),
    (426, 172, "羅東", True, False, "宜蘭縣", "right"),
    (424, 150, "宜蘭", True, False, "宜蘭縣", "right"),
    (422, 132, "礁溪", True, False, "宜蘭縣", "right"),
    (418, 120, "頭城", False, False, "宜蘭縣", "none"),
]

def generate_clean_svg():
    # Stations layer
    stations_svg = []
    for (x, y, name, is_hub, is_branch, county, label_pos) in STATIONS_DATA:
        dot_r = 5.5 if is_hub else (4.5 if is_branch else 3.5)
        dot_fill = "#ef4444" if is_hub else ("#10b981" if is_branch else "#3b82f6")
        dot_stroke = "#ffffff"
        dot_stroke_w = 1.8 if is_hub else 1.2
        
        # Label rendering
        label_markup = ""
        if label_pos != "none":
            star = "★ " if is_hub else ""
            badge_class = "station-pill-hub" if is_hub else ("station-pill-branch" if is_branch else "station-pill-main")
            
            # Label offsets
            if label_pos == "left":
                lx, ly, anchor = x - 9, y + 4, "end"
            elif label_pos == "right":
                lx, ly, anchor = x + 9, y + 4, "start"
            elif label_pos == "top":
                lx, ly, anchor = x, y - 9, "middle"
            elif label_pos == "bottom":
                lx, ly, anchor = x, y + 16, "middle"
            else:
                lx, ly, anchor = x + 8, y + 4, "start"

            font_weight = "800" if is_hub else "700"
            font_size = "11px" if is_hub else "10px"
            text_color = "#b91c1c" if is_hub else ("#047857" if is_branch else "#1e293b")

            label_markup = f'''<text x="{lx}" y="{ly}" text-anchor="{anchor}" font-size="{font_size}" font-weight="{font_weight}" fill="{text_color}" class="map-station-name">{star}{name}</text>'''

        stations_svg.append(f'''
        <g class="map-station-node" data-station="{name}" data-county="{county}" onclick="modalPickStation('{name}')">
            <circle cx="{x}" cy="{y}" r="14" fill="none" stroke="none" class="station-hitbox" />
            <circle cx="{x}" cy="{y}" r="{dot_r}" fill="{dot_fill}" stroke="{dot_stroke}" stroke-width="{dot_stroke_w}" class="station-dot" />
            {label_markup}
        </g>''')

    stations_svg_str = "\n".join(stations_svg)

    svg_code = f'''
    <div class="taiwan-map-container" id="taiwanMapContainer">
        <div class="map-toolbar">
            <div class="map-hint-box">
                <span class="map-hint-icon">🗺️</span>
                <span class="map-hint-text"><strong>地圖直接點選車站</strong>（★ 紅色為自強大站，綠色為觀光支線），選完自動跳下一站或關閉！</span>
            </div>
            <div class="map-legend">
                <span class="legend-item"><span class="legend-dot hub"></span> 自強特快大站</span>
                <span class="legend-item"><span class="legend-dot branch"></span> 觀光支線</span>
                <span class="legend-item"><span class="legend-dot main"></span> 沿線各站</span>
            </div>
        </div>

        <div class="map-viewport">
            <svg viewBox="50 20 420 690" class="taiwan-rail-svg" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <filter id="mapShadow" x="-10%" y="-10%" width="120%" height="120%">
                        <feDropShadow dx="0" dy="3" stdDeviation="4" flood-opacity="0.12" flood-color="#0f172a" />
                    </filter>
                </defs>

                <!-- Taiwan Island Mainland Geography Outline -->
                <path class="taiwan-island-bg" d="
                    M 385,52 C 415,55 450,105 440,165
                    C 435,205 425,275 410,350
                    C 395,425 350,535 315,605
                    C 285,655 235,700 200,705
                    C 185,705 160,695 140,685
                    C 105,665 95,615 100,565
                    C 105,515 115,445 110,385
                    C 100,315 115,245 145,195
                    C 175,145 230,110 295,85
                    C 345,60 365,48 385,52 Z
                " fill="#eaf4db" stroke="#a3cf78" stroke-width="2.5" filter="url(#mapShadow)" />

                <!-- Soft County Region Background Patches -->
                <g class="county-zones" opacity="0.6">
                    <path d="M 350,55 Q 390,50 405,70 Q 370,80 350,55 Z" fill="#d9ebd0" class="county-shape" data-county="基隆市" onclick="filterByCountyFromMap('基隆市')" />
                    <path d="M 270,95 Q 310,90 320,120 Q 280,125 270,95 Z" fill="#d0e6c5" class="county-shape" data-county="台北市" onclick="filterByCountyFromMap('台北市')" />
                    <path d="M 220,135 Q 275,105 345,110 Q 430,125 430,155 Q 355,145 220,135 Z" fill="#d9ebd0" class="county-shape" data-county="新北市" onclick="filterByCountyFromMap('新北市')" />
                    <path d="M 165,185 Q 225,155 235,200 Q 175,220 165,185 Z" fill="#e2f0d9" class="county-shape" data-county="桃園市" onclick="filterByCountyFromMap('桃園市')" />
                    <path d="M 120,235 Q 175,215 185,260 Q 130,270 120,235 Z" fill="#d4eac9" class="county-shape" data-county="新竹縣市" onclick="filterByCountyFromMap('新竹縣市')" />
                    <path d="M 90,285 Q 145,265 150,335 Q 95,350 90,285 Z" fill="#e5f2dc" class="county-shape" data-county="苗栗縣" onclick="filterByCountyFromMap('苗栗縣')" />
                    <path d="M 90,355 Q 160,345 160,435 Q 105,445 90,355 Z" fill="#d2e8c7" class="county-shape" data-county="台中市" onclick="filterByCountyFromMap('台中市')" />
                    <path d="M 110,450 Q 150,445 150,515 Q 115,520 110,450 Z" fill="#e1f0d8" class="county-shape" data-county="彰化縣" onclick="filterByCountyFromMap('彰化縣')" />
                    <path d="M 150,455 Q 235,455 225,535 Q 150,530 150,455 Z" fill="#d5ebcc" class="county-shape" data-county="南投縣" onclick="filterByCountyFromMap('南投縣')" />
                    <path d="M 110,525 Q 145,523 140,560 Q 110,560 110,525 Z" fill="#e3f1db" class="county-shape" data-county="雲林縣" onclick="filterByCountyFromMap('雲林縣')" />
                    <path d="M 100,565 Q 140,563 135,605 Q 100,605 100,565 Z" fill="#d7eccf" class="county-shape" data-county="嘉義縣市" onclick="filterByCountyFromMap('嘉義縣市')" />
                    <path d="M 85,610 Q 130,607 130,685 Q 85,685 85,610 Z" fill="#e0efd7" class="county-shape" data-county="台南市" onclick="filterByCountyFromMap('台南市')" />
                    <path d="M 90,690 Q 140,687 145,745 Q 95,745 90,690 Z" fill="#d4eac9" class="county-shape" data-county="高雄市" onclick="filterByCountyFromMap('高雄市')" />
                    <path d="M 135,740 Q 190,740 185,765 Q 135,760 135,740 Z" fill="#e3f1db" class="county-shape" data-county="屏東縣" onclick="filterByCountyFromMap('屏東縣')" />
                    <path d="M 395,155 Q 440,165 425,285 Q 385,275 395,155 Z" fill="#d8edd0" class="county-shape" data-county="宜蘭縣" onclick="filterByCountyFromMap('宜蘭縣')" />
                    <path d="M 335,335 Q 410,325 370,575 Q 315,565 335,335 Z" fill="#d0e7c5" class="county-shape" data-county="花蓮縣" onclick="filterByCountyFromMap('花蓮縣')" />
                    <path d="M 245,595 Q 325,585 265,735 Q 215,735 245,595 Z" fill="#dcefd6" class="county-shape" data-county="台東縣" onclick="filterByCountyFromMap('台東縣')" />
                </g>

                <!-- County Region Geographic Labels -->
                <g class="county-map-labels" font-size="11px" font-weight="800" fill="#4d7c0f" opacity="0.85">
                    <text x="358" y="46" class="map-label-pill" onclick="filterByCountyFromMap('基隆市')">基隆</text>
                    <text x="290" y="80" class="map-label-pill" onclick="filterByCountyFromMap('台北市')">台北市</text>
                    <text x="340" y="112" class="map-label-pill" onclick="filterByCountyFromMap('新北市')">新北市</text>
                    <text x="220" y="142" class="map-label-pill" onclick="filterByCountyFromMap('桃園市')">桃園</text>
                    <text x="175" y="215" class="map-label-pill" onclick="filterByCountyFromMap('新竹縣市')">新竹</text>
                    <text x="155" y="285" class="map-label-pill" onclick="filterByCountyFromMap('苗栗縣')">苗栗</text>
                    <text x="170" y="365" class="map-label-pill" onclick="filterByCountyFromMap('台中市')">台中</text>
                    <text x="98" y="455" class="map-label-pill" onclick="filterByCountyFromMap('彰化縣')">彰化</text>
                    <text x="195" y="455" class="map-label-pill" onclick="filterByCountyFromMap('南投縣')">南投 (集集線)</text>
                    <text x="100" y="515" class="map-label-pill" onclick="filterByCountyFromMap('雲林縣')">雲林</text>
                    <text x="150" y="555" class="map-label-pill" onclick="filterByCountyFromMap('嘉義縣市')">嘉義</text>
                    <text x="145" y="605" class="map-label-pill" onclick="filterByCountyFromMap('台南市')">台南</text>
                    <text x="145" y="655" class="map-label-pill" onclick="filterByCountyFromMap('高雄市')">高雄</text>
                    <text x="175" y="670" class="map-label-pill" onclick="filterByCountyFromMap('屏東縣')">屏東</text>
                    <text x="415" y="195" class="map-label-pill" onclick="filterByCountyFromMap('宜蘭縣')">宜蘭</text>
                    <text x="365" y="350" class="map-label-pill" onclick="filterByCountyFromMap('花蓮縣')">花蓮</text>
                    <text x="295" y="635" class="map-label-pill" onclick="filterByCountyFromMap('台東縣')">台東</text>
                </g>

                <!-- ============================================== -->
                <!-- Railway Tracks (Base Track & Dashed Rail Ties) -->
                <!-- ============================================== -->
                
                <!-- 1. Western Trunk North -->
                <path d="M 385,52 L 375,62 L 365,70 L 355,78 L 345,86 L 335,92 L 325,98 L 318,102 L 308,108 L 296,112 L 282,118 L 270,124 L 256,132 L 245,140 L 235,148 L 225,156 L 216,164 L 204,174 L 194,184 L 184,194 L 174,204 L 164,214 L 154,222 L 146,230 L 138,238 L 130,246 L 122,254 L 110,272" fill="none" stroke="#1e293b" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M 385,52 L 375,62 L 365,70 L 355,78 L 345,86 L 335,92 L 325,98 L 318,102 L 308,108 L 296,112 L 282,118 L 270,124 L 256,132 L 245,140 L 235,148 L 225,156 L 216,164 L 204,174 L 194,184 L 184,194 L 174,204 L 164,214 L 154,222 L 146,230 L 138,238 L 130,246 L 122,254 L 110,272" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-dasharray="5 4" stroke-linecap="butt" />

                <!-- 2. Mountain Line (Zhunan -> Miaoli -> Taichung -> Changhua) -->
                <path d="M 110,272 L 124,286 L 128,302 L 132,320 L 136,338 L 140,358 L 144,378 L 140,396 L 126,412" fill="none" stroke="#1e293b" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M 110,272 L 124,286 L 128,302 L 132,320 L 136,338 L 140,358 L 144,378 L 140,396 L 126,412" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-dasharray="5 4" stroke-linecap="butt" />

                <!-- 3. Coast Line (Zhunan -> Baishatun -> Dajia -> Shalu -> Changhua) -->
                <path d="M 110,272 L 96,284 L 90,300 L 88,318 L 92,334 L 96,348 L 104,368 L 110,384 L 126,412" fill="none" stroke="#1e293b" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M 110,272 L 96,284 L 90,300 L 88,318 L 92,334 L 96,348 L 104,368 L 110,384 L 126,412" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-dasharray="5 4" stroke-linecap="butt" />

                <!-- 4. Western Trunk South (Changhua -> Chiayi -> Tainan -> Kaohsiung -> Chaozhou -> Fangliao) -->
                <path d="M 126,412 L 130,432 L 134,452 L 138,468 L 134,488 L 130,504 L 126,522 L 122,540 L 116,562 L 112,580 L 108,598 L 104,614 L 112,624 L 108,636 L 112,650 L 116,664 L 126,668 L 144,672 L 158,678 L 174,684 L 188,688" fill="none" stroke="#1e293b" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M 126,412 L 130,432 L 134,452 L 138,468 L 134,488 L 130,504 L 126,522 L 122,540 L 116,562 L 112,580 L 108,598 L 104,614 L 112,624 L 108,636 L 112,650 L 116,664 L 126,668 L 144,672 L 158,678 L 174,684 L 188,688" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-dasharray="5 4" stroke-linecap="butt" />

                <!-- 5. South Link Line (Fangliao -> Taitung) -->
                <path d="M 188,688 L 222,664 L 248,642 L 268,620 L 284,598 L 296,574" fill="none" stroke="#1e293b" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M 188,688 L 222,664 L 248,642 L 268,620 L 284,598 L 296,574" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-dasharray="5 4" stroke-linecap="butt" />

                <!-- 6. Eastern Taitung Line (Taitung -> Hualien) -->
                <path d="M 296,574 L 306,550 L 316,528 L 326,506 L 338,480 L 350,456 L 360,432 L 368,410 L 376,386 L 384,362 L 392,338 L 400,314" fill="none" stroke="#1e293b" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M 296,574 L 306,550 L 316,528 L 326,506 L 338,480 L 350,456 L 360,432 L 368,410 L 376,386 L 384,362 L 392,338 L 400,314" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-dasharray="5 4" stroke-linecap="butt" />

                <!-- 7. North Link Line & Yilan Line (Hualien -> Suao -> Yilan -> Badu) -->
                <path d="M 400,314 L 406,284 L 414,252 L 420,222 L 424,194 L 426,172 L 424,150 L 422,132 L 418,120 L 412,118 L 400,108 L 388,96 L 382,88 L 375,78 L 365,70" fill="none" stroke="#1e293b" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M 400,314 L 406,284 L 414,252 L 420,222 L 424,194 L 426,172 L 424,150 L 422,132 L 418,120 L 412,118 L 400,108 L 388,96 L 382,88 L 375,78 L 365,70" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-dasharray="5 4" stroke-linecap="butt" />

                <!-- 8. Branch Lines (Amber Orange) -->
                <!-- Shenao Line -->
                <path d="M 375,78 L 398,48 L 408,50" fill="none" stroke="#d97706" stroke-width="3" stroke-dasharray="4 3" stroke-linecap="round" />
                <!-- Pingxi Line -->
                <path d="M 388,96 L 376,102 L 364,108 L 352,112" fill="none" stroke="#d97706" stroke-width="3" stroke-dasharray="4 3" stroke-linecap="round" />
                <!-- Neiwan & Liujia Line -->
                <path d="M 122,254 L 134,258 L 144,252" fill="none" stroke="#d97706" stroke-width="3" stroke-dasharray="4 3" stroke-linecap="round" />
                <path d="M 134,258 L 148,266 L 158,274" fill="none" stroke="#d97706" stroke-width="3" stroke-dasharray="4 3" stroke-linecap="round" />
                <!-- Jiji Line -->
                <path d="M 138,468 L 152,470 L 168,472 L 184,474 L 198,476" fill="none" stroke="#d97706" stroke-width="3" stroke-dasharray="4 3" stroke-linecap="round" />
                <!-- Shalun Line -->
                <path d="M 112,624 L 124,626" fill="none" stroke="#d97706" stroke-width="3" stroke-dasharray="4 3" stroke-linecap="round" />
                <!-- Suao Branch -->
                <path d="M 424,194 L 434,196" fill="none" stroke="#d97706" stroke-width="3" stroke-dasharray="4 3" stroke-linecap="round" />

                <!-- ============================================== -->
                <!-- Station Nodes Layer -->
                <!-- ============================================== -->
                <g class="map-stations-layer">
                    {stations_svg_str}
                </g>
            </svg>
        </div>
    </div>
    '''
    return svg_code

print("Perfect Taiwan Rail SVG Map generator created.")
