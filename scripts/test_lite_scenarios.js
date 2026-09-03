const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

console.log("=== Lite.html System Scenarios Audit ===\n");

const html = fs.readFileSync('lite.html', 'utf8');

const fakeWindow = {
    addEventListener: () => {},
    location: { search: '', href: '' },
    navigator: { serviceWorker: { register: () => Promise.resolve(), addEventListener: () => {} } },
    document: { 
        addEventListener: () => {},
        getElementById: () => ({ value: '', textContent: '', innerHTML: '', style: {}, classList: { add: ()=>{}, remove: ()=>{} } }),
        querySelectorAll: () => []
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
    Date,
    parseInt,
    parseFloat,
    performance: { now: () => Date.now() }
});

const scripts = html.match(/<script[\s\S]*?>([\s\S]*?)<\/script>/gi);
for (const s of scripts) {
    if (s.includes('src=')) continue;
    const code = s.replace(/<\/?script[\s\S]*?>/gi, '');
    try {
        vm.runInContext(code, ctx);
    } catch(e) {}
}

const timetableDataStr = fs.readFileSync('full_network_timetable.json', 'utf8');
vm.runInContext(`
    timetableData = ${timetableDataStr};
    buildIndex();
`, ctx);

let passedCount = 0;
let totalTests = 0;

function runScenario(title, fn) {
    totalTests++;
    try {
        fn();
        console.log(`[PASS] ${title}`);
        passedCount++;
    } catch(err) {
        console.error(`[FAIL] ${title}`);
        console.error(`       Error: ${err.stack}`);
    }
}

runScenario("Lite Scenario 1: 台北 -> 台中 Direct Express", () => {
    const routes = vm.runInContext(`planLeg("台北", "台中", 360, 'all', 'all')`, ctx);
    assert(routes.length >= 15, `Expected >= 15 routes, got ${routes.length}`);
    const directExpress = routes.filter(r => r.transfers === 0 && ['自強號', '新自強(EMU3000)', '普悠瑪'].includes(r.legs[0].trainType));
    assert(directExpress.length >= 12, `Expected >= 12 direct express, got ${directExpress.length}`);
});

runScenario("Lite Scenario 2: 高雄 -> 台東 Direct South Link", () => {
    const routes = vm.runInContext(`planLeg("高雄", "台東", 360, 'all', 'all')`, ctx);
    assert(routes.length >= 5, `Expected >= 5 routes, got ${routes.length}`);
    const direct = routes.filter(r => r.transfers === 0);
    assert(direct.length >= 4, `Expected >= 4 direct trains, got ${direct.length}`);
});

runScenario("Lite Scenario 3: 二水 -> 七堵 (No getting off direct train 270)", () => {
    const routes = vm.runInContext(`planLeg("二水", "七堵", 360, 'all', 'all')`, ctx);
    const badTransfer = routes.find(r => r.transfers > 0 && String(r.legs[0].trainNo) === '270');
    assert(!badTransfer, "Lite found redundant transfer off train 270");
});

console.log(`\n========================================`);
console.log(`Lite Audit Summary: ${passedCount} / ${totalTests} scenarios PASSED.`);
console.log(`========================================`);

if (passedCount === totalTests) {
    console.log("LITE EDITION VERIFIED SUCCESSFULLY!");
    process.exit(0);
} else {
    process.exit(1);
}
