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

vm.runInContext("currentDayFilter = 'all'; buildDeparturesIndex();", sandbox);

const routesAll = sandbox.planRoutes('二水', '彰化', 0, '');
console.log('Ershui -> Changhua all day routes count:', routesAll.length);
console.log('Direct routes count:', routesAll.filter(r => r.transfers === 0).length);

const routesNight = sandbox.planRoutes('二水', '彰化', 1140, '');
console.log('\nErshui -> Changhua from 19:00 routes count:', routesNight.length);
routesNight.forEach(r => {
    console.log(`  ${r.dep_time} -> ${r.arr_time} (${r.duration}分) [${r.legs.map(l => l.train_type + ' ' + l.train_number).join(' -> ')}]`);
});
