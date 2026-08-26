import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Define BRANCH_LINE_STATIONS JS set
branch_stations_js = """
        const BRANCH_LINE_STATIONS = new Set([
            // 平溪/深澳線
            '海科館', '八斗子', '大華', '十分', '望古', '嶺腳', '平溪', '菁桐',
            // 內灣/六家線
            '千甲', '新莊', '竹中', '六家', '上員', '榮華', '竹東', '橫山', '九讚頭', '合興', '富貴', '內灣',
            // 集集線
            '源泉', '濁水', '龍泉', '集集', '水里', '車埕',
            // 沙崙線
            '長榮大學', '沙崙'
        ]);
"""

# Insert BRANCH_LINE_STATIONS right after EXPRESS_MAJOR_STATIONS
html = html.replace('const EXPRESS_MAJOR_STATIONS = new Set([', branch_stations_js + '\n        const EXPRESS_MAJOR_STATIONS = new Set([', 1)

# 2. Add CSS for .station-btn.branch-station
branch_css = """
        .station-btn.branch-station {
            background: #f0fdf4;
            border: 1px solid #86efac;
            color: #166534;
            font-weight: 600;
        }
        .station-btn.branch-station:hover {
            background: #dcfce7;
            border-color: #4ade80;
            color: #14532d;
            box-shadow: 0 2px 6px rgba(34, 197, 94, 0.2);
        }
        [data-theme="dark"] .station-btn.branch-station {
            background: rgba(22, 101, 52, 0.22);
            border-color: rgba(74, 222, 128, 0.35);
            color: #86efac;
        }
        [data-theme="dark"] .station-btn.branch-station:hover {
            background: rgba(22, 101, 52, 0.45);
            border-color: #4ade80;
            color: #bbf7d0;
        }
"""

html = html.replace('</style>', branch_css + '\n    </style>', 1)

# 3. Update legend bar in Station Modal
old_legend = """            <div class="hub-legend-bar">
                <span>圖例說明：</span>
                <span class="hub-legend-tag" style="background:#ffe4e6; border:1px solid #f43f5e; color:#be123c;">⭐ 紅色為自強號停靠核心大站</span>
                <span class="hub-legend-tag" style="background:var(--bg-subtle); border:1px solid var(--border-color); color:var(--text-main);">一般區間車站</span>
            </div>"""

new_legend = """            <div class="hub-legend-bar">
                <span>圖例說明：</span>
                <span class="hub-legend-tag" style="background:#ffe4e6; border:1px solid #f43f5e; color:#be123c;">⭐ 紅色為自強號大站</span>
                <span class="hub-legend-tag" style="background:#f0fdf4; border:1px solid #86efac; color:#166534;">🌿 淺綠為觀光支線小站</span>
                <span class="hub-legend-tag" style="background:var(--bg-subtle); border:1px solid var(--border-color); color:var(--text-main);">一般幹線車站</span>
            </div>"""

html = html.replace(old_legend, new_legend, 1)

# 4. Update renderStationModal to apply .branch-station class and 🌿 icon
old_render_btns = """                            const isHub = EXPRESS_MAJOR_STATIONS.has(st);
                            const hubClass = isHub ? 'express-hub' : '';
                            const starIcon = isHub ? '⭐ ' : '';
                            return `<button class="station-btn ${hubClass}" onclick="modalPickStation('${st}')" title="${isHub ? '自強號特快停靠核心大站' : ''}">${starIcon}${st}</button>`;"""

new_render_btns = """                            const isHub = EXPRESS_MAJOR_STATIONS.has(st);
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

                            return `<button class="station-btn ${btnClass}" onclick="modalPickStation('${st}')" title="${titleTip}">${iconPrefix}${st}</button>`;"""

html = html.replace(old_render_btns, new_render_btns, 1)

# 5. Bump version to v3.2.0 (SemVer Minor: Branch Line Subtle Green Visual Indicators)
html = html.replace('v3.1.2 (2026.07.01版)', 'v3.2.0 (2026.07.01版)')
html = html.replace('核心版本: v3.1.2', '核心版本: v3.2.0 (觀光支線清新森林綠標示 · 自強號大站紅光 · 階層清晰)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Added Branch Line Subtle Visual Indicators and bumped version to v3.2.0!")
