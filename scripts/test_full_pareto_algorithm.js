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

// Let's implement full Pareto dominance function
function pruneStrictlyDominated(routes) {
    if (!routes || routes.length <= 1) return routes || [];

    const parseMin = (tStr) => {
        if (!tStr || !tStr.includes(':')) return 0;
        const [h, m] = tStr.split(':').map(Number);
        return h * 60 + m;
    };

    const getNormArr = (dep, arr) => (arr < dep ? arr + 1440 : arr);

    const mapped = routes.map(r => {
        const dMin = parseMin(r.dep_time);
        const aMin = parseMin(r.arr_time);
        return {
            route: r,
            depMin: dMin,
            arrMin: aMin,
            normArr: getNormArr(dMin, aMin),
            transfers: r.transfers || 0
        };
    });

    const nonDominated = [];
    for (let i = 0; i < mapped.length; i++) {
        const a = mapped[i];
        let isDominated = false;

        for (let j = 0; j < mapped.length; j++) {
            if (i === j) continue;
            const b = mapped[j];

            // b dominates a if:
            // 1. b departs at or after a (d_b >= d_a)
            // 2. b arrives at or before a (a_b <= a_a)
            // 3. b has fewer or equal transfers (t_b <= t_a)
            // 4. b is strictly better in at least one attribute
            if (b.depMin >= a.depMin && b.normArr <= a.normArr && b.transfers <= a.transfers) {
                if (b.depMin > a.depMin || b.normArr < a.normArr || b.transfers < a.transfers) {
                    isDominated = true;
                    break;
                } else if (i > j) {
                    // Duplicate identical route, keep first
                    isDominated = true;
                    break;
                }
            }
        }

        if (!isDominated) {
            nonDominated.push(a.route);
        }
    }

    return nonDominated;
}

// Test with 板橋 -> 宜蘭
console.log('--- Testing 板橋 -> 宜蘭 from 16:55 ---');
const rawRoutes = ctx.planRoutes('板橋', '宜蘭', 1015);
console.log(`Initial planRoutes count: ${rawRoutes.length}`);

const strictlyPruned = pruneStrictlyDominated(rawRoutes);
console.log(`After Strict Pareto Pruning count: ${strictlyPruned.length}`);

strictlyPruned.forEach((r, idx) => {
    console.log(`  #${idx+1} ${r.dep_time} -> ${r.arr_time} (${r.duration}m, 轉乘${r.transfers}次 ${r.transfer_stations.length ? 'via ' + r.transfer_stations.join(',') : '直達'}) [${r.legs.map(l=>l.train_type + ' ' + l.train_number).join(' -> ')}]`);
});

// Test with 社頭 -> 百福
console.log('\n--- Testing 社頭 -> 百福 from 06:00 ---');
const sbRoutes = ctx.planRoutes('社頭', '百福', 360);
console.log(`Initial planRoutes count: ${sbRoutes.length}`);
const sbPruned = pruneStrictlyDominated(sbRoutes);
console.log(`After Strict Pareto Pruning count: ${sbPruned.length}`);
sbPruned.slice(0, 5).forEach((r, idx) => {
    console.log(`  #${idx+1} ${r.dep_time} -> ${r.arr_time} (${r.duration}m, 轉乘${r.transfers}次 ${r.transfer_stations.length ? 'via ' + r.transfer_stations.join(',') : '直達'}) [${r.legs.map(l=>l.train_type + ' ' + l.train_number).join(' -> ')}]`);
});
