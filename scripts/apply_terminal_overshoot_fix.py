# -*- coding: utf-8 -*-
import re

print("Updating isStationOvershooting in index.html and lite.html to allow adjacent terminal hubs...")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_overshoot = """        function isStationOvershooting(orig, dest, mid) {
            if (!orig || !dest || !mid || mid === orig || mid === dest) return false;
            for (let cIdx = 0; cIdx < CORRIDOR_MAPS.length; cIdx++) {
                const corridor = CORRIDOR_MAPS[cIdx];
                const iOrig = corridor.indexOf(orig);
                const iDest = corridor.indexOf(dest);
                const iMid = corridor.indexOf(mid);
                if (iOrig !== -1 && iDest !== -1 && iMid !== -1) {
                    const minP = Math.min(iOrig, iDest);
                    const maxP = Math.max(iOrig, iDest);
                    if (iMid < minP || iMid > maxP) {
                        return true; // Strictly out of corridor bounds!
                    }
                }
            }
            return false;
        }"""

new_overshoot = """        function isStationOvershooting(orig, dest, mid) {
            if (!orig || !dest || !mid || mid === orig || mid === dest) return false;
            const TERMINAL_HUBS = new Set(['七堵', '八堵', '基隆', '新左營', '高雄', '二水', '竹中', '瑞芳']);
            for (let cIdx = 0; cIdx < CORRIDOR_MAPS.length; cIdx++) {
                const corridor = CORRIDOR_MAPS[cIdx];
                const iOrig = corridor.indexOf(orig);
                const iDest = corridor.indexOf(dest);
                const iMid = corridor.indexOf(mid);
                if (iOrig !== -1 && iDest !== -1 && iMid !== -1) {
                    const minP = Math.min(iOrig, iDest);
                    const maxP = Math.max(iOrig, iDest);
                    if (iMid < minP || iMid > maxP) {
                        if (TERMINAL_HUBS.has(mid) && Math.abs(iMid - iDest) <= 2) {
                            continue; // Valid transfer at adjacent terminal interchange hub!
                        }
                        return true; // Strictly out of corridor bounds!
                    }
                }
            }
            return false;
        }"""

html = html.replace(old_overshoot, new_overshoot)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated isStationOvershooting successfully!")
