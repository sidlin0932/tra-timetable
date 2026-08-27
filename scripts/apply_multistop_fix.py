# -*- coding: utf-8 -*-
import re

print("Patching index.html with planMultiStopRoutes, multi-transfer expansion, and cleaning executeSearch...")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update bestAtStation in planRoutes to allow up to 3 distinct arrivals per hub
old_best_at_station = """                                    } else if (hop < maxAllowedHops) {
                                        if (!bestAtStation[nextSt] || arrMin < bestAtStation[nextSt]) {
                                            bestAtStation[nextSt] = arrMin;
                                            const nextVis = new Set(state.visited);
                                            nextVis.add(nextSt);
                                            nextQueue.push({
                                                currentStation: nextSt,
                                                currentTimeMin: arrMin,
                                                legs: newLegs,
                                                visited: nextVis
                                            });
                                        }
                                    }"""

new_best_at_station = """                                    } else if (hop < maxAllowedHops) {
                                        if (!bestAtStation[nextSt]) bestAtStation[nextSt] = [];
                                        if (bestAtStation[nextSt].length < 3 || arrMin < bestAtStation[nextSt][bestAtStation[nextSt].length - 1]) {
                                            bestAtStation[nextSt].push(arrMin);
                                            bestAtStation[nextSt].sort((a, b) => a - b);
                                            if (bestAtStation[nextSt].length > 3) bestAtStation[nextSt].pop();
                                            const nextVis = new Set(state.visited);
                                            nextVis.add(nextSt);
                                            nextQueue.push({
                                                currentStation: nextSt,
                                                currentTimeMin: arrMin,
                                                legs: newLegs,
                                                visited: nextVis
                                            });
                                        }
                                    }"""

html = html.replace(old_best_at_station, new_best_at_station)

# 2. Add planMultiStopRoutes function
multi_stop_func = """
        function planMultiStopRoutes(wps, startTimeMin) {
            if (!wps || wps.length < 2) return [];
            if (wps.length === 2) {
                return planRoutes(wps[0].station, wps[1].station, startTimeMin);
            }

            // Segment 1 (A -> B)
            let candidateChains = planRoutes(wps[0].station, wps[1].station, startTimeMin).slice(0, 25);

            for (let seg = 1; seg < wps.length - 1; seg++) {
                const segOrig = wps[seg].station;
                const segDest = wps[seg + 1].station;
                const minStay = parseInt(wps[seg].minStay || 0, 10);
                const nextChains = [];

                for (let cIdx = 0; cIdx < candidateChains.length; cIdx++) {
                    const chain = candidateChains[cIdx];
                    const arrMin = timeToMin(chain.arr_time);
                    const earliestDep = arrMin + minStay;
                    const nextLegRoutes = planRoutes(segOrig, segDest, earliestDep).slice(0, 5);

                    for (let nIdx = 0; nIdx < nextLegRoutes.length; nIdx++) {
                        const nRoute = nextLegRoutes[nIdx];
                        const depMin = timeToMin(nRoute.dep_time);
                        const stayActual = depMin - arrMin;
                        if (stayActual < minStay) continue;

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
        window.planMultiStopRoutes = planMultiStopRoutes;
"""

if 'function planMultiStopRoutes' not in html:
    html = html.replace('window.pruneDominatedRoutes = pruneDominatedRoutes;',
                        'window.pruneDominatedRoutes = pruneDominatedRoutes;\n' + multi_stop_func)

# 3. Remove the duplicate second executeSearch function
duplicate_execute_search = """        function executeSearch() {
            const timeStr = document.getElementById('timeInput') ? (document.getElementById('timeInput').value || '00:00') : '00:00';
            const startTimeMin = timeToMin(timeStr);
            const via = document.getElementById('viaInput') ? document.getElementById('viaInput').value.trim() : '';

            const routeStr = waypoints.map(w => w.station).join(' ➔ ');
            const summaryEl = document.getElementById('routeSummaryText');
            if (summaryEl) {
                if (waypoints.length === 2 && via) {
                    summaryEl.textContent = `${waypoints[0].station} ➔ [經由 ${via}] ➔ ${waypoints[1].station}`;
                } else {
                    summaryEl.textContent = routeStr;
                }
            }
            updateClearViaButton();

            const orig = waypoints[0].station;
            const dest = waypoints[waypoints.length - 1].station;

            if (!orig || !dest || orig === dest || allTimetableData.length === 0) {
                currentRoutes = [];
                renderResults();
                return;
            }

            let rawRoutes = [];
            if (waypoints.length === 2) {
                rawRoutes = planRoutes(orig, dest, startTimeMin, via);
            } else {
                rawRoutes = planMultiStopRoutes(waypoints, startTimeMin);
            }

            const seen = new Set();
            currentRoutes = rawRoutes.filter(r => {
                const key = `${r.dep_time}-${r.arr_time}-${r.transfers}-${r.legs.map(l=>l.train_number).join('_')}`;
                if (seen.has(key)) return false;
                seen.add(key);
                return true;
            });

            currentRoutes = sortRoutes(currentRoutes);
            renderResults();
        }"""

html = html.replace(duplicate_execute_search, "")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html patched successfully!")
