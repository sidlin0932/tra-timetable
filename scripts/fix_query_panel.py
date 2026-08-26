import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the entire query-panel section with a perfectly structured, clean layout
clean_query_panel_html = """        <section class="query-panel">
            <!-- Row 1: Station Inputs & Departure Time -->
            <div class="query-main-row">
                <div class="form-group origin-group">
                    <label class="form-label" for="originInput">🚩 出發站 (起點)</label>
                    <div class="station-input-box">
                        <input type="text" id="originInput" class="station-input" value="板橋" placeholder="輸入站名 (如: 台北、新竹)..." autocomplete="off">
                        <button class="btn-station-picker" onclick="openStationModal('origin')">🗺️ 依縣市選站</button>
                        <div class="autocomplete-list" id="originAutoList"></div>
                    </div>
                </div>

                <div class="swap-wrapper">
                    <button class="btn-swap" onclick="swapStations()" title="對調出發與抵達站">⇄</button>
                </div>

                <div class="form-group dest-group">
                    <label class="form-label" for="destInput">🏁 抵達站 (終點)</label>
                    <div class="station-input-box">
                        <input type="text" id="destInput" class="station-input" value="台北" placeholder="輸入站名 (如: 內灣、花蓮)..." autocomplete="off">
                        <button class="btn-station-picker" onclick="openStationModal('dest')">🗺️ 依縣市選站</button>
                        <div class="autocomplete-list" id="destAutoList"></div>
                    </div>
                </div>

                <div class="form-group time-group">
                    <label class="form-label" for="timeInput">🕒 出發時間</label>
                    <div class="time-select-group">
                        <input type="time" id="timeInput" class="time-input" value="05:00">
                        <button class="btn-current-time" onclick="setCurrentTime()" title="設為現在時間">現在</button>
                    </div>
                </div>
            </div>

            <!-- Row 2: Quick Hubs Bar (Full Width) -->
            <div class="quick-hubs-bar">
                <span class="quick-hubs-title">⚡ 常用大站：</span>
                <div class="quick-hubs-list">
                    <button class="quick-hub-btn" onclick="quickFillStation('origin', '台北')">🚩 台北</button>
                    <button class="quick-hub-btn" onclick="quickFillStation('origin', '板橋')">🚩 板橋</button>
                    <button class="quick-hub-btn" onclick="quickFillStation('origin', '新竹')">🚩 新竹</button>
                    <button class="quick-hub-btn" onclick="quickFillStation('origin', '台中')">🚩 台中</button>
                    <button class="quick-hub-btn" onclick="quickFillStation('dest', '瑞芳')">🏁 瑞芳</button>
                    <button class="quick-hub-btn" onclick="quickFillStation('dest', '八斗子')">🏁 八斗子</button>
                    <button class="quick-hub-btn" onclick="quickFillStation('dest', '花蓮')">🏁 花蓮</button>
                    <button class="quick-hub-btn" onclick="quickFillStation('dest', '台東')">🏁 台東</button>
                    <button class="quick-hub-btn" onclick="quickFillStation('dest', '內灣')">🏁 內灣</button>
                    <button class="quick-hub-btn" onclick="quickFillStation('dest', '高雄')">🏁 高雄</button>
                </div>
            </div>

            <!-- Row 3: Filter Preferences & Search Action Button -->
            <div class="query-filter-row">
                <div class="form-group">
                    <span class="form-label">🔀 轉乘條件</span>
                    <div class="segmented-control" id="transferFilter">
                        <button class="segment-btn active" onclick="setTransferCondition('all', this)">無限次轉乘 (推薦)</button>
                        <button class="segment-btn" onclick="setTransferCondition('max2', this)">最多 2 次</button>
                        <button class="segment-btn" onclick="setTransferCondition('max1', this)">最多 1 次</button>
                        <button class="segment-btn" onclick="setTransferCondition('direct', this)">限直達車</button>
                    </div>
                </div>

                <div class="form-group">
                    <span class="form-label">🚆 車種偏好</span>
                    <div class="segmented-control" id="typeFilter">
                        <button class="segment-btn active" onclick="setTypeFilter('all', this)">全部車種</button>
                        <button class="segment-btn" onclick="setTypeFilter('trpass', this)">✅ TR-PASS 適用</button>
                        <button class="segment-btn" onclick="setTypeFilter('express', this)">對號特快</button>
                        <button class="segment-btn" onclick="setTypeFilter('local', this)">非對號區間</button>
                    </div>
                </div>

                <div class="search-btn-wrapper">
                    <button class="btn-search" onclick="executeSearch()">
                        <span>🔍</span> 查詢乘車方案
                    </button>
                </div>
            </div>
        </section>"""

old_qp_start = html.find('<section class="query-panel">')
old_qp_end = html.find('</section>\n\n        <section class="sort-bar"')

if old_qp_start != -1 and old_qp_end != -1:
    html = html[:old_qp_start] + clean_query_panel_html + html[old_qp_end + len('</section>'):]

# Replace / Add CSS for query panel layout
clean_query_css = """
        /* ==========================================================
           PIXEL-PERFECT QUERY PANEL (DESKTOP & MOBILE)
           ========================================================== */
        .query-panel {
            background: var(--bg-card);
            border-radius: var(--radius);
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border-color);
            padding: 24px;
            margin-bottom: 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .query-main-row {
            display: grid;
            grid-template-columns: 1fr auto 1fr 180px;
            gap: 14px;
            align-items: flex-end;
        }

        .swap-wrapper {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 44px;
            margin-bottom: 2px;
        }

        .btn-swap {
            width: 42px;
            height: 42px;
            border-radius: 50%;
            border: 1.5px solid var(--border-color);
            background: var(--bg-subtle);
            color: var(--primary);
            font-size: 1.25rem;
            font-weight: 800;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .btn-swap:hover {
            background: var(--primary);
            color: #ffffff;
            border-color: var(--primary);
            transform: rotate(180deg) scale(1.08);
            box-shadow: 0 4px 10px rgba(2, 132, 199, 0.3);
        }

        .time-select-group {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .time-input {
            flex: 1;
            padding: 9px 12px;
            border: 1.5px solid var(--border-color);
            border-radius: 8px;
            background: var(--bg-subtle);
            color: var(--text-main);
            font-family: 'Outfit', sans-serif;
            font-size: 1rem;
            font-weight: 700;
            outline: none;
        }
        .time-input:focus { border-color: var(--primary); }

        .btn-current-time {
            padding: 9px 12px;
            background: var(--bg-subtle);
            border: 1.5px solid var(--border-color);
            border-radius: 8px;
            color: var(--text-main);
            font-size: 0.85rem;
            font-weight: 700;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.15s;
        }
        .btn-current-time:hover {
            background: var(--primary);
            color: #fff;
            border-color: var(--primary);
        }

        .quick-hubs-bar {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            background: var(--bg-subtle);
            border-radius: 8px;
            border: 1px solid var(--border-color);
            flex-wrap: wrap;
        }
        .quick-hubs-title {
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--text-muted);
            white-space: nowrap;
        }
        .quick-hubs-list {
            display: flex;
            align-items: center;
            gap: 6px;
            flex-wrap: wrap;
        }
        .quick-hub-btn {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 4px 10px;
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--text-main);
            cursor: pointer;
            transition: all 0.15s;
        }
        .quick-hub-btn:hover {
            background: var(--primary-light);
            color: var(--primary);
            border-color: var(--primary);
            transform: translateY(-1px);
        }

        .query-filter-row {
            display: flex;
            align-items: flex-end;
            gap: 16px;
            flex-wrap: wrap;
        }
        .search-btn-wrapper {
            margin-left: auto;
            align-self: flex-end;
        }

        @media (max-width: 900px) {
            .query-main-row {
                grid-template-columns: 1fr;
                gap: 10px;
            }
            .swap-wrapper {
                height: auto;
                margin: 0;
            }
            .btn-swap {
                transform: rotate(90deg);
                margin: 2px auto;
            }
            .btn-swap:hover {
                transform: rotate(270deg);
            }
            .search-btn-wrapper {
                margin-left: 0;
                width: 100%;
            }
            .btn-search {
                width: 100%;
                justify-content: center;
            }
            .query-filter-row {
                flex-direction: column;
                align-items: stretch;
            }
        }
"""

html = html.replace('</style>', clean_query_css + '\n    </style>', 1)

# Bump version to v3.6.1
html = html.replace('v3.6.0 (2026.07.01版)', 'v3.6.1 (2026.07.01版)')
html = html.replace('核心版本: v3.6.0', '核心版本: v3.6.1 (修復未閉合網格標籤 · 桌面與手機雙端版面重構)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Fixed HTML structure, rebuilt query panel, and bumped to v3.6.1!")
