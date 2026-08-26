import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add CSS for Train Timetable Modal and clickable badges
train_modal_css = """
        .train-badge.clickable {
            cursor: pointer;
            transition: all 0.2s;
        }
        .train-badge.clickable:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            filter: brightness(1.1);
        }

        .train-modal-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
            margin-top: 12px;
        }
        .train-modal-table th {
            background: var(--bg-subtle);
            color: var(--text-muted);
            font-weight: 700;
            padding: 10px 16px;
            text-align: left;
            border-bottom: 2px solid var(--border-color);
        }
        .train-modal-table td {
            padding: 10px 16px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-main);
        }
        .train-modal-table tr:hover {
            background: var(--bg-subtle);
        }
        .train-modal-table tr.highlight-trip {
            background: var(--primary-light);
            font-weight: 700;
        }
        [data-theme="dark"] .train-modal-table tr.highlight-trip {
            background: rgba(2, 132, 199, 0.2);
        }
        .station-dot-seq {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            background: var(--bg-subtle);
            border: 1px solid var(--border-color);
            font-size: 0.75rem;
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            margin-right: 8px;
        }
        .highlight-trip .station-dot-seq {
            background: var(--primary);
            color: #ffffff;
            border-color: var(--primary);
        }
"""

css_insertion_point = "</style>"
html = html.replace(css_insertion_point, train_modal_css + "\n    </style>", 1)

# 2. Add Train Timetable Modal HTML before the script tags
train_modal_html = """
    <!-- Train Full Timetable Modal -->
    <div class="modal-backdrop" id="trainTimetableModal" onclick="closeTrainModal(event)">
        <div class="modal-dialog" style="max-width: 600px;" onclick="event.stopPropagation()">
            <div class="modal-header">
                <div>
                    <h3 id="trainModalTitle" style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                        🚆 列車時刻表
                    </h3>
                    <p id="trainModalSubtitle" style="font-size: 0.85rem; color: var(--text-muted); margin-top: 4px;"></p>
                </div>
                <button class="btn-modal-close" onclick="closeTrainModal()">&times;</button>
            </div>
            
            <div class="modal-body" style="padding: 0 16px 20px;">
                <table class="train-modal-table">
                    <thead>
                        <tr>
                            <th style="width: 70px;"># 序號</th>
                            <th>停靠站名</th>
                            <th style="text-align: right; width: 120px;">停靠時間</th>
                        </tr>
                    </thead>
                    <tbody id="trainModalBody"></tbody>
                </table>
            </div>
        </div>
    </div>
"""

modal_insertion_point = "<!-- County-classified Station Modal -->"
html = html.replace(modal_insertion_point, train_modal_html + "\n    " + modal_insertion_point, 1)

# 3. Update getTrainTypeBadge to be clickable and add openTrainTimetable JS function
old_badge_func = """function getTrainTypeBadge(type, number) {
            let badgeClass = 'badge-local';
            if (type.includes('新自強') || type.includes('3000')) badgeClass = 'badge-3000';
            else if (type.includes('自強') || type.includes('普悠瑪') || type.includes('太魯閣')) badgeClass = 'badge-express';
            else if (type.includes('莒光')) badgeClass = 'badge-chu';
            else if (type.includes('快')) badgeClass = 'badge-fastlocal';

            return `<span class="train-badge ${badgeClass}">${type} ${number}</span>`;
        }"""

new_badge_func = """function getTrainTypeBadge(type, number, fromSt, toSt) {
            let badgeClass = 'badge-local';
            if (type.includes('新自強') || type.includes('3000')) badgeClass = 'badge-3000';
            else if (type.includes('自強') || type.includes('普悠瑪') || type.includes('太魯閣')) badgeClass = 'badge-express';
            else if (type.includes('莒光')) badgeClass = 'badge-chu';
            else if (type.includes('快')) badgeClass = 'badge-fastlocal';

            const fromArg = fromSt ? `'${fromSt}'` : "''";
            const toArg = toSt ? `'${toSt}'` : "''";

            return `<span class="train-badge clickable ${badgeClass}" onclick="event.stopPropagation(); openTrainTimetable('${number}', ${fromArg}, ${toArg})" title="點擊查看 ${type} ${number} 次全線停靠時刻表">${type} ${number} 🔍</span>`;
        }

        function openTrainTimetable(trainNumber, highlightFrom, highlightTo) {
            const train = allTimetableData.find(t => t.train_number === trainNumber);
            if (!train) {
                alert('查無該列車時刻表');
                return;
            }

            const modal = document.getElementById('trainTimetableModal');
            const title = document.getElementById('trainModalTitle');
            const subtitle = document.getElementById('trainModalSubtitle');
            const body = document.getElementById('trainModalBody');

            title.innerHTML = `
                ${getTrainTypeBadge(train.train_type, train.train_number)}
                <span>${train.origin} ➔ ${train.dest}</span>
            `;

            const trBadge = train.is_trpass 
                ? '<span class="badge-trpass" style="margin-left:6px;">✅ TR-PASS 適用</span>' 
                : '<span class="badge-not-trpass" style="margin-left:6px;">⚠️ 不適用TR-PASS</span>';

            subtitle.innerHTML = `
                <span>車種車型: <strong>${train.train_model || train.train_type}</strong> · 路線: <strong>${train.line || '台鐵本線'}</strong></span>
                ${trBadge}
            `;

            let inHighlightRange = false;
            body.innerHTML = train.stops.map((stop, sIdx) => {
                if (highlightFrom && stop.station === highlightFrom) inHighlightRange = true;

                const isHighlighted = inHighlightRange || stop.station === highlightFrom || stop.station === highlightTo;
                const rowClass = isHighlighted ? 'highlight-trip' : '';

                if (highlightTo && stop.station === highlightTo) inHighlightRange = false;

                return `
                    <tr class="${rowClass}">
                        <td><span class="station-dot-seq">${sIdx + 1}</span></td>
                        <td>
                            <strong style="font-size: 1.05rem;">${stop.station}</strong>
                            ${stop.station === train.origin ? '<span style="font-size:0.75rem; color:var(--primary); margin-left:4px;">[始發站]</span>' : ''}
                            ${stop.station === train.dest ? '<span style="font-size:0.75rem; color:var(--primary); margin-left:4px;">[終點站]</span>' : ''}
                        </td>
                        <td style="text-align: right; font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700;">
                            ${stop.time}
                        </td>
                    </tr>
                `;
            }).join('');

            modal.classList.add('open');
        }

        function closeTrainModal(e) {
            if (!e || e.target.id === 'trainTimetableModal' || e.target.classList.contains('btn-modal-close')) {
                document.getElementById('trainTimetableModal').classList.remove('open');
            }
        }
"""

html = html.replace(old_badge_func, new_badge_func, 1)

# 4. Update badge calls in itinerary loop to pass leg.from and leg.to
html = html.replace("getTrainTypeBadge(l.train_type, l.train_number)", "getTrainTypeBadge(l.train_type, l.train_number, l.from, l.to)")
html = html.replace("getTrainTypeBadge(leg.train_type, leg.train_number)", "getTrainTypeBadge(leg.train_type, leg.train_number, leg.from, leg.to)")

# 5. Bump version to v2.6.0
html = html.replace('v2.5.0 (2026.07.01版)', 'v2.6.0 (2026.07.01版)')
html = html.replace('核心版本: v2.5.0', '核心版本: v2.6.0 (支援列車全線時刻表彈窗)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Applied Train Timetable Modal Feature and updated index.html to v2.6.0!")
