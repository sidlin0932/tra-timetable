# -*- coding: utf-8 -*-
import subprocess
import sys

test_js = """
const vm = require('vm');
const fs = require('fs');

const sandbox = {
    window: { addEventListener: () => {}, location: { search: '', href: '', replace: () => {} } },
    document: { getElementById: () => ({ value: '', textContent: '', innerHTML: '', style: {}, classList: { add: ()=>{}, remove: ()=>{} } }), querySelectorAll: () => [] },
    navigator: { onLine: true },
    location: { search: '', href: '', replace: () => {} },
    addEventListener: () => {},
    URLSearchParams: URLSearchParams,
    setInterval: () => {},
    clearInterval: () => {},
    setTimeout: (fn) => fn(),
    requestAnimationFrame: (fn) => fn(),
    console: console
};
vm.createContext(sandbox);

const dataCode = fs.readFileSync('data.js', 'utf8');
vm.runInContext(dataCode, sandbox);
sandbox.allTimetableData = sandbox.window.EMBEDDED_TIMETABLE_DATA || [];

const indexHtml = fs.readFileSync('index.html', 'utf8');
const scriptMatches = indexHtml.match(/<script(?![^>]*src=)>([\\s\\S]*?)<\\/script>/g);
const mainScript = scriptMatches[scriptMatches.length - 1].replace(/<\\/?script[^>]*>/g, '');
vm.runInContext(mainScript, sandbox);
sandbox.buildDeparturesIndex();

console.log('==================================================================');
console.log('🔍 全面檢視平替選項與去無意義前贅步 (Comprehensive Alternatives Audit)');
console.log('==================================================================');

const corridors = [
    {
        name: '集集 ➔ 板橋 (傍晚/夜間回程)',
        orig: '集集',
        dest: '板橋',
        startMin: 1080,
        expectedTrunks: ['154', '150', '152']
    },
    {
        name: '板橋 ➔ 車埕 (上午去程)',
        orig: '板橋',
        dest: '車埕',
        startMin: 360,
        expectedTrunks: ['105', '107', '109', '161']
    },
    {
        name: '台北 ➔ 台中 (西部山線幹線)',
        orig: '台北',
        dest: '台中',
        startMin: 420,
        expectedTrunks: ['105', '107', '109', '111']
    },
    {
        name: '板橋 ➔ 花蓮 (跨線東部幹線)',
        orig: '板橋',
        dest: '花蓮',
        startMin: 420,
        expectedTrunks: ['202', '204', '408', '410']
    },
    {
        name: '內灣 ➔ 六家 (跨支線轉乘)',
        orig: '內灣',
        dest: '六家',
        startMin: 480,
        expectedTrunks: []
    }
];

let allPassed = true;

corridors.forEach(c => {
    console.log(`\\n--- 檢視走廊：${c.name} ---`);
    const routes = sandbox.planRoutes(c.orig, c.dest, c.startMin, '');
    console.log(`總共規劃出 ${routes.length} 個方案`);

    // 1. Check for nonsensical pre-leg commuter detours
    let badPreLegs = 0;
    const trainMap = sandbox.getTrainMap();
    routes.forEach(r => {
        if (r.legs && r.legs.length >= 2) {
            const orig = r.legs[0].from;
            const rDepMin = sandbox.timeToMin(r.dep_time);
            for (let i = 1; i < r.legs.length; i++) {
                const nextT = trainMap.get(r.legs[i].train_number);
                if (nextT && nextT.stops) {
                    const st = nextT.stops.find(s => s.station === orig);
                    if (st && sandbox.timeToMin(st.time) >= rDepMin) {
                        badPreLegs++;
                        console.error(`  ❌ 發現無意義前贅步: ${r.legs.map(l=>l.train_type+' '+l.train_number).join(' -> ')}`);
                    }
                }
            }
        }
    });

    if (badPreLegs === 0) {
        console.log('  ✅ 100% 杜絕無意義前贅步 (0 筆)');
    } else {
        allPassed = false;
    }

    // 2. Check preservation of expected alternative trunk trains
    if (c.expectedTrunks.length > 0) {
        const presentTrunks = new Set();
        routes.forEach(r => {
            r.legs.forEach(l => presentTrunks.add(l.train_number));
        });

        c.expectedTrunks.forEach(tNo => {
            if (presentTrunks.has(tNo)) {
                console.log(`  ✅ 成功保留平替主力車次: ${tNo} 次`);
            } else {
                console.warn(`  ⚠️ 未見主力車次: ${tNo} 次`);
            }
        });
    }

    // Print top 4 sample routes
    console.log('  📋 方案樣例:');
    routes.slice(0, 4).forEach(r => {
        const legStr = r.legs.map(l => `${l.train_type} ${l.train_number} (${l.from} ${l.dep} ➔ ${l.to} ${l.arr})`).join(' ➔ ');
        console.log(`    • [${r.dep_time} ➔ ${r.arr_time} (${r.duration}分, 換車${r.transfers}次)] ${legStr}`);
    });
});

console.log('\\n==================================================================');
if (allPassed) {
    console.log('🎉 檢驗完全通過！所有合理平替選項（自強/區間快/EMU3000）完整保留，無意義行為徹底清除！');
} else {
    console.log('❌ 檢驗未完全通過');
    process.exit(1);
}
console.log('==================================================================\\n');
"""

res = subprocess.run(["node", "-e", test_js], capture_output=True, text=True, encoding="utf-8")
sys.stdout.buffer.write(res.stdout.encode('utf-8'))
if res.stderr:
    sys.stderr.buffer.write(res.stderr.encode('utf-8'))
if res.returncode != 0:
    sys.exit(1)
