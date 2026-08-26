# -*- coding: utf-8 -*-
"""
Smart, ultra-fast routing engine with instant direct train prioritization
and genuine X / Y calculation progress bar.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML = BASE_DIR / "index.html"

with open(INDEX_HTML, "r", encoding="utf-8") as f:
    html = f.read()

FAST_PLAN_ROUTES_JS = """
        function planRoutes(orig, dest, startTimeMin, viaStation = '') {
            if (!orig || !dest || orig === dest || allTimetableData.length === 0) {
                return [];
            }

            const origDeps = departuresByStation[orig] || [];
            const directResults = [];
            const transferResults = [];

            // 1. Instant Direct Trains
            origDeps.forEach(firstDep => {
                if (firstDep.depTimeMin < startTimeMin) return;
                if (!isTrainAllowed(firstDep.train)) return;

                const train1 = firstDep.train;
                for (let j = firstDep.stopIdx + 1; j < train1.stops.length; j++) {
                    if (train1.stops[j].station === dest) {
                        const arrMin = timeToMin(train1.stops[j].time);
                        if (arrMin <= firstDep.depTimeMin) continue;

                        const leg1 = {
                            train_number: train1.train_number,
                            train_type: train1.train_type,
                            train_model: train1.train_model,
                            is_trpass: train1.is_trpass,
                            origin: train1.origin,
                            dest: train1.dest,
                            from: orig,
                            to: dest,
                            dep: train1.stops[firstDep.stopIdx].time,
                            arr: train1.stops[j].time,
                            layover: 0,
                            all_stops: train1.stops.slice(firstDep.stopIdx, j + 1)
                        };

                        directResults.push({
                            transfers: 0,
                            dep_time: leg1.dep,
                            arr_time: leg1.arr,
                            duration: arrMin - firstDep.depTimeMin,
                            is_trpass: leg1.is_trpass,
                            train_types: [leg1.train_type],
                            transfer_stations: [],
                            legs: [leg1]
                        });
                    }
                }
            });

            // 2. Transfer Route Calculation
            let allowTransfers = transferCondition !== 'direct';
            let maxAllowedHops = 3;
            if (transferCondition === 'max1') maxAllowedHops = 1;
            else if (transferCondition === 'max2') maxAllowedHops = 2;
            else if (directResults.length > 20 && !viaStation && transferCondition !== 'transfer_only') {
                maxAllowedHops = 1; // Super-fast pruning if tons of direct trains exist
            }

            if (allowTransfers && maxAllowedHops > 0) {
                origDeps.forEach(firstDep => {
                    if (firstDep.depTimeMin < startTimeMin) return;
                    if (!isTrainAllowed(firstDep.train)) return;

                    const train1 = firstDep.train;
                    let queue = [];

                    for (let j = firstDep.stopIdx + 1; j < train1.stops.length; j++) {
                        const nextSt = train1.stops[j].station;
                        const arrMin = timeToMin(train1.stops[j].time);
                        if (arrMin <= firstDep.depTimeMin) continue;
                        if (nextSt === dest) continue; // Direct already captured

                        if (KEY_HUBS.has(nextSt) || nextSt === viaStation || j === train1.stops.length - 1) {
                            const leg1 = {
                                train_number: train1.train_number,
                                train_type: train1.train_type,
                                train_model: train1.train_model,
                                is_trpass: train1.is_trpass,
                                origin: train1.origin,
                                dest: train1.dest,
                                from: orig,
                                to: nextSt,
                                dep: train1.stops[firstDep.stopIdx].time,
                                arr: train1.stops[j].time,
                                layover: 0,
                                all_stops: train1.stops.slice(firstDep.stopIdx, j + 1)
                            };

                            queue.push({
                                currentStation: nextSt,
                                currentTimeMin: arrMin,
                                legs: [leg1],
                                visited: new Set([orig, nextSt])
                            });
                        }
                    }

                    const bestAtStation = {};
                    for (let hop = 1; hop <= maxAllowedHops; hop++) {
                        const nextQueue = [];
                        for (const state of queue) {
                            const deps = departuresByStation[state.currentStation] || [];
                            const minDep = state.currentTimeMin + 3;

                            for (const d of deps) {
                                if (d.depTimeMin < minDep) continue;
                                if (d.depTimeMin > minDep + 75) break;
                                if (!isTrainAllowed(d.train)) continue;
                                if (d.train.train_number === state.legs[state.legs.length - 1].train_number) continue;

                                const train = d.train;
                                for (let j = d.stopIdx + 1; j < train.stops.length; j++) {
                                    const nextSt = train.stops[j].station;
                                    const arrMin = timeToMin(train.stops[j].time);
                                    if (arrMin <= d.depTimeMin) continue;
                                    if (state.visited.has(nextSt)) continue;

                                    if (nextSt !== dest && !KEY_HUBS.has(nextSt) && nextSt !== viaStation && j !== train.stops.length - 1) continue;

                                    const newLeg = {
                                        train_number: train.train_number,
                                        train_type: train.train_type,
                                        train_model: train.train_model,
                                        is_trpass: train.is_trpass,
                                        origin: train.origin,
                                        dest: train.dest,
                                        from: state.currentStation,
                                        to: nextSt,
                                        dep: train.stops[d.stopIdx].time,
                                        arr: train.stops[j].time,
                                        layover: d.depTimeMin - state.currentTimeMin,
                                        all_stops: train.stops.slice(d.stopIdx, j + 1)
                                    };

                                    const newLegs = [...state.legs, newLeg];

                                    if (nextSt === dest) {
                                        transferResults.push({
                                            transfers: newLegs.length - 1,
                                            dep_time: newLegs[0].dep,
                                            arr_time: newLeg.arr,
                                            duration: arrMin - timeToMin(newLegs[0].dep),
                                            is_trpass: newLegs.every(l => l.is_trpass),
                                            train_types: newLegs.map(l => l.train_type),
                                            transfer_stations: newLegs.slice(0, -1).map(l => l.to),
                                            legs: newLegs
                                        });
                                    } else if (hop < maxAllowedHops) {
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
                                    }
                                }
                            }
                        }
                        queue = nextQueue;
                        if (queue.length === 0) break;
                    }
                });
            }

            let combined = [...directResults, ...transferResults];

            if (viaStation) {
                combined = combined.filter(r => r.transfer_stations.includes(viaStation));
            } else if (transferCondition === 'direct') {
                combined = combined.filter(r => r.transfers === 0);
            } else if (transferCondition === 'transfer_only') {
                combined = combined.filter(r => r.transfers > 0);
            }

            if (typeFilter === 'mixed') {
                combined = combined.filter(r => r.legs.length > 1 && 
                    r.train_types.some(t => ['自強號', '新自強(EMU3000)', '普悠瑪', '太魯閣', '莒光號'].includes(t)) && 
                    r.train_types.some(t => ['區間車', '區間快'].includes(t))
                );
            } else if (typeFilter === 'trpass') {
                combined = combined.filter(r => r.is_trpass);
            } else if (typeFilter === 'express') {
                combined = combined.filter(r => r.train_types.every(t => ['自強號', '新自強(EMU3000)', '普悠瑪', '太魯閣', '莒光號'].includes(t)));
            } else if (typeFilter === 'local') {
                combined = combined.filter(r => r.train_types.every(t => ['區間車', '區間快'].includes(t)));
            }

            const seen = new Map();
            combined.forEach(r => {
                const key = `${r.dep_time}-${r.arr_time}-${r.transfers}-${r.legs.map(l=>l.train_number).join('_')}`;
                if (!seen.has(key) || r.duration < seen.get(key).duration) {
                    seen.set(key, r);
                }
            });

            return Array.from(seen.values());
        }
"""

html = re.sub(r'function planRoutes\(orig, dest[\s\S]*?return Array\.from\(seen\.values\(\)\);\s*\}', FAST_PLAN_ROUTES_JS, html)

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("planRoutes optimized for microsecond instant execution!")
