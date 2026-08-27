# -*- coding: utf-8 -*-
import re

print("Applying updates to index.html...")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add .badge-line-dir CSS styles
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
            letter-spacing: 0.2px;
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
        [data-theme="dark"] .badge-line-dir.mt {
            background: rgba(16, 185, 129, 0.25);
            color: #6ee7b7;
            border-color: #059669;
        }
        [data-theme="dark"] .badge-line-dir.sea {
            background: rgba(37, 99, 235, 0.25);
            color: #93c5fd;
            border-color: #2563eb;
        }
        [data-theme="dark"] .badge-line-dir.cz {
            background: rgba(217, 119, 6, 0.25);
            color: #fde68a;
            border-color: #d97706;
        }
"""

if '.badge-line-dir' not in html:
    html = html.replace('.badge-local { background: var(--badge-local-bg); color: var(--badge-local); border: 1px solid rgba(37, 99, 235, 0.35); }',
                        '.badge-local { background: var(--badge-local-bg); color: var(--badge-local); border: 1px solid rgba(37, 99, 235, 0.35); }\n' + line_dir_css)

# 2. Update getTrainTypeBadge to include Mountain/Sea Line capsule
old_get_badge = """        function getTrainTypeBadge(type, number, fromSt, toSt) {
            let badgeClass = 'badge-local';
            if (type.includes('新自強') || type.includes('3000')) badgeClass = 'badge-3000';
            else if (type.includes('普悠瑪')) badgeClass = 'badge-puyuma';
            else if (type.includes('太魯閣')) badgeClass = 'badge-taroko';
            else if (type.includes('自強')) badgeClass = 'badge-express';
            else if (type.includes('莒光')) badgeClass = 'badge-chu';
            else if (type.includes('快')) badgeClass = 'badge-fastlocal';

            const fromArg = fromSt ? `'${fromSt}'` : "''";
            const toArg = toSt ? `'${toSt}'` : "''";

            return `<span class="train-badge clickable ${badgeClass}" onclick="event.stopPropagation(); openTrainTimetable('${number}', ${fromArg}, ${toArg})" title="點擊查看 ${type} ${number} 次全線停靠時刻表">${type} ${number} 🔍</span>`;
        }"""

new_get_badge = """        function getTrainTypeBadge(type, number, fromSt, toSt, customRouteDir) {
            let badgeClass = 'badge-local';
            if (type.includes('新自強') || type.includes('3000')) badgeClass = 'badge-3000';
            else if (type.includes('普悠瑪')) badgeClass = 'badge-puyuma';
            else if (type.includes('太魯閣')) badgeClass = 'badge-taroko';
            else if (type.includes('自強')) badgeClass = 'badge-express';
            else if (type.includes('莒光')) badgeClass = 'badge-chu';
            else if (type.includes('快')) badgeClass = 'badge-fastlocal';

            const fromArg = fromSt ? `'${fromSt}'` : "''";
            const toArg = toSt ? `'${toSt}'` : "''";

            let dir = customRouteDir;
            if (!dir && typeof allTimetableData !== 'undefined') {
                const tr = allTimetableData.find(t => String(t.train_number) === String(number));
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

            return `<span class="train-badge clickable ${badgeClass}" onclick="event.stopPropagation(); openTrainTimetable('${number}', ${fromArg}, ${toArg})" title="點擊查看 ${type} ${number} 次全線停靠時刻表">${type} ${number} ${dirBadge} 🔍</span>`;
        }"""

html = html.replace(old_get_badge, new_get_badge)

# 3. Update pruneDominatedRoutes with strict Pareto "去慢保優" and distinct middle-leg support
old_prune = """        function pruneDominatedRoutes(routes) {
            if (!routes || routes.length === 0) return [];

            function parseMin(t) {
                if (!t) return 0;
                const parts = String(t).split(':').map(Number);
                return (parts[0] || 0) * 60 + (parts[1] || 0);
            }

            function getNormalizedArr(dMin, aMin) {
                if (aMin < dMin) return aMin + 1440;
                return aMin;
            }

            // 1. All Direct Scheduled Trains are 100% Preserved (Never pruned!)
            const directRoutes = [];
            const directTrainNos = new Set();
            for (let r of routes) {
                if (r.transfers === 0) {
                    directRoutes.push(r);
                    if (r.legs && r.legs[0]) {
                        directTrainNos.add(String(r.legs[0].train_number || r.legs[0].trainNo));
                    }
                }
            }

            // 2. Transfer routes: eliminate fake/overshoot transfers
            const validTransferRoutes = routes.filter(r => {
                if (r.transfers > 0 && r.legs && r.legs.length > 1) {
                    const lastTrainNo = String(r.legs[r.legs.length - 1].train_number || r.legs[r.legs.length - 1].trainNo);
                    if (directTrainNos.has(lastTrainNo)) {
                        return false;
                    }
                    return true;
                }
                return false;
            });

            // 3. Prune transfer routes that are dominated by direct trains
            const nonDominatedTransfers = [];
            for (let i = 0; i < validTransferRoutes.length; i++) {
                const r1 = validTransferRoutes[i];
                const dep1 = parseMin(r1.dep_time || r1.depTime || (r1.legs && r1.legs[0] ? r1.legs[0].dep : '00:00'));
                const rawArr1 = parseMin(r1.arr_time || r1.arrTime || (r1.legs && r1.legs[r1.legs.length - 1] ? r1.legs[r1.legs.length - 1].arr : '00:00'));
                const arr1 = getNormalizedArr(dep1, rawArr1);

                let dominated = false;
                for (let j = 0; j < directRoutes.length; j++) {
                    const dRoute = directRoutes[j];
                    const depD = parseMin(dRoute.dep_time || (dRoute.legs && dRoute.legs[0] ? dRoute.legs[0].dep : '00:00'));
                    const rawArrD = parseMin(dRoute.arr_time || (dRoute.legs && dRoute.legs[0] ? dRoute.legs[0].arr : '00:00'));
                    const arrD = getNormalizedArr(depD, rawArrD);

                    // If a direct train departs at the same time or later AND arrives earlier or same -> transfer is dominated
                    if (depD >= dep1 && arrD <= arr1) {
                        dominated = true;
                        break;
                    }
                }
                if (!dominated) {
                    nonDominatedTransfers.push(r1);
                }
            }

            return [...directRoutes, ...nonDominatedTransfers];
        }"""

new_prune = """        function pruneDominatedRoutes(routes) {
            if (!routes || routes.length === 0) return [];

            function parseMin(t) {
                if (!t) return 0;
                const parts = String(t).split(':').map(Number);
                return (parts[0] || 0) * 60 + (parts[1] || 0);
            }

            function getNormalizedArr(dMin, aMin) {
                if (aMin < dMin) return aMin + 1440;
                return aMin;
            }

            // 1. All Direct Scheduled Trains are 100% Preserved (Never pruned!)
            const directRoutes = [];
            const directTrainNos = new Set();
            for (let r of routes) {
                if (r.transfers === 0) {
                    directRoutes.push(r);
                    if (r.legs && r.legs[0]) {
                        directTrainNos.add(String(r.legs[0].train_number || r.legs[0].trainNo));
                    }
                }
            }

            // 2. Transfer routes: eliminate fake/overshoot transfers
            const validTransferRoutes = routes.filter(r => {
                if (r.transfers > 0 && r.legs && r.legs.length > 1) {
                    const lastTrainNo = String(r.legs[r.legs.length - 1].train_number || r.legs[r.legs.length - 1].trainNo);
                    if (directTrainNos.has(lastTrainNo)) {
                        return false;
                    }
                    return true;
                }
                return false;
            });

            // 3. Strict Pareto Dominance & Slower Elimination (去慢保優)
            const allCandidates = [...directRoutes, ...validTransferRoutes];
            const nonDominatedTransfers = [];

            for (let i = 0; i < validTransferRoutes.length; i++) {
                const r1 = validTransferRoutes[i];
                const dep1 = parseMin(r1.dep_time || (r1.legs && r1.legs[0] ? r1.legs[0].dep : '00:00'));
                const rawArr1 = parseMin(r1.arr_time || (r1.legs && r1.legs[r1.legs.length - 1] ? r1.legs[r1.legs.length - 1].arr : '00:00'));
                const arr1 = getNormalizedArr(dep1, rawArr1);
                const tx1 = r1.transfers;
                const trainSeq1 = (r1.legs || []).map(l => String(l.train_number || l.trainNo)).join('-');

                let dominated = false;
                for (let j = 0; j < allCandidates.length; j++) {
                    const r2 = allCandidates[j];
                    if (r1 === r2) continue;

                    const dep2 = parseMin(r2.dep_time || (r2.legs && r2.legs[0] ? r2.legs[0].dep : '00:00'));
                    const rawArr2 = parseMin(r2.arr_time || (r2.legs && r2.legs[r2.legs.length - 1] ? r2.legs[r2.legs.length - 1].arr : '00:00'));
                    const arr2 = getNormalizedArr(dep2, rawArr2);
                    const tx2 = r2.transfers;
                    const trainSeq2 = (r2.legs || []).map(l => String(l.train_number || l.trainNo)).join('-');

                    // If r2 departs at the same time or later, and arrives at the same time or earlier:
                    if (dep2 >= dep1 && arr2 <= arr1) {
                        // Case A: r2 leaves later and arrives same/earlier -> r1 took longer from origin to destination (strictly slower)
                        if (dep2 > dep1 && arr2 <= arr1) {
                            dominated = true;
                            break;
                        }
                        // Case B: r2 leaves same time and arrives earlier -> r1 strictly slower
                        if (dep2 === dep1 && arr2 < arr1) {
                            dominated = true;
                            break;
                        }
                        // Case C: r2 leaves same time and arrives exact same time
                        if (dep2 === dep1 && arr2 === arr1) {
                            if (tx2 < tx1) {
                                dominated = true;
                                break;
                            } else if (tx2 === tx1 && trainSeq1 === trainSeq2) {
                                dominated = true;
                                break;
                            }
                            // If same dep, same arr, same tx, but DIFFERENT middle legs (trainSeq1 !== trainSeq2):
                            // Both distinct options are preserved so users can pick alternative trains!
                        }
                    }
                }
                if (!dominated) {
                    nonDominatedTransfers.push(r1);
                }
            }

            return [...directRoutes, ...nonDominatedTransfers];
        }"""

# Handle potential whitespace differences in old_prune replacement
html = re.sub(r'function pruneDominatedRoutes\(routes\)\s*\{[\s\S]*?return \[\.\.\.directRoutes, \.\.\.nonDominatedTransfers\];\s*\}', new_prune.strip(), html)

# 4. Update station modal timetable rendering to include Mountain / Sea Line tags
old_station_dep = """                    <tr>
                        <td>
                            ${getTrainTypeBadge(d.train_type, d.train_number)}
                        </td>"""

new_station_dep = """                    <tr>
                        <td>
                            ${getTrainTypeBadge(d.train_type, d.train_number, '', '', d.route_dir || '')}
                        </td>"""

html = html.replace(old_station_dep, new_station_dep)

# Also in openStationTimetable, store route_dir:
old_open_st_dep = """                        dest: t.dest,
                        is_trpass: t.is_trpass,
                        line: t.line || '',
                        nextStation: t.stops[sIdx + 1].station"""

new_open_st_dep = """                        dest: t.dest,
                        route_dir: t.route_dir || '',
                        is_trpass: t.is_trpass,
                        line: t.line || '',
                        nextStation: t.stops[sIdx + 1].station"""

html = html.replace(old_open_st_dep, new_open_st_dep)

# 5. In openTrainTimetable, show enhanced route description with mountain/sea badge
old_train_subtitle = """            subtitle.innerHTML = `
                <span>車種車型: <strong>${train.train_model || train.train_type}</strong> · 路線: <strong>${train.line || '台鐵本線'}</strong></span>
                ${trBadge}
            `;"""

new_train_subtitle = """            let lineWithDir = train.line || '台鐵本線';
            if (train.route_dir === '山線') {
                lineWithDir += ' <span class="badge-line-dir mt">⛰️ 經山線(台中線)</span>';
            } else if (train.route_dir === '海線') {
                lineWithDir += ' <span class="badge-line-dir sea">🌊 經海線(海岸線)</span>';
            } else if (train.route_dir === '成追線') {
                lineWithDir += ' <span class="badge-line-dir cz">🔄 經成追線(山海環線)</span>';
            }

            subtitle.innerHTML = `
                <span>車種車型: <strong>${train.train_model || train.train_type}</strong> · 路線: <strong>${lineWithDir}</strong></span>
                ${trBadge}
            `;"""

html = html.replace(old_train_subtitle, new_train_subtitle)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated successfully!")
