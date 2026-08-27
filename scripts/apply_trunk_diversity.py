# -*- coding: utf-8 -*-
import re

print("Updating index.html and lite.html with Intelligent Trunk Train Preservation (去無意義前贅步，保留152/150等多元幹線選擇)...")

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

        // 3. Intelligent Real-World Pruning: 去除無意義前贅步，全面保留多元主力列車 (如 152, 150, EMU3000, 普悠瑪)
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
                            if (origStopTimeMin >= rDepMin) {
                                return false; // Eliminate redundant pre-leg detour!
                            }
                        }
                    }
                }
                return true;
            });

            // Filter 2: Group by (First Train, Final Trunk Train)!
            // This guarantees that every distinct primary express train (e.g. 150, 152, 154, 168, 2046)
            // gets its optimal feeder connection preserved without being wiped out by earlier arrivals!
            const byPair = new Map();
            validTransferRoutes.forEach(r => {
                const firstTrain = r.legs[0].train_number;
                const lastTrain = r.legs[r.legs.length - 1].train_number;
                const key = `${firstTrain}___${lastTrain}`;
                if (!byPair.has(key)) byPair.set(key, []);
                byPair.get(key).push(r);
            });

            const nonDominatedTransfers = [];
            byPair.forEach(groupRoutes => {
                // Within the SAME (First Train -> Last Train) combo:
                // Sort by total duration, then transfers
                groupRoutes.sort((a, b) => {
                    if (a.duration !== b.duration) return a.duration - b.duration;
                    return a.transfers - b.transfers;
                });
                
                // Keep the best distinct middle-leg transfer paths for this trunk train
                const seenSeq = new Set();
                groupRoutes.forEach(r => {
                    const seq = r.legs.map(l => l.train_number).join('-');
                    if (!seenSeq.has(seq) && seenSeq.size < 2) {
                        seenSeq.add(seq);
                        nonDominatedTransfers.push(r);
                    }
                });
            });

            return [...directRoutes, ...nonDominatedTransfers];
        }
        window.pruneDominatedRoutes = pruneDominatedRoutes;"""

html = re.sub(r'// Fast Train Map Cache[\s\S]*?window\.pruneDominatedRoutes = pruneDominatedRoutes;', refined_prune_func, html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 2. Update lite.html
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

        // Pruning: 去除無意義前贅步，全面保留多元主力列車 (如 152, 150, EMU3000, 普悠瑪)
        function pruneDominatedRoutes(routes) {
            if (!routes || routes.length <= 1) return routes || [];

            const directRoutes = routes.filter(r => r.transfers === 0);
            const transferRoutes = routes.filter(r => r.transfers > 0);

            const trainMap = getTrainMap();

            // Filter 1: Eliminate nonsensical pre-leg commuter routes
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

            // Filter 2: Group by (First Train, Final Trunk Train)!
            const byPair = new Map();
            validTransferRoutes.forEach(r => {
                const firstTrain = r.legs[0].trainNo || r.legs[0].train_number;
                const lastTrain = r.legs[r.legs.length - 1].trainNo || r.legs[r.legs.length - 1].train_number;
                const key = `${firstTrain}___${lastTrain}`;
                if (!byPair.has(key)) byPair.set(key, []);
                byPair.get(key).push(r);
            });

            const nonDominatedTransfers = [];
            byPair.forEach(groupRoutes => {
                groupRoutes.sort((a, b) => {
                    if (a.duration !== b.duration) return a.duration - b.duration;
                    return a.transfers - b.transfers;
                });
                const seenSeq = new Set();
                groupRoutes.forEach(r => {
                    const seq = r.legs.map(l => l.trainNo || l.train_number).join('-');
                    if (!seenSeq.has(seq) && seenSeq.size < 2) {
                        seenSeq.add(seq);
                        nonDominatedTransfers.push(r);
                    }
                });
            });

            return [...directRoutes, ...nonDominatedTransfers];
        }"""

lite = re.sub(r'// Fast Train Map Cache[\s\S]*?return \[\.\.\.directRoutes, \.\.\.nonDominatedTransfers\];\s*\}', lite_prune, lite)

with open('lite.html', 'w', encoding='utf-8') as f:
    f.write(lite)

print("index.html and lite.html updated successfully!")
