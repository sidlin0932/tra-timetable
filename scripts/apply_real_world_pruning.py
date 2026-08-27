# -*- coding: utf-8 -*-
import re

print("Applying refined real-world pruning logic to index.html and lite.html...")

# 1. Update index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

refined_prune_func = """        // Fast Train Map Cache for O(1) Pre-leg Lookup
        let cachedTrainMap = null;
        function getTrainMap() {
            if (!cachedTrainMap || cachedTrainMap.size !== allTimetableData.length) {
                cachedTrainMap = new Map();
                allTimetableData.forEach(t => cachedTrainMap.set(t.train_number, t));
            }
            return cachedTrainMap;
        }

        // 3. Intelligent Real-World Pruning (去慢保優 ＆ 始發車次平替保留)
        function pruneDominatedRoutes(routes) {
            if (!routes || routes.length <= 1) return routes || [];

            const directRoutes = routes.filter(r => r.transfers === 0);
            const transferRoutes = routes.filter(r => r.transfers > 0);

            const parseMin = (tStr) => {
                if (!tStr || !tStr.includes(':')) return 0;
                const [h, m] = tStr.split(':').map(Number);
                return h * 60 + m;
            };

            const getNormalizedArr = (depMin, arrMin) => {
                return (arrMin < depMin) ? arrMin + 1440 : arrMin;
            };

            const trainMap = getTrainMap();

            // Filter 1: Eliminate nonsensical pre-leg commuter routes
            // (If an express train in leg 2+ already stops at the origin station later, passenger should board the express directly at origin!)
            const validTransferRoutes = transferRoutes.filter(r => {
                if (!r.legs || r.legs.length < 2) return true;
                const origStation = r.legs[0].from;
                const rDepMin = parseMin(r.dep_time);
                
                for (let i = 1; i < r.legs.length; i++) {
                    const nextTrain = trainMap.get(r.legs[i].train_number);
                    if (nextTrain && nextTrain.stops) {
                        const origStop = nextTrain.stops.find(s => s.station === origStation);
                        if (origStop) {
                            const origStopTimeMin = parseMin(origStop.time);
                            // If the express train stopped at origin at or after commuter train departure time, eliminate this redundant early commuter hop!
                            if (origStopTimeMin >= rDepMin) {
                                return false;
                            }
                        }
                    }
                }
                return true;
            });

            // Filter 2: Group by the FIRST TRAIN from origin station!
            // Each distinct first train (e.g. 103 海線, 105 PP自強, 107 普悠瑪, 161 EMU3000) is preserved as an official legitimate departure choice.
            const nonDominatedTransfers = [];
            const byFirstTrain = new Map();
            validTransferRoutes.forEach(r => {
                const firstTrainKey = r.legs[0].train_number;
                if (!byFirstTrain.has(firstTrainKey)) byFirstTrain.set(firstTrainKey, []);
                byFirstTrain.get(firstTrainKey).push(r);
            });

            byFirstTrain.forEach((groupRoutes) => {
                for (let i = 0; i < groupRoutes.length; i++) {
                    const r1 = groupRoutes[i];
                    const dep1 = parseMin(r1.dep_time);
                    const arr1 = getNormalizedArr(dep1, parseMin(r1.arr_time));
                    const tx1 = r1.transfers;
                    const trainSeq1 = r1.legs.map(l => l.train_number).join('-');

                    let dominated = false;
                    for (let j = 0; j < groupRoutes.length; j++) {
                        if (i === j) continue;
                        const r2 = groupRoutes[j];
                        const dep2 = parseMin(r2.dep_time);
                        const arr2 = getNormalizedArr(dep2, parseMin(r2.arr_time));
                        const tx2 = r2.transfers;
                        const trainSeq2 = r2.legs.map(l => l.train_number).join('-');

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
        }
        window.pruneDominatedRoutes = pruneDominatedRoutes;"""

# Replace in index.html
html = re.sub(r'function pruneDominatedRoutes\(routes\)\s*\{[\s\S]*?window\.pruneDominatedRoutes = pruneDominatedRoutes;', refined_prune_func, html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated with refined real-world pruning!")
