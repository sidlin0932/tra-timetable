const fs = require('fs');
const vm = require('vm');

const sandbox = {
    window: { addEventListener: () => {}, location: { search: '', href: '', replace: () => {} } },
    document: { getElementById: () => ({ value: '', textContent: '', innerHTML: '', style: {}, classList: { add: ()=>{}, remove: ()=>{} } }), querySelectorAll: () => [] },
    navigator: { onLine: true }, location: { search: '', href: '', replace: () => {} },
    addEventListener: () => {}, URLSearchParams: URLSearchParams, setInterval: () => {}, clearInterval: () => {}, setTimeout: (fn) => fn(), requestAnimationFrame: (fn) => fn(), localStorage: { getItem: () => null, setItem: () => {} }, console: console
};
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync('data.js', 'utf8'), sandbox);
sandbox.allTimetableData = sandbox.window.EMBEDDED_TIMETABLE_DATA || [];
const indexHtml = fs.readFileSync('index.html', 'utf8');
const scriptMatches = indexHtml.match(/<script(?![^>]*src=)>([\s\S]*?)<\/script>/g);
vm.runInContext(scriptMatches[scriptMatches.length - 1].replace(/<\/?script[^>]*>/g, ''), sandbox);

const debugCode = `
currentDayFilter = 'all';
buildDeparturesIndex();

const r = planRoutes('社頭', '百福', 360, '');
console.log('planRoutes(社頭 -> 百福):', r.length);

const wp = [ { station: '社頭', minStay: 0 }, { station: '百福', minStay: 30 }, { station: '暖暖', minStay: 0 } ];
const mr = planMultiStopRoutes(wp, 360);
console.log('planMultiStopRoutes:', mr.length);
`;
vm.runInContext(debugCode, sandbox);
