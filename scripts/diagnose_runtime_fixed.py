# -*- coding: utf-8 -*-
import subprocess

test_js = """
const fs = require('fs');
const vm = require('vm');

const sandbox = {
    window: {
        addEventListener: () => {},
        location: { search: '', href: '', replace: () => {} }
    },
    document: {
        getElementById: (id) => {
            if (id === 'timeInput') return { value: '05:00' };
            if (id === 'viaInput') return { value: '' };
            if (id === 'routeSummaryText') return { textContent: '' };
            if (id === 'primarySort') return { value: 'arr_time-asc' };
            if (id === 'secondarySort') return { value: 'duration-asc' };
            if (id === 'resultsCount') return { textContent: '' };
            if (id === 'resultsList') return { innerHTML: '' };
            if (id === 'btnClearVia') return { style: {} };
            if (id === 'waypointsList') return { innerHTML: '' };
            if (id === 'waypointsCountBadge') return { textContent: '' };
            if (id === 'viaGroupBlock') return { style: {} };
            return { value: '', textContent: '', innerHTML: '', style: {}, classList: { add: ()=>{}, remove: ()=>{} } };
        },
        querySelectorAll: () => []
    },
    navigator: { onLine: true },
    location: { search: '', href: '', replace: () => {} },
    addEventListener: () => {},
    setInterval: (fn) => fn(),
    clearInterval: () => {},
    setTimeout: (fn) => fn(),
    requestAnimationFrame: (fn) => fn(),
    console: console,
    URLSearchParams: function() { return { get: () => null }; }
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

console.log('Total timetable trains:', sandbox.allTimetableData.length);

const r1 = sandbox.planRoutes('板橋', '台北', 300, '');
console.log('planRoutes 板橋->台北 count:', r1 ? r1.length : 0);

const r2 = sandbox.planRoutes('台北', '內灣', 300, '');
console.log('planRoutes 台北->內灣 count:', r2 ? r2.length : 0);

const r3 = sandbox.planRoutes('內灣', '六家', 300, '');
console.log('planRoutes 內灣->六家 count:', r3 ? r3.length : 0);

sandbox.waypoints = [
    { station: '板橋', minStay: 0 },
    { station: '台北', minStay: 0 }
];

sandbox.executeSearch();
console.log('executeSearch currentRoutes count:', sandbox.currentRoutes ? sandbox.currentRoutes.length : 0);
"""

res = subprocess.run(["node", "-e", test_js], capture_output=True, text=True, encoding="utf-8")
print("STDOUT:\n", res.stdout)
print("STDERR:\n", res.stderr)
