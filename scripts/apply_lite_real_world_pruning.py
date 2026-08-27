# -*- coding: utf-8 -*-
import re

with open('lite.html', 'r', encoding='utf-8') as f:
    lite = f.read()

lite_prune = """        // Fast Train Map Cache for O(1) Pre-leg Lookup
        let cachedTrainMap = null;
        function getTrainMap() {
            if (!cachedTrainMap || cachedTrainMap.size !== allTimetableData.length) {
                cachedTrainMap = new Map();
                allTimetableData.forEach(t => cachedTrainMap.set(t.train_number, t));
            }
            return cachedTrainMap;
        }

        // Pruning: Refined Real-World Pareto Dominance & First-Leg Choice Preservation
        function pruneDominatedRoutes(routes) {
            if (!routes || routes.length <= 1) return routes || [];

            const directRoutes = routes.filter(r => r.transfers === 0);
            const transferRoutes = routes.filter(r => r.transfers > 0);

            const trainMap = getTrainMap();

            // Filter 1: Eliminate nonsensical pre-leg commuter routes (e.g. taking a local train early to board the same express train down the line when the express already stops at the origin)
            const validTransferRoutes = transferRoutes.filter(r => {
                if (!r.legs || r.legs.length < 2) return true;
                const origStation = r.legs[0].from;
                const rDepMin = r.depMin;
                
                for (let i = 1; i < r.legs.length; i++) {
                    const nextTrainNo = r.legs[i].trainNo || r.legs[i].train_number;
                    const nextTrain = trainMap.get(nextTrainNo);
                    if (nextTrain && nextTrain.stops) {
                        const origStop = nextTrain.stops.find(s => s.station === origStation);
                        if (origStop) {
                            const origStopTimeMin = timeToMin(origStop.time);
                            if (origStopTimeMin >= rDepMin) {
                                return false;
                            }
                        }
                    }
                }
                return true;
            });

            // Filter 2: Group by the FIRST TRAIN from origin station!
            const nonDominatedTransfers = [];
            const byFirstTrain = new Map();
            validTransferRoutes.forEach(r => {
                const firstTrainKey = r.legs[0].trainNo || r.legs[0].train_number;
                if (!byFirstTrain.has(firstTrainKey)) byFirstTrain.set(firstTrainKey, []);
                byFirstTrain.get(firstTrainKey).push(r);
            });

            byFirstTrain.forEach((groupRoutes) => {
                for (let i = 0; i < groupRoutes.length; i++) {
                    const r1 = groupRoutes[i];
                    const dep1 = r1.depMin;
                    const arr1 = r1.arrMin;
                    const tx1 = r1.transfers;
                    const trainSeq1 = r1.legs.map(l => l.trainNo || l.train_number).join('-');

                    let dominated = false;
                    for (let j = 0; j < groupRoutes.length; j++) {
                        if (i === j) continue;
                        const r2 = groupRoutes[j];
                        const dep2 = r2.depMin;
                        const arr2 = r2.arrMin;
                        const tx2 = r2.transfers;
                        const trainSeq2 = r2.legs.map(l => l.trainNo || l.train_number).join('-');

                        if (arr2 < arr1) {
                            dominated = true;
                            break;
                        } else if (arr2 === arr1) {
                            if (tx2 < tx1) {
                                dominated = true;
                                break;
                            } else if (tx2 === tx1 && trainSeq1 === trainSeq2) {
                                dominated = true;
                                break;
                            }
                        }
                    }
                    if (!dominated) {
                        nonDominatedTransfers.push(r1);
                    }
                }
            });

            return [...directRoutes, ...nonDominatedTransfers];
        }"""

# In lite.html, replace the pruning block at the end of planLeg:
lite = re.sub(r'// Pruning 3: Strict Pareto Dominance[\s\S]*?return optimal;\s*\}', 'return pruneDominatedRoutes(routes);\n        }\n\n' + lite_prune, lite)

with open('lite.html', 'w', encoding='utf-8') as f:
    f.write(lite)

print("lite.html successfully updated!")
