import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Update renderResults in index.html to add rich leg running times, total pure moving time, and layover breakdown
old_render_trip_card = """                const transferStationsWithLayovers = route.legs.slice(0, -1).map((leg, idx) => {
                    const nextLeg = route.legs[idx + 1];
                    const layoverM = (nextLeg && nextLeg.layover) ? nextLeg.layover : 0;
                    const isTight = layoverM > 0 && layoverM <= 15;
                    const layoverStr = layoverM > 0 
                        ? (isTight ? ` · <strong style="color:#e11d48;">⚡等 ${layoverM}分</strong>` : ` · 等 ${layoverM}分`)
                        : '';
                    return `${leg.to}${layoverStr}`;
                }).join('、');

                const transferTagHtml = isDirect 
                    ? `<span class="transfer-tag transfer-direct">🟢 直達無須換車</span>`
                    : `<span class="transfer-tag transfer-hop">🟠 轉乘 ${route.transfers} 次 (${transferStationsWithLayovers})</span>`;"""

new_render_trip_card = """                const totalLayoverMin = route.legs.reduce((sum, l) => sum + (l.layover || 0), 0);
                const pureMovingMin = route.duration - totalLayoverMin;

                const transferStationsWithLayovers = route.legs.slice(0, -1).map((leg, idx) => {
                    const nextLeg = route.legs[idx + 1];
                    const layoverM = (nextLeg && nextLeg.layover) ? nextLeg.layover : 0;
                    const isTight = layoverM > 0 && layoverM <= 15;
                    const layoverStr = layoverM > 0 
                        ? (isTight ? ` · <strong style="color:#e11d48;">⚡等 ${layoverM}分</strong>` : ` · 等 ${layoverM}分`)
                        : '';
                    return `${leg.to}${layoverStr}`;
                }).join('、');

                const transferTagHtml = isDirect 
                    ? `<span class="transfer-tag transfer-direct">🟢 直達無須換車</span>`
                    : `<span class="transfer-tag transfer-hop">🟠 轉乘 ${route.transfers} 次 (${transferStationsWithLayovers})</span>
                       <div style="font-size:0.75rem; color:var(--text-muted); margin-top:2px;">純車行 ${minToDuration(pureMovingMin)} · 總等車 ${totalLayoverMin}分</div>`;

                const legsBadgesWithDuration = route.legs.map(l => {
                    const legDurationMin = timeToMin(l.arr) - timeToMin(l.dep);
                    const durStr = legDurationMin > 0 ? `<span style="font-size:0.75rem; opacity:0.85; margin-left:3px;">(${legDurationMin}分)</span>` : '';
                    return `<span style="display:inline-flex; align-items:center;">${getTrainTypeBadge(l.train_type, l.train_number, l.from, l.to)}${durStr}</span>`;
                }).join(' <span style="color:var(--text-muted); font-size:0.8rem; font-weight:700; margin:0 2px;">➔</span> ');"""

html = html.replace(old_render_trip_card, new_render_trip_card, 1)
html = html.replace('${legsBadges}\n                                ${trPassBadge}', '${legsBadgesWithDuration}\n                                ${trPassBadge}')

# Bump version to v3.4.0 (SemVer Minor: Multi-dimensional Transit Analytics on Summary Cards)
html = html.replace('v3.3.0 (2026.07.01版)', 'v3.4.0 (2026.07.01版)')
html = html.replace('核心版本: v3.3.0', '核心版本: v3.4.0 (全方位乘車數據外露 · 車程/等候時間/每段行駛分鐘一目了然)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated to v3.4.0 with rich transit analytics on summary cards!")
