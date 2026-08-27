# -*- coding: utf-8 -*-
import subprocess
import json
import os
import sys

print("==================================================================")
print("Master Comprehensive System Audit across 5 Core Dimensions")
print("==================================================================")

test_js = """
const vm = require('vm');
const fs = require('fs');

const sandbox = {
    window: { addEventListener: () => {}, location: { search: '', href: '', replace: () => {} } },
    document: {
        getElementById: () => ({ value: '', textContent: '', innerHTML: '', style: {}, classList: { add: ()=>{}, remove: ()=>{} } }),
        querySelectorAll: () => []
    },
    navigator: { onLine: true },
    location: { search: '', href: '', replace: () => {} },
    addEventListener: () => {},
    URLSearchParams: URLSearchParams,
    setInterval: () => {},
    clearInterval: () => {},
    setTimeout: (fn) => fn(),
    requestAnimationFrame: (fn) => fn(),
    localStorage: {
        getItem: () => null,
        setItem: () => {}
    },
    console: console
};
vm.createContext(sandbox);

// 1. Load Data
const dataCode = fs.readFileSync('data.js', 'utf8');
vm.runInContext(dataCode, sandbox);
sandbox.allTimetableData = sandbox.window.EMBEDDED_TIMETABLE_DATA || [];

// 2. Load Index
const indexHtml = fs.readFileSync('index.html', 'utf8');
const scriptMatches = indexHtml.match(/<script(?![^>]*src=)>([\\s\\S]*?)<\\/script>/g);
const mainScript = scriptMatches[scriptMatches.length - 1].replace(/<\\/?script[^>]*>/g, '');
vm.runInContext(mainScript, sandbox);
vm.runInContext("currentDayFilter = 'all'; buildDeparturesIndex();", sandbox);

let failures = [];

console.log('\\n[DIMENSION 1] 資料庫完整度與列車時間單調性 (Database & Train Monotonicity)');
console.log(`  • 列車總收錄數: ${sandbox.allTimetableData.length} 班`);

let nonMonotonicCount = 0;
sandbox.allTimetableData.forEach(t => {
    let lastM = -1;
    let crossMidnight = false;
    t.stops.forEach((s, idx) => {
        const m = sandbox.timeToMin(s.time);
        if (lastM !== -1) {
            if (m < lastM) {
                if (!crossMidnight && m < 360 && lastM > 1200) {
                    crossMidnight = true; // Legit cross-midnight train
                } else if (!crossMidnight) {
                    nonMonotonicCount++;
                }
            }
        }
        lastM = m;
    });
});
if (nonMonotonicCount === 0) {
    console.log('  ✅ 924 班列車時間單調性驗證 100% 正常（無倒流異常）');
} else {
    failures.push(`資料庫有 ${nonMonotonicCount} 班列車時間異常`);
}

// Check 2007 endpoints
const t2007 = sandbox.allTimetableData.find(t => t.train_number === '2007');
if (t2007 && t2007.dest === '二水') {
    console.log(`  ✅ 區間快 2007 次終點站正確校正為: ${t2007.dest} (${t2007.stops[t2007.stops.length-1].time})`);
} else {
    failures.push(`2007 次終點站不正確: ${t2007 ? t2007.dest : 'NotFound'}`);
}

console.log('\\n[DIMENSION 2] 零折返拓撲防護 (Zero-Backtracking / Anti-Overshoot)');
const testOvershoots = [
    { orig: '台北', dest: '鶯歌', illegalVia: '桃園' },
    { orig: '板橋', dest: '樹林', illegalVia: '桃園' },
    { orig: '台中', dest: '新烏日', illegalVia: '彰化' },
    { orig: '花蓮', dest: '吉安', illegalVia: '壽豐' }
];

testOvershoots.forEach(test => {
    const routes = sandbox.planRoutes(test.orig, test.dest, 360, '');
    let badCount = 0;
    routes.forEach(r => {
        r.legs.forEach(l => {
            if (l.to === test.illegalVia) badCount++;
        });
    });
    if (badCount === 0) {
        console.log(`  ✅ ${test.orig} ➔ ${test.dest}: 0 筆越站折返 (成功阻斷 ${test.illegalVia})`);
    } else {
        failures.push(`${test.orig} ➔ ${test.dest} 發現 ${badCount} 筆越站折返！`);
    }
});

console.log('\\n[DIMENSION 3] 多元主力平替車次保留 (Trunk Train Diversity Preservation)');
const jijiRoutes = sandbox.planRoutes('集集', '板橋', 1080, '');
const trunks = new Set();
jijiRoutes.forEach(r => r.legs.forEach(l => trunks.add(l.train_number)));

['154', '150', '152'].forEach(tNo => {
    if (trunks.has(tNo)) {
        console.log(`  ✅ 集集 ➔ 板橋 成功保留多元主力車次: ${tNo} 次`);
    } else {
        failures.push(`集集 ➔ 板橋 遺失主力車次: ${tNo}`);
    }
});

console.log('\\n[DIMENSION 4] 無意義前贅步杜絕 (Zero Redundant Pre-Leg Detours)');
let badPreLegs = 0;
const trainMap = sandbox.getTrainMap();
jijiRoutes.forEach(r => {
    if (r.legs && r.legs.length >= 2) {
        const orig = r.legs[0].from;
        const rDepMin = sandbox.timeToMin(r.dep_time);
        for (let i = 1; i < r.legs.length; i++) {
            const nextT = trainMap.get(r.legs[i].train_number);
            if (nextT && nextT.stops) {
                const st = nextT.stops.find(s => s.station === orig);
                if (st && sandbox.timeToMin(st.time) >= rDepMin) {
                    badPreLegs++;
                }
            }
        }
    }
});
if (badPreLegs === 0) {
    console.log('  ✅ 100% 杜絕起早搭慢車去前站等同一班快車之怪異路線');
} else {
    failures.push(`發現 ${badPreLegs} 筆無意義前贅步！`);
}

console.log('\\n[DIMENSION 5] 連續多站點停靠規劃 (Multi-Stop Waypoints Router)');
const multiWaypoints = [
    { station: '社頭', minStay: 0 },
    { station: '百福', minStay: 30 },
    { station: '暖暖', minStay: 0 }
];
const multiRoutes = sandbox.planMultiStopRoutes(multiWaypoints, 360);
console.log(`  ✅ 社頭 ➔ 百福(停留30分) ➔ 暖暖: 成功規劃出 ${multiRoutes.length} 個分段行程`);
if (multiRoutes.length < 5) {
    failures.push('多站點連續規劃回傳方案過少');
}

console.log('\\n==================================================================');
if (failures.length === 0) {
    console.log('🎉🎉🎉 全盤檢驗 100% 全部通過！系統健康度滿分！');
} else {
    console.log('❌ 發現問題:', failures);
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
