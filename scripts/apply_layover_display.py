import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Update transferTagHtml in renderResults
old_transfer_code = """                const isDirect = route.transfers === 0;
                const transferTagHtml = isDirect 
                    ? `<span class="transfer-tag transfer-direct">🟢 直達無須換車</span>`
                    : `<span class="transfer-tag transfer-hop">🟠 轉乘 ${route.transfers} 次 (${route.transfer_stations.join('、')})</span>`;"""

new_transfer_code = """                const isDirect = route.transfers === 0;
                
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
                    : `<span class="transfer-tag transfer-hop">🟠 轉乘 ${route.transfers} 次 (${transferStationsWithLayovers})</span>`;"""

html = html.replace(old_transfer_code, new_transfer_code, 1)

# Bump version to v3.3.0 (SemVer Minor: Direct Layover Duration Display on Summary Cards)
html = html.replace('v3.2.0 (2026.07.01版)', 'v3.3.0 (2026.07.01版)')
html = html.replace('核心版本: v3.2.0', '核心版本: v3.3.0 (轉乘站名直接外露精確等候時間 · 緊湊轉乘高亮)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated to v3.3.0 with direct layover duration display on summary cards!")
