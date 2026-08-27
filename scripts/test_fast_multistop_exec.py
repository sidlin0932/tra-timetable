# -*- coding: utf-8 -*-
import subprocess
import sys

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

// Define optimized planMultiStopRoutes in sandbox
const optMultiStop = function(wps, startTimeMin) {
    if (!wps || wps.length < 2) return [];
    if (wps.length === 2) {
        return sandbox.planRoutes(wps[0].station, wps[1].station, startTimeMin);
    }

    let candidateChains = sandbox.planRoutes(wps[0].station, wps[1].station, startTimeMin).slice(0, 25);
    if (candidateChains.length === 0) return [];

    for (let seg = 1; seg < wps.length - 1; seg++) {
        const segOrig = wps[seg].station;
        const segDest = wps[seg + 1].station;
        const minStay = parseInt(wps[seg].minStay || 0, 10);
        
        const minArrMin = Math.min(...candidateChains.map(c => sandbox.timeToMin(c.arr_time)));
        const allSegRoutes = sandbox.planRoutes(segOrig, segDest, minArrMin + minStay);
        if (allSegRoutes.length === 0) return [];

        const nextChains = [];
        for (let cIdx = 0; cIdx < candidateChains.length; cIdx++) {
            const chain = candidateChains[cIdx];
            const arrMin = sandbox.timeToMin(chain.arr_time);
            const earliestDep = arrMin + minStay;
            
            const viableNext = allSegRoutes.filter(r => sandbox.timeToMin(r.dep_time) >= earliestDep).slice(0, 3);
            for (let nIdx = 0; nIdx < viableNext.length; nIdx++) {
                const nRoute = viableNext[nIdx];
                const depMin = sandbox.timeToMin(nRoute.dep_time);
                const stayActual = depMin - arrMin;

                const newLegs = [
                    ...chain.legs,
                    ...nRoute.legs.map((l, lIdx) => lIdx === 0 ? { ...l, stayBefore: stayActual, layover: stayActual } : l)
                ];

                const totalDuration = sandbox.timeToMin(nRoute.arr_time) - sandbox.timeToMin(chain.dep_time);

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
};

const t0 = Date.now();
const wps = [
    { station: '社頭', minStay: 0 },
    { station: '百福', minStay: 0 },
    { station: '暖暖', minStay: 0 }
];

const r = optMultiStop(wps, 0);
const elapsed = Date.now() - t0;
console.log(`社頭 -> 百福 -> 暖暖 finished in ${elapsed}ms! Total routes: ${r.length}`);

r.slice(0, 5).forEach(route => {
    const legsStr = route.legs.map(l => `${l.train_type} ${l.train_number} (${l.from} ${l.dep} -> ${l.to} ${l.arr})`).join(' -> ');
    console.log(`[${route.dep_time} -> ${route.arr_time} (${route.duration}m, tx=${route.transfers})] ${legsStr}`);
});
"""

res = subprocess.run(["node", "-e", test_js], capture_output=True, text=True, encoding="utf-8")
sys.stdout.buffer.write(res.stdout.encode('utf-8'))
if res.stderr:
    sys.stderr.buffer.write(res.stderr.encode('utf-8'))
