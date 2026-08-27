import json
import subprocess

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

// Fast Hash Map of all trains
const trainMap = new Map();
sandbox.allTimetableData.forEach(t => trainMap.set(t.train_number, t));

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
            if (nextTrain) {
                const origStop = nextTrain.stops.find(s => s.station === origStation);
                if (origStop) {
                    const origStopTimeMin = parseMin(origStop.time);
                    if (origStopTimeMin >= rDepMin) {
                        return false; // Eliminate weird pre-leg detour!
                    }
                }
            }
        }
        return true;
    });

    // Filter 2: Group by the FIRST TRAIN from origin station!
    // Each distinct first train (e.g. 103, 105, 107, 161) is preserved as an official legitimate departure choice.
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
};

const r = sandbox.planRoutes('板橋', '車埕', 0, '');
console.log('Total Banqiao -> Checheng routes with refined pruning:', r.length);
r.sort((a,b) => sandbox.timeToMin(a.dep_time) - sandbox.timeToMin(b.dep_time));
r.slice(0, 10).forEach(route => {
    const legsStr = route.legs.map(l => `${l.train_type} ${l.train_number} (${l.from} ${l.dep} -> ${l.to} ${l.arr})`).join(' -> ');
    console.log(`[${route.dep_time} -> ${route.arr_time} (${route.duration}m, tx=${route.transfers})] ${legsStr}`);
});
"""

res = subprocess.run(["node", "-e", test_js], capture_output=True, text=True, encoding="utf-8")
print(res.stdout)
