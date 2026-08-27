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
buildDeparturesIndex();
const orig = '社頭';
const dest = '百福';

console.log('Taipei -> Baifu departures:', (departuresByStation['台北']||[]).length);
console.log('Qidu -> Baifu departures:', (departuresByStation['七堵']||[]).length);

// Let's trace transferResults in planRoutes
const origDeps = departuresByStation[orig] || [];
let transferResults = [];
let queue = [];
origDeps.forEach(firstDep => {
    if (firstDep.depTimeMin < 360) return;
    const train1 = firstDep.train;
    for (let j = firstDep.stopIdx + 1; j < train1.stops.length; j++) {
        const nextSt = train1.stops[j].station;
        const arrMin = timeToMin(train1.stops[j].time);
        if (KEY_HUBS.has(nextSt) && !isStationOvershooting(orig, dest, nextSt)) {
            queue.push({ currentStation: nextSt, currentTimeMin: arrMin, train: train1.train_number });
        }
    }
});
console.log('Queue size:', queue.length);

queue.forEach(state => {
    const deps = departuresByStation[state.currentStation] || [];
    const minDep = state.currentTimeMin + 3;
    deps.forEach(d => {
        if (d.depTimeMin < minDep || d.depTimeMin > minDep + 75) return;
        const train = d.train;
        for (let j = d.stopIdx + 1; j < train.stops.length; j++) {
            if (train.stops[j].station === dest) {
                console.log('Found route to Baifu via', state.currentStation, 'train', d.train.train_number, 'at', train.stops[j].time);
            }
        }
    });
});
`;
vm.runInContext(debugCode, sandbox);
