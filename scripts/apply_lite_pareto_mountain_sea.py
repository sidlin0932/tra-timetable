# -*- coding: utf-8 -*-
import re

print("Applying updates to lite.html...")

with open('lite.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add .badge-line-dir CSS styles to lite.html
line_dir_css = """
        .badge-line-dir {
            display: inline-flex;
            align-items: center;
            padding: 1px 5px;
            font-size: 0.72rem;
            font-weight: 800;
            border-radius: 5px;
            margin-left: 4px;
            vertical-align: middle;
        }
        .badge-line-dir.mt {
            background: #ecfdf5;
            color: #047857;
            border: 1px solid #a7f3d0;
        }
        .badge-line-dir.sea {
            background: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
        }
        .badge-line-dir.cz {
            background: #fef3c7;
            color: #b45309;
            border: 1px solid #fde68a;
        }
"""

if '.badge-line-dir' not in html:
    html = html.replace('.badge-local-fast { background: #d1fae5; color: #059669; border: 1px solid rgba(5,150,105,0.35); }',
                        '.badge-local-fast { background: #d1fae5; color: #059669; border: 1px solid rgba(5,150,105,0.35); }\n' + line_dir_css)

# 2. Update getTrainBadge in lite.html
old_get_badge = """        function getTrainBadge(type, no) {
            let cls = 'badge-local';
            if (type.includes('EMU3000')) cls = 'badge-emu3000';
            else if (type.includes('普悠瑪')) cls = 'badge-puyuma';
            else if (type.includes('太魯閣')) cls = 'badge-taroko';
            else if (type.includes('自強')) cls = 'badge-tzu-chiang';
            else if (type.includes('莒光')) cls = 'badge-chu-kuang';
            else if (type.includes('區間快')) cls = 'badge-local-fast';
            return `<span class=\"badge ${cls}\" style=\"cursor:pointer;\" onclick=\"event.stopPropagation(); showTrainDetail('${no}')\" title=\"點擊查看 ${no} 次完整停靠時刻表\">${type} ${no}次 🔍</span>`;
        }"""

new_get_badge = """        function getTrainBadge(type, no, customRouteDir) {
            let cls = 'badge-local';
            if (type.includes('EMU3000')) cls = 'badge-emu3000';
            else if (type.includes('普悠瑪')) cls = 'badge-puyuma';
            else if (type.includes('太魯閣')) cls = 'badge-taroko';
            else if (type.includes('自強')) cls = 'badge-tzu-chiang';
            else if (type.includes('莒光')) cls = 'badge-chu-kuang';
            else if (type.includes('區間快')) cls = 'badge-local-fast';

            let dir = customRouteDir;
            if (!dir && typeof timetableData !== 'undefined') {
                const tr = timetableData.find(t => String(t.train_number) === String(no));
                if (tr) dir = tr.route_dir;
            }

            let dirBadge = '';
            if (dir === '山線') {
                dirBadge = `<span class="badge-line-dir mt">⛰️山線</span>`;
            } else if (dir === '海線') {
                dirBadge = `<span class="badge-line-dir sea">🌊海線</span>`;
            } else if (dir === '成追線') {
                dirBadge = `<span class="badge-line-dir cz">🔄成追</span>`;
            }

            return `<span class=\"badge ${cls}\" style=\"cursor:pointer;\" onclick=\"event.stopPropagation(); showTrainDetail('${no}')\" title=\"點擊查看 ${no} 次完整停靠時刻表\">${type} ${no}次 ${dirBadge} 🔍</span>`;
        }"""

html = html.replace(old_get_badge, new_get_badge)

# 3. Update Pareto Pruning in planLeg
old_plan_leg_pareto = """            // Pruning 3: Pareto Dominance Filtering (Keep only Pareto-optimal routes)
            const optimal = [];
            for (let i = 0; i < routes.length; i++) {
                const r1 = routes[i];
                let isDominated = false;
                for (let j = 0; j < routes.length; j++) {
                    if (i === j) continue;
                    const r2 = routes[j];
                    // If r2 departs later/same, arrives earlier/same, and has fewer/same transfers -> r1 is useless
                    if (r2.depMin >= r1.depMin && r2.arrMin <= r1.arrMin && r2.transfers <= r1.transfers) {
                        if (r2.depMin > r1.depMin || r2.arrMin < r1.arrMin || r2.transfers < r1.transfers) {
                            isDominated = true;
                            break;
                        }
                    }
                }
                if (!isDominated) optimal.push(r1);
            }

            return optimal;"""

new_plan_leg_pareto = """            // Pruning 3: Strict Pareto Dominance & Slower Elimination (去慢保優)
            const optimal = [];
            for (let i = 0; i < routes.length; i++) {
                const r1 = routes[i];
                let isDominated = false;
                const trainSeq1 = (r1.legs || []).map(l => String(l.trainNo || l.train_number)).join('-');

                for (let j = 0; j < routes.length; j++) {
                    if (i === j) continue;
                    const r2 = routes[j];
                    const trainSeq2 = (r2.legs || []).map(l => String(l.trainNo || l.train_number)).join('-');

                    if (r2.depMin >= r1.depMin && r2.arrMin <= r1.arrMin) {
                        // Case A: r2 leaves later and arrives same/earlier -> r1 took longer total time (strictly slower)
                        if (r2.depMin > r1.depMin && r2.arrMin <= r1.arrMin) {
                            isDominated = true;
                            break;
                        }
                        // Case B: r2 leaves same time and arrives earlier -> r1 slower
                        if (r2.depMin === r1.depMin && r2.arrMin < r1.arrMin) {
                            isDominated = true;
                            break;
                        }
                        // Case C: r2 leaves same time and arrives same time
                        if (r2.depMin === r1.depMin && r2.arrMin === r1.arrMin) {
                            if (r2.transfers < r1.transfers) {
                                isDominated = true;
                                break;
                            } else if (r2.transfers === r1.transfers && trainSeq1 === trainSeq2) {
                                isDominated = true;
                                break;
                            }
                        }
                    }
                }
                if (!isDominated) optimal.push(r1);
            }

            return optimal;"""

html = html.replace(old_plan_leg_pareto, new_plan_leg_pareto)

# 4. In showTrainDetail of lite.html, show mountain/sea route
old_show_detail_meta = """            document.getElementById('liteModalTrainMeta').innerHTML = `
                <span>車種: <strong>${train.train_type}</strong> (${train.train_model || 'EMU'})</span>
                <span>路線: <strong>${train.line || '台鐵本線'}</strong></span>
                ${trBadge}
            `;"""

new_show_detail_meta = """            let lineWithDir = train.line || '台鐵本線';
            if (train.route_dir === '山線') {
                lineWithDir += ' <span class="badge-line-dir mt">⛰️ 經山線(台中線)</span>';
            } else if (train.route_dir === '海線') {
                lineWithDir += ' <span class="badge-line-dir sea">🌊 經海線(海岸線)</span>';
            } else if (train.route_dir === '成追線') {
                lineWithDir += ' <span class="badge-line-dir cz">🔄 經成追線(山海環線)</span>';
            }

            document.getElementById('liteModalTrainMeta').innerHTML = `
                <span>車種: <strong>${train.train_type}</strong> (${train.train_model || 'EMU'})</span>
                <span>路線: <strong>${lineWithDir}</strong></span>
                ${trBadge}
            `;"""

html = html.replace(old_show_detail_meta, new_show_detail_meta)

with open('lite.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("lite.html updated successfully!")
