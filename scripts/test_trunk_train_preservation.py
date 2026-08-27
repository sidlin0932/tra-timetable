import subprocess
import json

test_js = """
const vm = require('vm');
const fs = require('fs');

const sandbox = {
    window: { addEventListener: () => {}, location: { search: '', href: '', replace: () => {} } },
    document: { getElementById: () => ({ value: '', textContent: '', innerHTML: '', style: {}, classList: { add: ()=>{}, remove: ()=>{} } }), querySelectorAll: () => [] },
    navigator: { onLine: true },
    location: { search: '', href: '', replace: () => {} },
    addEventListener: () => {},
    URLSearchParams: URLSearchParams,
    setInterval: () => {},
    clearInterval: () => {},
    setTimeout: (fn) => fn(),
    requestAnimationFrame: (fn) => fn(),
    console: console
};
vm.createContext(sandbox);

const dataCode = fs.readFileSync('data.js', 'utf8');
vm.runInContext(dataCode, sandbox);
sandbox.allTimetableData = sandbox.window.EMBEDDED_TIMETABLE_DATA || [];

const indexHtml = fs.readFileSync('index.html', 'utf8');
const scriptMatches = indexHtml.match(/<script(?![^>]*src=)>([\\s\\S]*?)<\\/script>/g);
const mainScript = scriptMatches[scriptMatches.length - 1].replace(/<\\/?script[^>]*>/g, '');
vm.runInContext(mainScript, sandbox);
sandbox.buildDeparturesIndex();

const trainMap = new Map();
sandbox.allTimetableData.forEach(t => trainMap.set(t.train_number, t));

// Intelligent Multi-Choice Trunk Train Preservation
sandbox.pruneDominatedRoutes = function(routes) {
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

    // Filter 1: Eliminate nonsensical pre-leg commuter routes
    // (If the 2nd train ALREADY stopped at origin station at or after route departure time, passenger should board the 2nd train directly!)
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
                        return false;
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
        // Pick the best connection (e.g. fewer transfers, or shortest layover)
        groupRoutes.sort((a, b) => {
            if (a.duration !== b.duration) return a.duration - b.duration;
            return a.transfers - b.transfers;
        });
        // Keep the best 1-2 distinct middle-leg transfer paths for this trunk train
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
};

// Query Jiji -> Banqiao from 18:00
const r = sandbox.planRoutes('集集', '板橋', 1080, '');
console.log('Total Jiji -> Banqiao routes from 18:00:', r.length);
r.sort((a, b) => sandbox.timeToMin(a.dep_time) - sandbox.timeToMin(b.dep_time) || sandbox.timeToMin(a.arr_time) - sandbox.timeToMin(b.arr_time));
r.forEach(route => {
    const legsStr = route.legs.map(l => `${l.train_type} ${l.train_number} (${l.from} ${l.dep} -> ${l.to} ${l.arr})`).join(' -> ');
    console.log(`[${route.dep_time} -> ${route.arr_time} (${route.duration}m, tx=${route.transfers})] ${legsStr}`);
});
"""

res = subprocess.run(["node", "-e", test_js], capture_output=True, text=True, encoding="utf-8")
print(res.stdout)
