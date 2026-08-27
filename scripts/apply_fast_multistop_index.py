# -*- coding: utf-8 -*-

print("Updating index.html with fast planMultiStopRoutes and maxAllowedHops = 2 default...")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

fast_multi_stop = """        function planMultiStopRoutes(wps, startTimeMin) {
            if (!wps || wps.length < 2) return [];
            if (wps.length === 2) {
                return planRoutes(wps[0].station, wps[1].station, startTimeMin);
            }

            // Segment 1 (A -> B)
            let candidateChains = planRoutes(wps[0].station, wps[1].station, startTimeMin).slice(0, 20);
            if (candidateChains.length === 0) return [];

            for (let seg = 1; seg < wps.length - 1; seg++) {
                const segOrig = wps[seg].station;
                const segDest = wps[seg + 1].station;
                const minStay = parseInt(wps[seg].minStay || 0, 10);
                
                const minArrMin = Math.min(...candidateChains.map(c => timeToMin(c.arr_time)));
                const allSegRoutes = planRoutes(segOrig, segDest, minArrMin + minStay);
                if (allSegRoutes.length === 0) return [];

                const nextChains = [];
                for (let cIdx = 0; cIdx < candidateChains.length; cIdx++) {
                    const chain = candidateChains[cIdx];
                    const arrMin = timeToMin(chain.arr_time);
                    const earliestDep = arrMin + minStay;
                    
                    const viableNext = allSegRoutes.filter(r => timeToMin(r.dep_time) >= earliestDep).slice(0, 3);
                    for (let nIdx = 0; nIdx < viableNext.length; nIdx++) {
                        const nRoute = viableNext[nIdx];
                        const depMin = timeToMin(nRoute.dep_time);
                        const stayActual = depMin - arrMin;

                        const newLegs = [
                            ...chain.legs,
                            ...nRoute.legs.map((l, lIdx) => lIdx === 0 ? { ...l, stayBefore: stayActual, layover: stayActual } : l)
                        ];

                        const totalDuration = timeToMin(nRoute.arr_time) - timeToMin(chain.dep_time);

                        nextChains.push({
                            transfers: chain.transfers + nRoute.transfers + 1,
                            dep_time: chain.dep_time,
                            arr_time: nRoute.arr_time,
                            duration: totalDuration,
                            is_trpass: chain.is_trpass && nRoute.is_trpass,
                            train_types: newLegs.map(l => l.train_type),
                            transfer_stations: newLegs.slice(0, -1).map(l => l.to),
                            stopovers: [
                                ...(chain.stopovers || []),
                                { station: segOrig, stayMin: stayActual, is_through: false }
                            ],
                            legs: newLegs
                        });
                    }
                }
                candidateChains = nextChains;
                if (candidateChains.length === 0) break;
            }

            return candidateChains;
        }
        window.planMultiStopRoutes = planMultiStopRoutes;"""

# Replace planMultiStopRoutes
import re
html = re.sub(r'function planMultiStopRoutes\(wps, startTimeMin\)\s*\{[\s\S]*?window\.planMultiStopRoutes = planMultiStopRoutes;', fast_multi_stop, html)

# Replace maxAllowedHops = 3 with maxAllowedHops = 2 in planRoutes
html = html.replace('let maxAllowedHops = 3;', 'let maxAllowedHops = 2;')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html successfully updated with fast planMultiStopRoutes!")
