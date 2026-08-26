import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Express major stations set (每個縣市不超過5個核心特等/一等自強號大站)
EXPRESS_MAJOR_STATIONS_JS = """
        const EXPRESS_MAJOR_STATIONS = new Set([
            // 基隆市
            '基隆', '八堵', '七堵',
            // 台北市
            '南港', '松山', '台北', '萬華',
            // 新北市
            '板橋', '樹林', '鶯歌', '瑞芳', '雙溪',
            // 桃園市
            '桃園', '中壢', '楊梅',
            // 新竹縣市
            '竹北', '新竹',
            // 苗栗縣
            '竹南', '苗栗', '通霄', '苑裡',
            // 台中市
            '豐原', '台中', '新烏日', '大甲', '沙鹿',
            // 彰化縣
            '彰化', '員林', '田中', '二水',
            // 雲林縣
            '斗六', '斗南',
            // 嘉義縣市
            '大林', '民雄', '嘉義',
            // 台南市
            '新營', '善化', '台南',
            // 高雄市
            '岡山', '楠梓', '新左營', '高雄', '鳳山',
            // 屏東縣
            '屏東', '潮州', '南州', '林邊', '枋寮',
            // 宜蘭縣
            '頭城', '礁溪', '宜蘭', '羅東', '蘇澳新',
            // 花蓮縣
            '新城(太魯閣)', '花蓮', '吉安', '瑞穗', '玉里',
            // 台東縣
            '池上', '關山', '鹿野', '台東', '知本'
        ]);
"""

# 1. Add CSS for Express Major Station Button
css_express_station = """
        .station-btn.express-hub {
            background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%);
            border: 1.5px solid #f43f5e;
            color: #be123c;
            font-weight: 800;
            box-shadow: 0 1px 3px rgba(244, 63, 94, 0.15);
        }
        .station-btn.express-hub:hover {
            background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%);
            color: #ffffff;
            border-color: #be123c;
            box-shadow: 0 4px 10px rgba(244, 63, 94, 0.35);
        }
        [data-theme="dark"] .station-btn.express-hub {
            background: rgba(244, 63, 94, 0.18);
            border-color: #fb7185;
            color: #fda4af;
        }
        [data-theme="dark"] .station-btn.express-hub:hover {
            background: #e11d48;
            color: #ffffff;
            border-color: #f43f5e;
        }
        .hub-legend-bar {
            padding: 8px 24px;
            font-size: 0.8rem;
            color: var(--text-muted);
            background: var(--bg-subtle);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .hub-legend-tag {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
        }
"""

css_insert_target = "</style>"
html = html.replace(css_insert_target, css_express_station + "\n    </style>", 1)

# 2. Add Legend bar into Station Picker Modal
legend_bar_html = """
            <div class="hub-legend-bar">
                <span>圖例說明：</span>
                <span class="hub-legend-tag" style="background:#ffe4e6; border:1px solid #f43f5e; color:#be123c;">⭐ 紅色為自強號停靠核心大站</span>
                <span class="hub-legend-tag" style="background:var(--bg-subtle); border:1px solid var(--border-color); color:var(--text-main);">一般區間車站</span>
            </div>
"""

legend_insert_target = '<div class="modal-tabs-nav" id="modalCountyTabs"></div>'
html = html.replace(legend_insert_target, legend_insert_target + "\n" + legend_bar_html, 1)

# 3. Add EXPRESS_MAJOR_STATIONS in JS and update renderStationModal
js_insert_target = "const ALL_STATIONS = Array.from(new Set(COUNTY_GROUPS.flatMap(g => g.stations)));"
html = html.replace(js_insert_target, EXPRESS_MAJOR_STATIONS_JS + "\n        " + js_insert_target, 1)

# 4. Update renderStationModal to attach .express-hub class and ⭐ icon
old_render_btn = "${group.stations.map(st => `\n                            <button class=\"station-btn\" onclick=\"modalPickStation('${st}')\">${st}</button>\n                        `).join('')}"

new_render_btn = """${group.stations.map(st => {
                            const isHub = EXPRESS_MAJOR_STATIONS.has(st);
                            const hubClass = isHub ? 'express-hub' : '';
                            const starIcon = isHub ? '⭐ ' : '';
                            return `<button class="station-btn ${hubClass}" onclick="modalPickStation('${st}')" title="${isHub ? '自強號特快停靠核心大站' : ''}">${starIcon}${st}</button>`;
                        }).join('')}"""

html = html.replace(old_render_btn, new_render_btn, 1)

# 5. Bump version to v2.8.0
html = html.replace('v2.7.0 (2026.07.01版)', 'v2.8.0 (2026.07.01版)')
html = html.replace('核心版本: v2.7.0', '核心版本: v2.8.0 (自強號特快大站醒目標色)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Applied Express Major Stations Highlighting and updated index.html to v2.8.0!")
