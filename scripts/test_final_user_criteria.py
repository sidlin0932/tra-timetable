# -*- coding: utf-8 -*-
import subprocess
import sys

test_script = """
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

// 1. Verify Taipei -> Dajia (Sea line)
const rSea = sandbox.planRoutes('台北', '大甲', 0, '');
const seaDirects = rSea.filter(r => r.transfers === 0);
console.log('Taipei -> Dajia direct trains:', seaDirects.length);
if (seaDirects.length < 5) throw new Error('Sea direct trains missing!');

// 2. Verify Taipei -> Taichung (Mountain line)
const rMt = sandbox.planRoutes('台北', '台中', 0, '');
const mtDirects = rMt.filter(r => r.transfers === 0);
console.log('Taipei -> Taichung direct trains:', mtDirects.length);
if (mtDirects.length < 20) throw new Error('Mountain direct trains missing!');

// 3. Verify Slower Transfer Options with Same Arrival are Pruned
const transfers = rMt.filter(r => r.transfers > 0);
for (let i = 0; i < transfers.length; i++) {
    const tr = transfers[i];
    for (let j = 0; j < rMt.length; j++) {
        const cand = rMt[j];
        if (tr === cand) continue;
        if (cand.arr_time === tr.arr_time && cand.dep_time > tr.dep_time) {
            throw new Error(`Dominance violation! Transfer Route (${tr.dep_time} -> ${tr.arr_time}) should have been pruned by (${cand.dep_time} -> ${cand.arr_time})`);
        }
    }
}
console.log('Pareto Transfer Pruning Test: PASS! All dominated slower transfer routes were eliminated.');

// 4. Verify getTrainTypeBadge outputs Mountain / Sea line badges
const badge105 = sandbox.getTrainTypeBadge('自強號', '105');
if (!badge105.includes('山線')) throw new Error('105 Mountain badge missing!');
console.log('Badge 105 (Mountain): PASS');

const badge103 = sandbox.getTrainTypeBadge('自強號', '103');
if (!badge103.includes('海線')) throw new Error('103 Sea badge missing!');
console.log('Badge 103 (Sea): PASS');

console.log('ALL USER CRITERIA VERIFIED 100% SUCCESSFULLY!');
"""

res = subprocess.run(["node", "-e", test_script], capture_output=True, text=True, encoding="utf-8")
sys.stdout.buffer.write(res.stdout.encode('utf-8'))
if res.stderr:
    sys.stderr.buffer.write(res.stderr.encode('utf-8'))
if res.returncode != 0:
    exit(1)
