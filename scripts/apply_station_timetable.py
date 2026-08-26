import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add CSS for clickable stations and Station Timetable Modal
station_css = """
        .clickable-station {
            cursor: pointer;
            text-decoration: underline;
            text-decoration-style: dotted;
            text-underline-offset: 3px;
            transition: color 0.15s;
        }
        .clickable-station:hover {
            color: var(--primary);
            text-decoration-style: solid;
        }
        .stop-chip.clickable {
            cursor: pointer;
            transition: all 0.15s;
        }
        .stop-chip.clickable:hover {
            background: var(--primary-light);
            color: var(--primary);
            border-color: var(--primary);
            font-weight: 700;
        }
"""

css_insert_target = "</style>"
html = html.replace(css_insert_target, station_css + "\n    </style>", 1)

# 2. Add Station Departures Modal HTML
station_modal_html = """
    <!-- Station Full Departures Timetable Modal -->
    <div class="modal-backdrop" id="stationDeparturesModal" onclick="closeStationDeparturesModal(event)">
        <div class="modal-dialog" style="max-width: 780px;" onclick="event.stopPropagation()">
            <div class="modal-header">
                <div>
                    <h3 id="stationDepModalTitle" style="display: flex; align-items: center; gap: 8px;">
                        📍 車站全日發車時刻表
                    </h3>
                    <p id="stationDepModalSubtitle" style="font-size: 0.85rem; color: var(--text-muted); margin-top: 4px;"></p>
                </div>
                <button class="btn-modal-close" onclick="closeStationDeparturesModal()">&times;</button>
            </div>
            
            <div style="padding: 10px 20px; background: var(--bg-subtle); border-bottom: 1px solid var(--border-color); display: flex; gap: 8px; flex-wrap: wrap; align-items: center; justify-content: space-between;">
                <div class="segmented-control" id="stationDepTypeFilter">
                    <button class="segment-btn active" onclick="filterStationDepTable('all', this)">全部班次</button>
                    <button class="segment-btn" onclick="filterStationDepTable('express', this)">對號特快</button>
                    <button class="segment-btn" onclick="filterStationDepTable('local', this)">非對號區間</button>
                    <button class="segment-btn" onclick="filterStationDepTable('trpass', this)">TR-PASS 適用</button>
                </div>
                <div style="font-size: 0.82rem; color: var(--text-muted);">
                    💡 點擊車次按鈕可開箱該列車全線時刻表
                </div>
            </div>

            <div class="modal-body" style="padding: 0 16px 20px; max-height: 65vh; overflow-y: auto;">
                <table class="train-modal-table">
                    <thead>
                        <tr>
                            <th style="width: 90px;">發車時間</th>
                            <th style="width: 160px;">車種車次</th>
                            <th>開往目的地</th>
                            <th style="width: 110px;">下一停靠站</th>
                            <th style="text-align: right; width: 110px;">票券說明</th>
                        </tr>
                    </thead>
                    <tbody id="stationDepModalBody"></tbody>
                </table>
            </div>
        </div>
    </div>
"""

modal_insert_target = "<!-- Train Full Timetable Modal -->"
html = html.replace(modal_insert_target, station_modal_html + "\n    " + modal_insert_target, 1)

# 3. Add openStationTimetable and filterStationDepTable JavaScript functions
js_station_functions = """
        let currentStationDepList = [];
        let currentStationDepFilter = 'all';

        function openStationTimetable(stationName) {
            const deps = [];
            allTimetableData.forEach(t => {
                const sIdx = t.stops.findIndex(s => s.station === stationName);
                if (sIdx !== -1 && sIdx < t.stops.length - 1) {
                    deps.push({
                        time: t.stops[sIdx].time,
                        timeMin: timeToMin(t.stops[sIdx].time),
                        train_number: t.train_number,
                        train_type: t.train_type,
                        train_model: t.train_model,
                        origin: t.origin,
                        dest: t.dest,
                        is_trpass: t.is_trpass,
                        line: t.line || '',
                        nextStation: t.stops[sIdx + 1].station
                    });
                }
            });

            deps.sort((a, b) => a.timeMin - b.timeMin);
            currentStationDepList = deps;

            document.getElementById('stationDepModalTitle').innerHTML = `📍 <strong>${stationName}</strong> 車站全日發車時刻表`;
            document.getElementById('stationDepModalSubtitle').textContent = `全日共收錄 ${deps.length} 班出發列車 · 依發車時間順序排列`;

            // Reset segmented control filter
            const filterBtns = document.querySelectorAll('#stationDepTypeFilter .segment-btn');
            filterBtns.forEach(b => b.classList.remove('active'));
            if (filterBtns[0]) filterBtns[0].classList.add('active');
            currentStationDepFilter = 'all';

            renderStationDepRows();
            document.getElementById('stationDeparturesModal').classList.add('open');
        }

        function filterStationDepTable(filterType, btn) {
            currentStationDepFilter = filterType;
            const filterBtns = document.querySelectorAll('#stationDepTypeFilter .segment-btn');
            filterBtns.forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            renderStationDepRows();
        }

        function renderStationDepRows() {
            const tbody = document.getElementById('stationDepModalBody');
            
            const filtered = currentStationDepList.filter(d => {
                if (currentStationDepFilter === 'trpass' && !d.is_trpass) return false;
                if (currentStationDepFilter === 'express' && !['自強號', '新自強(EMU3000)', '普悠瑪', '太魯閣', '莒光號'].includes(d.train_type)) return false;
                if (currentStationDepFilter === 'local' && !['區間車', '區間快'].includes(d.train_type)) return false;
                return true;
            });

            if (filtered.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:30px; color:var(--text-muted);">查無符合條件的發車班次</td></tr>`;
                return;
            }

            tbody.innerHTML = filtered.map((d, idx) => {
                const trBadge = d.is_trpass 
                    ? '<span class="badge-trpass">TR-PASS 適用</span>'
                    : '<span class="badge-not-trpass">不適用TR-PASS</span>';

                return `
                    <tr>
                        <td style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: var(--primary);">
                            ${d.time}
                        </td>
                        <td>
                            ${getTrainTypeBadge(d.train_type, d.train_number)}
                        </td>
                        <td>
                            <strong style="font-size: 1rem;">開往 ${d.dest}</strong>
                            <span style="font-size: 0.78rem; color: var(--text-muted); display: block;">始發: ${d.origin}</span>
                        </td>
                        <td style="color: var(--text-muted); font-size: 0.9rem;">
                            ➔ ${d.nextStation}
                        </td>
                        <td style="text-align: right;">
                            ${trBadge}
                        </td>
                    </tr>
                `;
            }).join('');
        }

        function closeStationDeparturesModal(e) {
            if (!e || e.target.id === 'stationDeparturesModal' || e.target.classList.contains('btn-modal-close')) {
                document.getElementById('stationDeparturesModal').classList.remove('open');
            }
        }
"""

js_insert_target = "function openTrainTimetable("
html = html.replace(js_insert_target, js_station_functions + "\n        function openTrainTimetable(", 1)

# 4. Make stations clickable in renderResults
html = html.replace('<div class="time-st-label">${route.legs[0].from} 出發</div>', '<div class="time-st-label"><span class="clickable-station" onclick="event.stopPropagation(); openStationTimetable(\'${route.legs[0].from}\')">${route.legs[0].from} 出發 📋</span></div>')
html = html.replace('<div class="time-st-label">${route.legs[route.legs.length-1].to} 抵達</div>', '<div class="time-st-label"><span class="clickable-station" onclick="event.stopPropagation(); openStationTimetable(\'${route.legs[route.legs.length-1].to}\')">${route.legs[route.legs.length-1].to} 抵達 📋</span></div>')
html = html.replace('第 ${legIdx + 1} 段：${leg.from} (${leg.dep}) ➔ ${leg.to} (${leg.arr})', '第 ${legIdx + 1} 段：<span class="clickable-station" onclick="openStationTimetable(\'${leg.from}\')">${leg.from}</span> (${leg.dep}) ➔ <span class="clickable-station" onclick="openStationTimetable(\'${leg.to}\')">${leg.to}</span> (${leg.arr})')
html = html.replace('<span class="stop-chip">${s.station} (${s.time})</span>', '<span class="stop-chip clickable" onclick="openStationTimetable(\'${s.station}\')" title="查看 ${s.station} 全日發車時刻表">${s.station} (${s.time})</span>')

# 5. Bump version to v2.7.0
html = html.replace('v2.6.0 (2026.07.01版)', 'v2.7.0 (2026.07.01版)')
html = html.replace('核心版本: v2.6.0', '核心版本: v2.7.0 (支援車站全日發車時刻表與列車時刻雙彈窗)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Applied Station Timetable Modal Feature and updated index.html to v2.7.0!")
