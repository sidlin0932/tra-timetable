import subprocess

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

// Test Multi-Stop: 社頭 -> 百福 -> 暖暖
const wps = [
    { station: '社頭', minStay: 0 },
    { station: '百福', minStay: 0 },
    { station: '暖暖', minStay: 0 }
];

console.log('Testing planMultiStopRoutes...');
"""

res = subprocess.run(["node", "-e", test_js], capture_output=True, text=True, encoding="utf-8")
print("Output:", res.stdout)
print("Stderr:", res.stderr)
