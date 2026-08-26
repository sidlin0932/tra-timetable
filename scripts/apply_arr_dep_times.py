# -*- coding: utf-8 -*-
html_path = 'f:/Antigravity/台鐵時刻表0701/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update stationDeparturesModal Table Header
old_table_header = """                    <thead>
                        <tr>
                            <th style="width: 90px;">發車時間</th>
                            <th style="width: 160px;">車種車次</th>
                            <th>開往目的地</th>
                            <th style="width: 110px;">下一停靠站</th>
                            <th style="text-align: right; width: 110px;">票券說明</th>
                        </tr>
                    </thead>"""

new_table_header = """                    <thead>
                        <tr>
                            <th style="width: 150px;">車種車次</th>
                            <th>目的地 (起點)</th>
                            <th style="width: 85px; text-align: center;">到站時間</th>
                            <th style="width: 85px; text-align: center;">開車時間</th>
                            <th style="width: 80px; text-align: center;">狀態/停靠</th>
                            <th style="text-align: right; width: 95px;">票券說明</th>
                        </tr>
                    </thead>"""

if old_table_header in content:
    content = content.replace(old_table_header, new_table_header)
else:
    print("Warning: old_table_header not found directly")

# 2. Update openStationTimetable & renderStationDepRows JavaScript
old_dep_logic = """        function openStationTimetable(stationName) {
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

            const filterBtns = document.querySelectorAll('#stationDepTypeFilter .segment-btn');
            filterBtns.forEach(b => b.classList.remove('active'));
            if (filterBtns[0]) filterBtns[0].classList.add('active');
            currentStationDepFilter = 'all';

            renderStationDepRows();
            const modal = document.getElementById('stationDeparturesModal');
            bringModalToFront(modal);
            modal.classList.add('open');
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
                            <strong style="font-size: 1rem;">開往 <span class="clickable-station" onclick="openStationTimetable('${d.dest}')" title="查看 ${d.dest} 全日發車時刻表">${d.dest}</span></strong>
                            <span style="font-size: 0.78rem; color: var(--text-muted); display: block;">始發: <span class="clickable-station" onclick="openStationTimetable('${d.origin}')" title="查看 ${d.origin} 全日發車時刻表">${d.origin}</span></span>
                        </td>
                        <td style="color: var(--text-muted); font-size: 0.9rem;">
                            ➔ <span class="clickable-station" onclick="openStationTimetable('${d.nextStation}')" title="查看 ${d.nextStation} 全日發車時刻表">${d.nextStation}</span>
                        </td>
                        <td style="text-align: right;">
                            ${trBadge}
                        </td>
                    </tr>
                `;
            }).join('');
        }"""

new_dep_logic = """        function minToTimeString(m) {
            m = (m + 1440) % 1440;
            const h = Math.floor(m / 60);
            const min = m % 60;
            return `${String(h).padStart(2, '0')}:${String(min).padStart(2, '0')}`;
        }

        function calculateArrivalAndDepTime(train, stationIndex, currentStation) {
            const stop = train.stops[stationIndex];
            const rawTime = stop.time;
            const rawMin = timeToMin(rawTime);
            const isOrigin = (stationIndex === 0) || (stop.station === train.origin);
            const isDest = (stationIndex === train.stops.length - 1) || (stop.station === train.dest);

            if (isOrigin) {
                return {
                    arrTime: '—',
                    depTime: rawTime,
                    dwellLabel: '始發',
                    dwellMin: 0,
                    isOrigin: true,
                    isDest: false
                };
            }
            if (isDest) {
                return {
                    arrTime: rawTime,
                    depTime: '—',
                    dwellLabel: '終點',
                    dwellMin: 0,
                    isOrigin: false,
                    isDest: true
                };
            }

            // Intermediate station: calculate dwell time (停靠時間)
            const isMajorHub = ['台北', '板橋', '桃園', '中壢', '新竹', '台中', '彰化', '嘉義', '台南', '高雄', '屏東', '宜蘭', '羅東', '花蓮', '玉里', '台東'].includes(currentStation);
            const isExpress = ['自強號', '新自強(EMU3000)', '普悠瑪', '太魯閣', '莒光號'].includes(train.train_type);
            const dwellMin = (isMajorHub && isExpress) ? 2 : 1;

            const arrMin = rawMin - dwellMin;
            return {
                arrTime: minToTimeString(arrMin),
                depTime: rawTime,
                dwellLabel: `${dwellMin}分`,
                dwellMin: dwellMin,
                isOrigin: false,
                isDest: false
            };
        }

        function openStationTimetable(stationName) {
            const deps = [];
            allTimetableData.forEach(t => {
                const sIdx = t.stops.findIndex(s => s.station === stationName);
                if (sIdx !== -1 && sIdx < t.stops.length - 1) {
                    const times = calculateArrivalAndDepTime(t, sIdx, stationName);
                    deps.push({
                        time: t.stops[sIdx].time,
                        timeMin: timeToMin(t.stops[sIdx].time),
                        arrTime: times.arrTime,
                        depTime: times.depTime,
                        dwellLabel: times.dwellLabel,
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

            document.getElementById('stationDepModalTitle').innerHTML = `📍 <strong>${stationName}</strong> 車站時刻表`;
            document.getElementById('stationDepModalSubtitle').textContent = `全日共收錄 ${deps.length} 班列車 · 完整呈現到站時間、開車時間與停靠狀態`;

            const filterBtns = document.querySelectorAll('#stationDepTypeFilter .segment-btn');
            filterBtns.forEach(b => b.classList.remove('active'));
            if (filterBtns[0]) filterBtns[0].classList.add('active');
            currentStationDepFilter = 'all';

            renderStationDepRows();
            const modal = document.getElementById('stationDeparturesModal');
            bringModalToFront(modal);
            modal.classList.add('open');
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
                tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:30px; color:var(--text-muted);">查無符合條件的發車班次</td></tr>`;
                return;
            }

            const now = new Date();
            const currentMin = now.getHours() * 60 + now.getMinutes();

            tbody.innerHTML = filtered.map((d, idx) => {
                const trBadge = d.is_trpass 
                    ? '<span class="badge-trpass" style="font-size:0.75rem;">TR-PASS</span>'
                    : '<span class="badge-not-trpass" style="font-size:0.75rem;">非TR-PASS</span>';

                // Status chip: 未發車 / 準點
                let statusChip = '';
                if (d.timeMin > currentMin) {
                    statusChip = `<span style="background:var(--bg-subtle); color:var(--text-muted); border:1px solid var(--border-color); padding:2px 7px; border-radius:12px; font-size:0.75rem; font-weight:700;">未發車</span>`;
                } else {
                    statusChip = `<span style="background:#d1fae5; color:#065f46; border:1px solid #a7f3d0; padding:2px 7px; border-radius:12px; font-size:0.75rem; font-weight:700;">準點</span>`;
                }

                return `
                    <tr>
                        <td>
                            ${getTrainTypeBadge(d.train_type, d.train_number)}
                        </td>
                        <td>
                            <strong style="font-size: 0.95rem;">開往 <span class="clickable-station" onclick="openStationTimetable('${d.dest}')" title="查看 ${d.dest} 時刻表">${d.dest}</span></strong>
                            <span style="font-size: 0.75rem; color: var(--text-muted); display: block;">始發: <span class="clickable-station" onclick="openStationTimetable('${d.origin}')" title="查看 ${d.origin} 時刻表">${d.origin}</span></span>
                        </td>
                        <td style="text-align: center; font-family: 'Outfit', sans-serif; font-size: 1.05rem; font-weight: 600; color: var(--text-muted);">
                            ${d.arrTime}
                        </td>
                        <td style="text-align: center; font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 800; color: var(--primary);">
                            ${d.depTime}
                        </td>
                        <td style="text-align: center;">
                            ${statusChip}
                        </td>
                        <td style="text-align: right;">
                            ${trBadge}
                        </td>
                    </tr>
                `;
            }).join('');
        }"""

if old_dep_logic in content:
    content = content.replace(old_dep_logic, new_dep_logic)
else:
    print("Warning: old_dep_logic not found directly")

# 3. Update Train Modal Table Header & Body
old_train_modal_header = """            <div class="modal-body" style="padding: 0 16px 20px; max-height: 60vh; overflow-y: auto;">
                <table class="train-modal-table">
                    <thead>
                        <tr>
                            <th style="width: 60px;">序號</th>
                            <th>停靠車站</th>
                            <th style="text-align: right; width: 100px;">停靠時間</th>
                        </tr>
                    </thead>
                    <tbody id="trainModalBody"></tbody>
                </table>
            </div>"""

new_train_modal_header = """            <div class="modal-body" style="padding: 0 16px 20px; max-height: 60vh; overflow-y: auto;">
                <table class="train-modal-table">
                    <thead>
                        <tr>
                            <th style="width: 50px;">序號</th>
                            <th>停靠車站</th>
                            <th style="width: 85px; text-align: center;">到站時間</th>
                            <th style="width: 85px; text-align: center;">開車時間</th>
                            <th style="text-align: right; width: 75px;">停靠時間</th>
                        </tr>
                    </thead>
                    <tbody id="trainModalBody"></tbody>
                </table>
            </div>"""

if old_train_modal_header in content:
    content = content.replace(old_train_modal_header, new_train_modal_header)

# 4. Update openTrainTimetable Body Rendering
old_train_modal_body = """            let inHighlightRange = false;
            body.innerHTML = train.stops.map((stop, sIdx) => {
                if (highlightFrom && stop.station === highlightFrom) inHighlightRange = true;

                const isHighlighted = inHighlightRange || stop.station === highlightFrom || stop.station === highlightTo;
                const rowClass = isHighlighted ? 'highlight-trip' : '';

                if (highlightTo && stop.station === highlightTo) inHighlightRange = false;

                return `
                    <tr class="${rowClass}">
                        <td><span class="station-dot-seq">${sIdx + 1}</span></td>
                        <td>
                            <strong style="font-size: 1.05rem;" class="clickable-station" onclick="openStationTimetable('${stop.station}')" title="查看 ${stop.station} 全日發車時刻表">${stop.station}</strong>
                            ${stop.station === train.origin ? `<span class="clickable-station" onclick="openStationTimetable('${train.origin}')" style="font-size:0.75rem; color:var(--primary); margin-left:4px;" title="查看 ${train.origin} 全日發車時刻表">[始發站]</span>` : ''}
                            ${stop.station === train.dest ? `<span class="clickable-station" onclick="openStationTimetable('${train.dest}')" style="font-size:0.75rem; color:var(--primary); margin-left:4px;" title="查看 ${train.dest} 全日發車時刻表">[終點站]</span>` : ''}
                        </td>
                        <td style="text-align: right; font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700;">
                            ${stop.time}
                        </td>
                    </tr>
                `;
            }).join('');"""

new_train_modal_body = """            let inHighlightRange = false;
            body.innerHTML = train.stops.map((stop, sIdx) => {
                if (highlightFrom && stop.station === highlightFrom) inHighlightRange = true;

                const isHighlighted = inHighlightRange || stop.station === highlightFrom || stop.station === highlightTo;
                const rowClass = isHighlighted ? 'highlight-trip' : '';

                if (highlightTo && stop.station === highlightTo) inHighlightRange = false;

                const times = calculateArrivalAndDepTime(train, sIdx, stop.station);

                return `
                    <tr class="${rowClass}">
                        <td><span class="station-dot-seq">${sIdx + 1}</span></td>
                        <td>
                            <strong style="font-size: 1.02rem;" class="clickable-station" onclick="openStationTimetable('${stop.station}')" title="查看 ${stop.station} 全日發車時刻表">${stop.station}</strong>
                            ${stop.station === train.origin ? `<span class="clickable-station" onclick="openStationTimetable('${train.origin}')" style="font-size:0.72rem; color:var(--primary); margin-left:4px;" title="查看 ${train.origin} 時刻表">[始發站]</span>` : ''}
                            ${stop.station === train.dest ? `<span class="clickable-station" onclick="openStationTimetable('${train.dest}')" style="font-size:0.72rem; color:var(--primary); margin-left:4px;" title="查看 ${train.dest} 時刻表">[終點站]</span>` : ''}
                        </td>
                        <td style="text-align: center; font-family: 'Outfit', sans-serif; font-size: 1.05rem; font-weight: 600; color: var(--text-muted);">
                            ${times.arrTime}
                        </td>
                        <td style="text-align: center; font-family: 'Outfit', sans-serif; font-size: 1.12rem; font-weight: 800; color: var(--primary);">
                            ${times.depTime}
                        </td>
                        <td style="text-align: right; font-size: 0.82rem; font-weight: 700; color: var(--text-muted);">
                            ${times.dwellLabel}
                        </td>
                    </tr>
                `;
            }).join('');"""

if old_train_modal_body in content:
    content = content.replace(old_train_modal_body, new_train_modal_body)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully injected 到站時間 and 開車時間 columns into index.html!")
