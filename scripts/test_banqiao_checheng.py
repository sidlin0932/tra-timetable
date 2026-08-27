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

// Query Banqiao -> Checheng
const r = sandbox.planRoutes('板橋', '車埕', 0, '');
console.log('Total Banqiao -> Checheng routes:', r.length);
r.slice(0, 10).forEach(route => {
    const legsStr = route.legs.map(l => `${l.train_type} ${l.train_number} (${l.from} ${l.dep} -> ${l.to} ${l.arr})`).join(' -> ');
    console.log(`[${route.dep_time} -> ${route.arr_time} (${route.duration}m, tx=${route.transfers})] ${legsStr}`);
});
"""

res = subprocess.run(["node", "-e", test_js], capture_output=True, text=True, encoding="utf-8")
sys.stdout.buffer.write(res.stdout.encode('utf-8'))
if res.stderr:
    sys.stderr.buffer.write(res.stderr.encode('utf-8'))
