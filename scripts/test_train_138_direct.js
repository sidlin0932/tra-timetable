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

const r1 = sandbox.planRoutes('後龍', '七堵', 1100, '');
console.log('後龍 -> 七堵 (after 18:20):');
r1.forEach(r => {
    console.log(`  ${r.dep_time} -> ${r.arr_time} (${r.duration}分) [${r.legs.map(l => l.train_type + ' ' + l.train_number).join(' -> ')}] (轉乘: ${r.transfers})`);
});

const r2 = sandbox.planRoutes('屏東', '七堵', 900, '');
console.log('\n屏東 -> 七堵 (after 15:00):');
r2.filter(r => r.legs.some(l => l.train_number === '138')).forEach(r => {
    console.log(`  ${r.dep_time} -> ${r.arr_time} (${r.duration}分) [${r.legs.map(l => l.train_type + ' ' + l.train_number).join(' -> ')}] (轉乘: ${r.transfers})`);
});
