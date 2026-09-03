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

const dataJs = fs.readFileSync('data.js', 'utf8');
vm.runInContext(dataJs, ctx);

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

console.log('Testing planRoutes: 板橋 -> 宜蘭 from 16:55 (1015 min)');
const routes = ctx.planRoutes('板橋', '宜蘭', 1015);
console.log(`Total routes found: ${routes.length}`);

// Check if ANY route uses 桃園, 中壢, or 樹林 as transfer station
const badRoutes = routes.filter(r => r.transfer_stations.some(s => ['桃園', '中壢', '樹林', '內壢', '楊梅', '新竹'].includes(s)));
console.log(`Routes with reverse-ride (桃園/中壢/樹林): ${badRoutes.length}`);

if (badRoutes.length > 0) {
    console.log('BAD ROUTES DETECTED:');
    badRoutes.slice(0, 5).forEach(r => {
        console.log(`  ${r.dep_time} -> ${r.arr_time} (${r.duration}m) via [${r.transfer_stations.join(', ')}] | trains: ${r.legs.map(l=>l.train_number).join(' -> ')}`);
    });
} else {
    console.log('SUCCESS: ZERO reverse-ride routes detected!');
}

console.log('\nTop 5 valid routes from 板橋 to 宜蘭:');
routes.slice(0, 5).forEach((r, idx) => {
    console.log(`  #${idx+1} ${r.dep_time} -> ${r.arr_time} (${r.duration}分, 轉乘${r.transfers}次 ${r.transfer_stations.length ? 'via ' + r.transfer_stations.join(',') : '直達'})`);
    r.legs.forEach((l, lIdx) => {
        console.log(`     Leg ${lIdx+1}: ${l.train_type} ${l.train_number} (${l.from} ${l.dep} -> ${l.to} ${l.arr})`);
    });
});
