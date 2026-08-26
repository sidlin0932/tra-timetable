import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Expand KEY_HUBS to include all Western Trunk Line junction hubs
old_hubs = """        const KEY_HUBS = new Set([
            '新竹', '北新竹', '竹中', '樹林', '板橋', '台北', '松山', '南港',
            '七堵', '八堵', '瑞芳', '宜蘭', '羅東', '花蓮', '二水', '彰化',
            '台中', '嘉義', '台南', '中洲', '新左營', '高雄', '屏東', '潮州', '枋寮', '台東'
        ]);"""

new_hubs = """        const KEY_HUBS = new Set([
            '新竹', '北新竹', '竹中', '樹林', '板橋', '台北', '松山', '南港',
            '七堵', '八堵', '瑞芳', '宜蘭', '羅東', '花蓮', '竹南', '苗栗', '豐原',
            '台中', '彰化', '員林', '二水', '斗六', '大林', '嘉義', '新營', '善化',
            '台南', '中洲', '新左營', '高雄', '屏東', '潮州', '枋寮', '台東'
        ]);"""

html = html.replace(old_hubs, new_hubs, 1)

# 2. Refine Dominance filter in planRoutes so that Local/Commuter itineraries are preserved
# and not eliminated by direct Express trains
old_dom = """            // Smart Transit Quality & Dominance Filter:
            // Discard redundant 3-hop/4-hop detours if a cleaner route exists
            const cleanResults = [];
            allResults.sort((a, b) => a.transfers - b.transfers || a.duration - b.duration);

            for (const r of allResults) {
                const arrM = timeToMin(r.arr_time);
                const depM = timeToMin(r.dep_time);
                const isDominated = cleanResults.some(cr => {
                    const cArr = timeToMin(cr.arr_time);
                    const cDep = timeToMin(cr.dep_time);
                    if (cDep >= depM && cArr <= arrM + 5 && cr.transfers < r.transfers) {
                        return true;
                    }
                    return false;
                });
                if (!isDominated) {
                    cleanResults.push(r);
                }
            }

            return cleanResults;"""

new_dom = """            // Smart Transit Quality & Dominance Filter:
            // Discard redundant detours, but preserve pure commuter (Local) chains alongside Express
            const cleanResults = [];
            allResults.sort((a, b) => a.transfers - b.transfers || a.duration - b.duration);

            for (const r of allResults) {
                const arrM = timeToMin(r.arr_time);
                const depM = timeToMin(r.dep_time);
                const isAllLocal = r.legs.every(l => ['區間車', '區間快'].includes(l.train_type));

                const isDominated = cleanResults.some(cr => {
                    const cArr = timeToMin(cr.arr_time);
                    const cDep = timeToMin(cr.dep_time);
                    const crAllLocal = cr.legs.every(l => ['區間車', '區間快'].includes(l.train_type));

                    // Only express dominates express, or local dominates local with fewer transfers
                    if (isAllLocal && !crAllLocal) {
                        return false; // Do not let express kill all-local commuter chains!
                    }

                    if (cDep >= depM && cArr <= arrM + 5 && cr.transfers < r.transfers) {
                        return true;
                    }
                    return false;
                });
                if (!isDominated) {
                    cleanResults.push(r);
                }
            }

            return cleanResults;"""

html = html.replace(old_dom, new_dom, 1)

# 3. Bump version to v3.1.0 (Minor feature release: Western Line Multi-Segment Commuter Stitching & Dual Hierarchy Preservation)
html = html.replace('v3.0.3 (2026.07.01版)', 'v3.1.0 (2026.07.01版)')
html = html.replace('核心版本: v3.0.3', '核心版本: v3.1.0 (全台西部幹線區間車多段智慧縫合 · 直達特快與全區間接駁雙軌並存)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Enhanced Commuter Multi-hop Stitching and bumped version to v3.1.0!")
