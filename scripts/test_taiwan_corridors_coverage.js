
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
vm.runInContext("currentDayFilter = 'all'; buildDeparturesIndex();", sandbox);

const corridors = [
    { name: '北部生活圈 (基隆 ➔ 台北)', orig: '基隆', dest: '台北' },
    { name: '北桃通勤圈 (台北 ➔ 中壢)', orig: '台北', dest: '中壢' },
    { name: '竹苗通勤圈 (新竹 ➔ 苗栗)', orig: '新竹', dest: '苗栗' },
    { name: '台中都會區 (豐原 ➔ 新烏日)', orig: '豐原', dest: '新烏日' },
    { name: '彰雲嘉生活圈 (二水 ➔ 彰化)', orig: '二水', dest: '彰化' },
    { name: '嘉南生活圈 (嘉義 ➔ 台南)', orig: '嘉義', dest: '台南' },
    { name: '高屏生活圈 (高雄 ➔ 潮州)', orig: '高雄', dest: '潮州' },
    { name: '宜蘭線走廊 (八堵 ➔ 羅東)', orig: '八堵', dest: '羅東' },
    { name: '花東縱谷線 (花蓮 ➔ 台東)', orig: '花蓮', dest: '台東' },
    { name: '南迴幹線 (台東 ➔ 枋寮)', orig: '台東', dest: '枋寮' },
    { name: '集集觀光支線 (二水 ➔ 車埕)', orig: '二水', dest: '車埕' },
    { name: '內灣/六家線 (新竹 ➔ 內灣)', orig: '新竹', dest: '內灣' },
    { name: '平溪/深澳線 (瑞芳 ➔ 菁桐)', orig: '瑞芳', dest: '菁桐' },
    { name: '沙崙高鐵接駁 (台南 ➔ 沙崙)', orig: '台南', dest: '沙崙' }
];

console.log('================================================================');
console.log('全台 14 大核心走廊與支線方案覆蓋率檢驗 (Taiwan Corridors Audit)');
console.log('================================================================');

corridors.forEach(c => {
    const routes = sandbox.planRoutes(c.orig, c.dest, 0, '');
    const direct = routes.filter(r => r.transfers === 0).length;
    console.log(`• ${c.name.padEnd(26, ' ')} : ${routes.length} 方案 (直達 ${direct} 班)`);
});
console.log('================================================================');
