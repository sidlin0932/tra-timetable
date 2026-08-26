import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add CSS for Plan B and Tight transfers
css_target = ".layover-alert {"
css_replacement = """.badge-tight-transfer {
            background: #fef3c7;
            color: #d97706;
            border: 1px solid #fde68a;
            font-size: 0.75rem;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        [data-theme="dark"] .badge-tight-transfer {
            background: rgba(217, 119, 6, 0.2);
            border-color: rgba(217, 119, 6, 0.4);
            color: #fbbf24;
        }
        .plan-b-card {
            background: #eff6ff;
            border: 1.5px solid #bfdbfe;
            border-radius: 8px;
            padding: 10px 14px;
            margin: 8px 0 12px;
            font-size: 0.85rem;
            color: #1e40af;
        }
        [data-theme="dark"] .plan-b-card {
            background: rgba(30, 58, 138, 0.25);
            border-color: rgba(59, 130, 246, 0.4);
            color: #93c5fd;
        }
        .plan-b-title {
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 4px;
        }
        .layover-alert.tight {
            background: #fff1f2;
            border-color: #fecdd3;
            color: #e11d48;
        }
        [data-theme="dark"] .layover-alert.tight {
            background: rgba(225, 29, 72, 0.2);
            border-color: rgba(225, 29, 72, 0.4);
            color: #fda4af;
        }

        .layover-alert {"""

html = html.replace(css_target, css_replacement, 1)

# 2. Add findBackupLeg and update renderResults in JS
js_render_target = "function renderResults() {"
js_render_replacement = """function findBackupLeg(fromStation, toStation, currentDepTime) {
            const depMin = timeToMin(currentDepTime);
            const candidates = [];
            allTimetableData.forEach(t => {
                const fromStop = t.stops.find(s => s.station === fromStation);
                const toStop = t.stops.find(s => s.station === toStation);
                if (fromStop && toStop) {
                    const fIdx = t.stops.indexOf(fromStop);
                    const tIdx = t.stops.indexOf(toStop);
                    if (fIdx < tIdx) {
                        const tDep = timeToMin(fromStop.time);
                        if (tDep > depMin) {
                            candidates.push({
                                train_number: t.train_number,
                                train_type: t.train_type,
                                dep: fromStop.time,
                                arr: toStop.time,
                                depMin: tDep,
                                delayMin: tDep - depMin
                            });
                        }
                    }
                }
            });
            candidates.sort((a, b) => a.depMin - b.depMin);
            return candidates[0] || null;
        }

        function renderResults() {"""

html = html.replace(js_render_target, js_render_replacement, 1)

# 3. Update the render itinerary loop with Plan B card
old_itinerary_block_start = "const itineraryHtml = route.legs.map((leg, legIdx) => {"
old_itinerary_block_end = "return `\n                    <div class=\"trip-card\">"

new_itinerary_block = """const hasTightTransfer = route.legs.some(l => l.layover > 0 && l.layover <= 15);
                const tightTransferBadge = hasTightTransfer 
                    ? `<span class="badge-tight-transfer">⚡ 含緊湊轉乘 · 附備案</span>`
                    : '';

                const itineraryHtml = route.legs.map((leg, legIdx) => {
                    let layoverAlert = '';
                    let planBHtml = '';

                    if (leg.layover) {
                        const isTight = leg.layover <= 15;
                        const alertClass = isTight ? 'layover-alert tight' : 'layover-alert';
                        const tightNotice = isTight ? ' <span style="color:#ef4444; font-weight:800;">(⚠️ 緊湊轉乘)</span>' : '';
                        layoverAlert = `<div class="${alertClass}">⏳ 在 <strong>${leg.from}</strong> 站轉乘，停留等候 <strong>${leg.layover} 分鐘</strong>${tightNotice}</div>`;

                        const backup = findBackupLeg(leg.from, leg.to, leg.dep);
                        if (backup) {
                            planBHtml = `
                                <div class="plan-b-card">
                                    <div class="plan-b-title">
                                        <span>🛡️ 萬一轉乘不及之【第二備案】：</span>
                                    </div>
                                    <div>
                                        下一班可搭乘 <strong>${backup.train_type} ${backup.train_number}</strong> (${leg.from} ${backup.dep} ➔ ${leg.to} ${backup.arr})，預估延後 <strong>${backup.delayMin} 分鐘</strong>抵達。
                                    </div>
                                </div>
                            `;
                        }
                    }

                    const stopsChips = leg.all_stops.map(s => 
                        `<span class="stop-chip">${s.station} (${s.time})</span>`
                    ).join('');

                    return `
                        <div class="timeline-step">
                            <div class="timeline-dot ${legIdx > 0 ? 'transfer' : ''}"></div>
                            ${layoverAlert}
                            ${planBHtml}
                            <div class="leg-card">
                                <div class="leg-header">
                                    <div class="leg-route">
                                        第 ${legIdx + 1} 段：${leg.from} (${leg.dep}) ➔ ${leg.to} (${leg.arr})
                                    </div>
                                    <div>
                                        ${getTrainTypeBadge(leg.train_type, leg.train_number)}
                                        <span style="font-size:0.8rem; color:var(--text-muted); margin-left:6px;">(${leg.origin} 開往 ${leg.dest})</span>
                                    </div>
                                </div>
                                <div style="font-size:0.82rem; color:var(--text-muted); margin-top:6px;">
                                    沿途停靠 (${leg.all_stops.length} 站)：
                                </div>
                                <div class="all-stops-list">
                                    ${stopsChips}
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');

                return `
                    <div class="trip-card">
                        <div class="trip-header-row" onclick="toggleDetails(${rIdx})">
                            <div class="train-types-badges">
                                ${legsBadges}
                                ${trPassBadge}
                                ${tightTransferBadge}
                            </div>"""

start_pos = html.find(old_itinerary_block_start)
end_pos = html.find(old_itinerary_block_end)

if start_pos != -1 and end_pos != -1:
    end_of_header_row = html.find('<div class="train-types-badges">', end_pos)
    end_of_badges = html.find('</div>', end_of_header_row) + 6
    html = html[:start_pos] + new_itinerary_block + html[end_of_badges:]

# 4. Bump version to v2.5.0
html = html.replace('v2.4.0 (2026.07.01版)', 'v2.5.0 (2026.07.01版)')
html = html.replace('核心版本: v2.4.0', '核心版本: v2.5.0 (含轉乘失敗第二備案)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Applied Plan B Backup Feature and updated index.html to v2.5.0!")
