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

const testPairs = [
    ['板橋', '宜蘭', 1015],
    ['台北', '台中', 360],
    ['社頭', '百福', 360],
    ['內灣', '六家', 360],
    ['屏東', '台東', 360],
    ['潮州', '花蓮', 360],
    ['台南', '台北', 360],
    ['基隆', '新竹', 360]
];

console.log('Running comprehensive routing sanity checks:');
let allPassed = true;
for (const [orig, dest, startMin] of testPairs) {
    const r = ctx.planRoutes(orig, dest, startMin);
    console.log(`  ${orig} ➔ ${dest} (from ${startMin}m): ${r.length} routes found`);
    if (r.length === 0) {
        console.error(`  ERROR: 0 routes for ${orig} -> ${dest}!`);
        allPassed = false;
    }
}

if (allPassed) {
    console.log('\nALL TEST PAIRS PASSED PERFECTLY!');
} else {
    process.exit(1);
}
