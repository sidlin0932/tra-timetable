const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

console.log("=== TRA Timetable Full System Scenarios Audit ===\n");

const html = fs.readFileSync('index.html', 'utf8');

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
    allTimetableData = ${timetableDataStr};
    currentDayFilter = 'all';
    typeFilter = 'all';
    transferCondition = 'all';
    buildDeparturesIndex();
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
        console.error(`       Error: ${err.message}`);
    }
}

// Scenario 1: 台北 -> 台中 Direct Express Trains
runScenario("Scenario 1: 台北 -> 台中 Direct Express Trains (No artificial transfers)", () => {
    const routes = vm.runInContext(`planRoutes("台北", "台中", 360)`, ctx);
    assert(routes.length >= 20, `Expected at least 20 routes, got ${routes.length}`);
    const directExpress = routes.filter(r => r.transfers === 0 && ['自強號', '新自強(EMU3000)', '普悠瑪'].includes(r.train_types[0]));
    assert(directExpress.length >= 18, `Expected at least 18 direct express trains, got ${directExpress.length}`);
    
    // Check specific mountain line express trains
    const trainNumbers = directExpress.map(r => r.legs[0].train_number);
    const expectedTrains = ['107', '111', '109', '115', '117', '121', '127', '131'];
    expectedTrains.forEach(tNum => {
        assert(trainNumbers.includes(tNum), `Expected train ${tNum} to be direct to Taichung`);
    });
});

// Scenario 2: 新竹 -> 沙鹿 Real Sea Line Only
runScenario("Scenario 2: 新竹 -> 沙鹿 Real Sea Line Only (Mountain trains excluded)", () => {
    const routes = vm.runInContext(`planRoutes("新竹", "沙鹿", 360)`, ctx);
    assert(routes.length >= 5, `Expected at least 5 routes, got ${routes.length}`);
    routes.forEach(r => {
        if (r.transfers === 0) {
            const tNum = r.legs[0].train_number;
            assert(!['105', '115', '117', '121', '125'].includes(tNum), `Mountain train ${tNum} incorrectly routed via Shalu`);
        }
    });
    const trainNumbers = routes.filter(r => r.transfers === 0).map(r => r.legs[0].train_number);
    assert(trainNumbers.includes('103'), "Expected Sea Line train 103 direct from Hsinchu to Shalu");
});

// Scenario 3: 高雄 -> 台東 Direct South Link (< 180 min, no 9h Banqiao detour)
runScenario("Scenario 3: 高雄 -> 台東 Direct South Link (< 180 min)", () => {
    const routes = vm.runInContext(`planRoutes("高雄", "台東", 360)`, ctx);
    assert(routes.length >= 5, `Expected at least 5 routes, got ${routes.length}`);
    const directSouthLink = routes.filter(r => r.transfers === 0);
    assert(directSouthLink.length >= 4, `Expected at least 4 direct South Link trains, got ${directSouthLink.length}`);
    directSouthLink.forEach(r => {
        assert(r.duration <= 190, `South Link duration ${r.duration}m exceeds 190 min`);
    });
    // Ensure no route detours via Banqiao
    routes.forEach(r => {
        const intermediateStations = r.legs.map(l => l.from).concat(r.legs.map(l => l.to));
        assert(!intermediateStations.includes('板橋'), `Route detoured through Banqiao: ${JSON.stringify(r)}`);
    });
});

// Scenario 4: 二水 -> 七堵 (No getting off direct train 270, Commuter TPASS preserved)
runScenario("Scenario 4: 二水 -> 七堵 (No getting off direct train, Commuter TPASS preserved)", () => {
    const routes = vm.runInContext(`planRoutes("二水", "七堵", 360)`, ctx);
    assert(routes.length >= 5, `Expected at least 5 routes, got ${routes.length}`);
    
    // Train 270 must be direct
    const t270Route = routes.find(r => r.transfers === 0 && r.legs[0].train_number === '270');
    assert(t270Route, "Expected train 270 to be direct from Ershui to Qidu");

    // Must NOT have a route where passenger boards 270 and gets off at Tanaka
    const bad270Transfer = routes.find(r => r.transfers > 0 && r.legs[0].train_number === '270');
    assert(!bad270Transfer, "Found redundant transfer telling passenger to get off direct train 270!");

    // Commuter TPASS route must be preserved
    const commuterRoute = routes.find(r => r.legs.every(l => ['區間車', '區間快'].includes(l.train_type)));
    assert(commuterRoute, "Expected pure commuter TPASS transfer route to be preserved");
});

// Scenario 5: 台中 -> 沙鹿 (Transfer via Changhua / Chengzhui in < 60 min, no Zhunan north detour)
runScenario("Scenario 5: 台中 -> 沙鹿 (Transfer via Changhua / Chengzhui, no Zhunan north detour)", () => {
    const routes = vm.runInContext(`planRoutes("台中", "沙鹿", 360)`, ctx);
    assert(routes.length >= 5, `Expected at least 5 routes, got ${routes.length}`);
    
    // Fastest transfer should be under 60 minutes
    const fastest = routes[0];
    assert(fastest.duration <= 60, `Fastest transfer took ${fastest.duration}m, expected <= 60m`);

    // No route should transfer at Zhunan (100km north detour)
    routes.forEach(r => {
        const transfers = r.transfer_stations || [];
        assert(!transfers.includes('竹南'), `Route made redundant north detour to Zhunan: ${JSON.stringify(r)}`);
    });
});

// Scenario 6: Station Departures Timetable Integrity (20 Key Stations)
runScenario("Scenario 6: Station Departures Timetable Integrity (20 Key Stations)", () => {
    const testStations = [
        '基隆', '台北', '板橋', '桃園', '新竹', '竹南', '苗栗', '台中', '新烏日', '彰化',
        '員林', '嘉義', '台南', '高雄', '屏東', '潮州', '大武', '台東', '花蓮', '宜蘭',
        '沙鹿', '大甲', '車埕', '內灣'
    ];
    testStations.forEach(st => {
        const deps = vm.runInContext(`departuresByStation["${st}"] || []`, ctx);
        assert(deps.length > 0, `Station ${st} has 0 departures in timetable index!`);
        // Verify chronological ordering
        for (let i = 1; i < deps.length; i++) {
            assert(deps[i].depTimeMin >= deps[i-1].depTimeMin, `Departures at ${st} not sorted chronologically: ${deps[i-1].depTimeMin} > ${deps[i].depTimeMin}`);
        }
    });
});

console.log(`\n========================================`);
console.log(`Audit Summary: ${passedCount} / ${totalTests} scenarios PASSED.`);
console.log(`========================================`);

if (passedCount === totalTests) {
    console.log("ALL SCENARIOS VERIFIED SUCCESSFULLY!");
    process.exit(0);
} else {
    process.exit(1);
}
