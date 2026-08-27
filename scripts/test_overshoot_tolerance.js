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
sandbox.buildDeparturesIndex();

sandbox.isStationOvershooting = function(orig, dest, mid) {
    if (!orig || !dest || !mid || mid === orig || mid === dest) return false;
    const TERMINAL_HUBS = new Set(['七堵', '八堵', '基隆', '新左營', '高雄', '二水', '竹中', '瑞芳']);
    
    for (let cIdx = 0; cIdx < sandbox.CORRIDOR_MAPS.length; cIdx++) {
        const corridor = sandbox.CORRIDOR_MAPS[cIdx];
        const iOrig = corridor.indexOf(orig);
        const iDest = corridor.indexOf(dest);
        const iMid = corridor.indexOf(mid);
        if (iOrig !== -1 && iDest !== -1 && iMid !== -1) {
            const minP = Math.min(iOrig, iDest);
            const maxP = Math.max(iOrig, iDest);
            if (iMid < minP || iMid > maxP) {
                if (TERMINAL_HUBS.has(mid) && Math.abs(iMid - iDest) <= 2) {
                    continue;
                }
                return true;
            }
        }
    }
    return false;
};

const r1 = sandbox.planRoutes('社頭', '百福', 360, '');
const r2 = sandbox.planRoutes('台北', '鶯歌', 360, '');
console.log('Shetou -> Baifu routes:', r1.length);
console.log('Taipei -> Yingge routes:', r2.length);

const wp = [ { station: '社頭', minStay: 0 }, { station: '百福', minStay: 30 }, { station: '暖暖', minStay: 0 } ];
const rMulti = sandbox.planMultiStopRoutes(wp, 360);
console.log('Shetou -> Baifu -> Nuannuan multi-stop routes:', rMulti.length);
