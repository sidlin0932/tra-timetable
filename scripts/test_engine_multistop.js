const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync('index.html', 'utf8');

const fakeWindow = {
    addEventListener: () => {},
    location: { search: '', href: '' },
    navigator: { serviceWorker: { register: () => Promise.resolve(), addEventListener: () => {} } },
    document: { 
        addEventListener: () => {},
        getElementById: () => ({ value: '', textContent: '', innerHTML: '', style: {}, classList: { add: ()=>{}, remove: ()=>{} } })
    }
};

const ctx = vm.createContext({
    window: fakeWindow,
    document: fakeWindow.document,
    navigator: fakeWindow.navigator,
    location: fakeWindow.location,
    URLSearchParams: class { get() { return null; } },
    console,
    Math,
    Set,
    Map,
    Array,
    Object,
    parseInt,
    parseFloat,
    performance: { now: () => Date.now() }
});

// Load data.js
const dataJs = fs.readFileSync('data.js', 'utf8');
vm.runInContext(dataJs, ctx);

// Extract main script
const scripts = html.match(/<script[\s\S]*?>([\s\S]*?)<\/script>/gi);
let engineScript = '';
for (const s of scripts) {
    if (s.includes('planMultiStopRoutes')) {
        engineScript = s.replace(/<\/?script[\s\S]*?>/gi, '');
        break;
    }
}

vm.runInContext(engineScript, ctx);
ctx.allTimetableData = ctx.EMBEDDED_TIMETABLE_DATA;
ctx.buildDeparturesIndex();

console.log('Testing in-engine planMultiStopRoutes: 板橋 -> 宜蘭 -> 板橋');

const leg1 = ctx.planRoutes('板橋', '宜蘭', 360);
console.log('Leg 1 count:', leg1.length);
if (leg1.length > 0) {
    console.log('Sample leg 1:', leg1[0].dep_time, leg1[0].arr_time);
}

const leg2 = ctx.planRoutes('宜蘭', '板橋', 480);
console.log('Leg 2 count:', leg2.length);
if (leg2.length > 0) {
    console.log('Sample leg 2:', leg2[0].dep_time, leg2[0].arr_time);
}

const wps = [
    { station: '板橋', minStay: 0 },
    { station: '宜蘭', minStay: 30 },
    { station: '板橋', minStay: 0 }
];

const results = ctx.planMultiStopRoutes(wps, 360);
console.log('Results count:', results.length);
if (results.length > 0) {
    console.log('Top 3 results:');
    results.slice(0, 3).forEach((r, idx) => {
        console.log(`  #${idx+1} ${r.dep_time} -> ${r.arr_time} (共 ${r.duration} 分鐘, ${r.legs.length} 段列車)`);
        r.legs.forEach((l, lIdx) => {
            console.log(`    Leg ${lIdx+1}: ${l.train_type} ${l.train_number} (${l.from} ${l.dep} -> ${l.to} ${l.arr}) ${l.stayBefore !== undefined ? '[宜蘭停留 ' + l.stayBefore + ' 分鐘]' : ''}`);
        });
    });
}
