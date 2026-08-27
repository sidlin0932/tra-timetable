# -*- coding: utf-8 -*-
import json
import re

print("Adding planMultiStopRoutes into index.html and lite.html...")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

multi_stop_func = """
        // ==========================================
        // Multi-Stop Waypoint Routing Chaining Engine
        // ==========================================
        function planMultiStopRoutes(waypointList, startMin) {
            if (!waypointList || waypointList.length < 2) return [];
            
            const orig0 = waypointList[0].station;
            const dest0 = waypointList[1].station;
            if (!orig0 || !dest0) return [];
            
            const stay0 = parseInt(waypointList[1].minStay, 10) || 0;
            let currentChains = planRoutes(orig0, dest0, startMin, '').slice(0, 25).map(r => ({
                legs: [...r.legs],
                dep_time: r.dep_time,
                arr_time: r.arr_time,
                endMin: timeToMin(r.arr_time) + stay0
            }));
            
            for (let wIdx = 1; wIdx < waypointList.length - 1; wIdx++) {
                const segOrig = waypointList[wIdx].station;
                const segDest = waypointList[wIdx + 1].station;
                const stayMin = parseInt(waypointList[wIdx + 1].minStay, 10) || 0;
                const nextChains = [];
                
                for (const chain of currentChains) {
                    const segRoutes = planRoutes(segOrig, segDest, chain.endMin, '').slice(0, 8);
                    for (const sr of segRoutes) {
                        const newLegs = [...chain.legs, ...sr.legs];
                        const arrM = timeToMin(sr.arr_time);
                        nextChains.push({
                            legs: newLegs,
                            dep_time: chain.dep_time,
                            arr_time: sr.arr_time,
                            endMin: arrM + stayMin
                        });
                    }
                }
                currentChains = nextChains;
                if (currentChains.length === 0) break;
            }
            
            return currentChains.map(c => {
                const depM = timeToMin(c.dep_time);
                const arrM = timeToMin(c.arr_time);
                const dur = (arrM >= depM) ? (arrM - depM) : (arrM + 1440 - depM);
                return {
                    transfers: c.legs.length - 1,
                    dep_time: c.dep_time,
                    arr_time: c.arr_time,
                    duration: dur,
                    is_trpass: c.legs.every(l => l.is_trpass),
                    train_types: c.legs.map(l => l.train_type),
                    transfer_stations: c.legs.slice(0, -1).map(l => l.to),
                    legs: c.legs
                };
            });
        }
        window.planMultiStopRoutes = planMultiStopRoutes;
"""

if 'function planMultiStopRoutes' not in html:
    html = html.replace('function showRealProgressBar', multi_stop_func + '\n        function showRealProgressBar')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("planMultiStopRoutes successfully integrated!")
