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

const scripts = html.match(/<script[\s\S]*?>([\s\S]*?>)?([\s\S]*?)<\/script>/gi);
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

console.log('Testing planRoutes: 板橋 -> 宜蘭 at 17:10');
const routes = ctx.planRoutes('板橋', '宜蘭', 1030); // 17:10

console.log(`Total routes: ${routes.length}`);

// Find 4224 direct
const d4224 = routes.find(r => r.transfers === 0 && r.legs[0].train_number === '4224');
console.log('Direct 4224:', d4224 ? `${d4224.dep_time} -> ${d4224.arr_time}` : 'Not found');

// Find transfers starting with 4224
const t4224 = routes.filter(r => r.transfers > 0 && r.legs[0].train_number === '4224');
console.log(`Transfers starting with 4224: ${t4224.length}`);
t4224.forEach(r => {
    console.log(`  BAD TRANSFER: ${r.dep_time} -> ${r.arr_time} (${r.duration}m) via ${r.transfer_stations.join(',')} trains: ${r.legs.map(l=>l.train_number).join('->')}`);
});
