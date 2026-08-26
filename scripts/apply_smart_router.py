import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace planRoutes with the smart router
old_func_start = html.find('function planRoutes(orig, dest, startTimeMin) {')
old_func_end = html.find('function sortRoutes(routes) {')

new_func = """function planRoutes(orig, dest, startTimeMin) {
            if (!orig || !dest || orig === dest || allTimetableData.length === 0) {
                return [];
            }

            let maxAllowedTransfers = 4;
            if (transferCondition === 'direct') maxAllowedTransfers = 0;
            else if (transferCondition === 'max1') maxAllowedTransfers = 1;
            else if (transferCondition === 'max2') maxAllowedTransfers = 2;
            else if (transferCondition === 'all') maxAllowedTransfers = 4;

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
                    } else if (maxAllowedTransfers > 0 && (KEY_HUBS.has(nextSt) || j === train1.stops.length - 1)) {
                        queue.push({
                            currentStation: nextSt,
                            currentTimeMin: arrMin,
                            legs: [leg1],
                            visited: new Set([orig, nextSt])
                        });
                    }
                }

                const bestAtStationForThisDep = {};

                for (let hop = 1; hop <= maxAllowedTransfers; hop++) {
                    const nextQueue = [];
                    for (const state of queue) {
                        const deps = departuresByStation[state.currentStation] || [];
                        const minDep = state.currentTimeMin + 3;

                        for (const d of deps) {
                            if (d.depTimeMin < minDep) continue;
                            if (d.depTimeMin > minDep + 90) continue;
                            if (!isTrainAllowed(d.train)) continue;
                            if (d.train.train_number === state.legs[state.legs.length - 1].train_number) continue;

                            const train = d.train;
                            for (let j = d.stopIdx + 1; j < train.stops.length; j++) {
                                const nextSt = train.stops[j].station;
                                const arrMin = timeToMin(train.stops[j].time);
                                if (arrMin <= d.depTimeMin) continue;
                                if (state.visited.has(nextSt)) continue;

                                if (nextSt !== dest && !KEY_HUBS.has(nextSt) && j !== train.stops.length - 1) continue;

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
                                    if (!bestAtStationForThisDep[nextSt] || arrMin < bestAtStationForThisDep[nextSt]) {
                                        bestAtStationForThisDep[nextSt] = arrMin;
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

            // Smart Transit Quality & Dominance Filter:
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

            return cleanResults;
        }

        """

html = html[:old_func_start] + new_func + html[old_func_end:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Applied smart routing & dominance filter to index.html!")
