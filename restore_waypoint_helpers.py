# -*- coding: utf-8 -*-
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML = BASE_DIR / "index.html"

with open(INDEX_HTML, "r", encoding="utf-8") as f:
    html = f.read()

WAYPOINT_HELPERS = """
        function addWaypoint() {
            if (waypoints.length >= 6) {
                alert('最多支援 6 個連續停靠站規劃！');
                return;
            }
            waypoints.splice(waypoints.length - 1, 0, { station: '', minStay: 0 });
            renderWaypointsUI();
            setModalTarget(`waypoint-${waypoints.length - 2}`);
            openStationModal();
        }

        function removeWaypoint(idx) {
            if (waypoints.length <= 2) return;
            waypoints.splice(idx, 1);
            renderWaypointsUI();
            executeSearch();
        }

        function moveWaypoint(idx, dir) {
            const targetIdx = idx + dir;
            if (targetIdx < 0 || targetIdx >= waypoints.length) return;
            const temp = waypoints[idx];
            waypoints[idx] = waypoints[targetIdx];
            waypoints[targetIdx] = temp;
            renderWaypointsUI();
            executeSearch();
        }

        function reverseWaypoints() {
            waypoints.reverse();
            renderWaypointsUI();
            executeSearch();
        }

        function swapStations() {
            reverseWaypoints();
        }

        function quickFillWaypoint(target, st) {
            if (target === 'dest') {
                waypoints[waypoints.length - 1].station = st;
            } else if (typeof target === 'number' && waypoints[target]) {
                waypoints[target].station = st;
            }
            renderWaypointsUI();
            executeSearch();
        }

        // ==========================================
        // Single-Leg & Chained Multi-Leg Routing Core
        // ==========================================
        function getDirectLegTrains(orig, dest, startTimeMin) {
            const origDeps = departuresByStation[orig] || [];
            const results = [];

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

                        results.push({
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

            results.sort((a, b) => timeToMin(a.dep_time) - timeToMin(b.dep_time));
            return results;
        }

        function planRoutes(orig, dest, startTimeMin, viaStation = '') {
            if (!orig || !dest || orig === dest || allTimetableData.length === 0) {
                return [];
            }

            let maxAllowedTransfers = 4;
            if (transferCondition === 'direct') maxAllowedTransfers = 0;
            else if (transferCondition === 'max1') maxAllowedTransfers = 1;
            else if (transferCondition === 'max2') maxAllowedTransfers = 2;
            else if (transferCondition === 'all' || transferCondition === 'transfer_only') maxAllowedTransfers = 4;

            const origDeps = departuresByStation[orig] || [];
            const allResults = [];

            origDeps.forEach(firstDep => {
                if (firstDep.depTimeMin < startTimeMin) return;
                if (!isTrainAllowed(firstDep.train)) return;

                const train1 = firstDep.train;
                let queue = [];

                for (let j = firstDep.stopIdx + 1; j < train1.stops.length; j++) {
                    const nextSt = train1.stops[j].station;
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
                        to: nextSt,
                        dep: train1.stops[firstDep.stopIdx].time,
                        arr: train1.stops[j].time,
                        layover: 0,
                        all_stops: train1.stops.slice(firstDep.stopIdx, j + 1)
                    };

                    if (nextSt === dest) {
                        allResults.push({
                            transfers: 0,
                            dep_time: leg1.dep,
                            arr_time: leg1.arr,
                            duration: arrMin - firstDep.depTimeMin,
                            is_trpass: leg1.is_trpass,
                            train_types: [leg1.train_type],
                            transfer_stations: [],
                            legs: [leg1]
                        });
                    } else if (maxAllowedTransfers > 0 && (KEY_HUBS.has(nextSt) || nextSt === viaStation || j === train1.stops.length - 1)) {
                        queue.push({
                            currentStation: nextSt,
                            currentTimeMin: arrMin,
                            legs: [leg1],
                            visited: new Set([orig, nextSt])
                        });
                    }
                }

                const bestAtStation = {};

                for (let hop = 1; hop <= maxAllowedTransfers; hop++) {
                    const nextQueue = [];
                    for (const state of queue) {
                        const deps = departuresByStation[state.currentStation] || [];
                        const minDep = state.currentTimeMin + 3;

                        for (const d of deps) {
                            if (d.depTimeMin < minDep) continue;
                            if (d.depTimeMin > minDep + 90) break; // Optimized with pre-sorted array!
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
                                    allResults.push({
                                        transfers: newLegs.length - 1,
                                        dep_time: newLegs[0].dep,
                                        arr_time: newLeg.arr,
                                        duration: arrMin - timeToMin(newLegs[0].dep),
                                        is_trpass: newLegs.every(l => l.is_trpass),
                                        train_types: newLegs.map(l => l.train_type),
                                        transfer_stations: newLegs.slice(0, -1).map(l => l.to),
                                        legs: newLegs
                                    });
                                } else if (hop < maxAllowedTransfers) {
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

            let filteredResults = allResults;

            if (viaStation) {
                filteredResults = filteredResults.filter(r => r.transfer_stations.includes(viaStation));
            } else if (transferCondition === 'direct') {
                filteredResults = filteredResults.filter(r => r.transfers === 0);
            } else if (transferCondition === 'transfer_only') {
                filteredResults = filteredResults.filter(r => r.transfers > 0);
            }

            if (typeFilter === 'mixed') {
                filteredResults = filteredResults.filter(r => r.legs.length > 1 && 
                    r.train_types.some(t => ['自強號', '新自強(EMU3000)', '普悠瑪', '太魯閣', '莒光號'].includes(t)) && 
                    r.train_types.some(t => ['區間車', '區間快'].includes(t))
                );
            } else if (typeFilter === 'trpass') {
                filteredResults = filteredResults.filter(r => r.is_trpass);
            } else if (typeFilter === 'express') {
                filteredResults = filteredResults.filter(r => r.train_types.every(t => ['自強號', '新自強(EMU3000)', '普悠瑪', '太魯閣', '莒光號'].includes(t)));
            } else if (typeFilter === 'local') {
                filteredResults = filteredResults.filter(r => r.train_types.every(t => ['區間車', '區間快'].includes(t)));
            }

            const seen = new Map();
            filteredResults.forEach(r => {
                const key = `${r.dep_time}-${r.arr_time}-${r.transfers}-${r.legs.map(l=>l.train_number).join('_')}`;
                if (!seen.has(key) || r.duration < seen.get(key).duration) {
                    seen.set(key, r);
                }
            });

            return Array.from(seen.values());
        }

        function planMultiStopRoutes(wps, startTimeMin) {
            if (!wps || wps.length < 2) return [];
            if (wps.length === 2) {
                const via = document.getElementById('viaInput') ? document.getElementById('viaInput').value.trim() : '';
                return planRoutes(wps[0].station, wps[1].station, startTimeMin, via);
            }

            const directCandidates = [];
            for (let seg = 0; seg < wps.length - 1; seg++) {
                const fSt = wps[seg].station;
                const tSt = wps[seg + 1].station;
                const segTrains = getDirectLegTrains(fSt, tSt, 0);
                if (segTrains.length > 0) {
                    directCandidates.push(segTrains.map(r => r.legs[0]));
                } else {
                    const fallbackRoutes = planRoutes(fSt, tSt, 0, '');
                    if (fallbackRoutes.length > 0) {
                        directCandidates.push(fallbackRoutes[0].legs);
                    } else {
                        return [];
                    }
                }
            }

            let chainCombinations = [[]];
            for (let seg = 0; seg < directCandidates.length; seg++) {
                const legsForSeg = directCandidates[seg];
                const nextChains = [];
                const minStayM = wps[seg + 1] ? (wps[seg + 1].minStay || 0) : 0;

                for (const currentChain of chainCombinations) {
                    const lastLeg = currentChain.length > 0 ? currentChain[currentChain.length - 1] : null;
                    const minDepartureMin = lastLeg 
                        ? timeToMin(lastLeg.arr) + (minStayM === 0 ? 3 : minStayM)
                        : startTimeMin;

                    for (const candidateLeg of legsForSeg) {
                        const depM = timeToMin(candidateLeg.dep);
                        if (depM < minDepartureMin) continue;
                        if (lastLeg && depM > minDepartureMin + 240) continue;

                        let isThrough = false;
                        if (lastLeg && lastLeg.train_number === candidateLeg.train_number && minStayM === 0) {
                            isThrough = true;
                        }

                        const layoverM = lastLeg ? depM - timeToMin(lastLeg.arr) : 0;
                        const legCopy = {
                            ...candidateLeg,
                            layover: layoverM,
                            is_through: isThrough
                        };

                        nextChains.push([...currentChain, legCopy]);
                    }
                }
                chainCombinations = nextChains;
                if (chainCombinations.length === 0) break;
            }

            const multiRoutes = [];
            for (const chain of chainCombinations) {
                if (chain.length !== wps.length - 1) continue;

                let transfersCount = 0;
                for (let i = 0; i < chain.length - 1; i++) {
                    if (!chain[i + 1].is_through) transfersCount++;
                }

                const firstDep = chain[0].dep;
                const lastArr = chain[chain.length - 1].arr;
                const duration = timeToMin(lastArr) - timeToMin(firstDep);
                if (duration <= 0) continue;

                const stopovers = [];
                for (let i = 0; i < chain.length - 1; i++) {
                    const stName = wps[i + 1].station;
                    const stayMin = chain[i + 1].layover;
                    const isThru = chain[i + 1].is_through;
                    stopovers.push({
                        station: stName,
                        stayMin: stayMin,
                        is_through: isThru
                    });
                }

                multiRoutes.push({
                    transfers: transfersCount,
                    dep_time: firstDep,
                    arr_time: lastArr,
                    duration: duration,
                    is_trpass: chain.every(l => l.is_trpass),
                    train_types: chain.map(l => l.train_type),
                    transfer_stations: chain.slice(0, -1).map(l => l.to),
                    legs: chain,
                    stopovers: stopovers
                });
            }

            return multiRoutes;
        }
"""

# Insert WAYPOINT_HELPERS right before High-Speed Router
html = html.replace("// ==========================================\n        // High-Speed Router & Instant UI Engine", WAYPOINT_HELPERS + "\n        // ==========================================\n        // High-Speed Router & Instant UI Engine")

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Waypoint helpers and optimized planRoutes successfully restored!")
