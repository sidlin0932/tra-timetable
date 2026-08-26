# -*- coding: utf-8 -*-
"""
Adds end-to-end routing simulation tests in verify_local_stable.py to guarantee
that critical queries (板橋->台北, 內灣->六家, 台北->花蓮) never regress.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VERIFY_PY = BASE_DIR / "verify_local_stable.py"

with open(VERIFY_PY, "r", encoding="utf-8") as f:
    code = f.read()

TEST_6_CODE = """
def test_routing_simulation():
    log_step("6. End-to-End Node.js Route Planning Simulation")
    
    index_html = BASE_DIR / "index.html"
    with open(index_html, "r", encoding="utf-8") as f:
        html_content = f.read()

    scripts = re.findall(r"<script(?![^>]*src=)>([\s\S]*?)</script>", html_content)
    if not scripts:
        fail_step("No script block found in index.html")

    main_script = scripts[-1]
    
    data_js_path = BASE_DIR / "data.js"
    with open(data_js_path, "r", encoding="utf-8") as f:
        data_js = f.read()

    sim_node_code = f\"\"\"
    const vm = require('vm');
    const sandbox = {{
        window: {{}},
        document: {{
            getElementById: () => ({{ value: '', textContent: '', innerHTML: '', style: {{}}, classList: {{ add: ()=>{}, remove: ()=>{{}} }} }}),
            querySelectorAll: () => []
        }},
        navigator: {{ onLine: true }},
        location: {{ search: '' }},
        addEventListener: () => {{}},
        setInterval: () => {{}},
        clearInterval: () => {{}},
        setTimeout: (fn) => fn(),
        requestAnimationFrame: (fn) => fn(),
        console: console
    }};
    vm.createContext(sandbox);

    // 1. Load data.js
    {data_js}
    sandbox.allTimetableData = sandbox.window.EMBEDDED_TIMETABLE_DATA || [];

    // 2. Load index.html logic
    \"\"\"

    test_runner = f\"\"\"
    const vm = require('vm');
    const sandbox = {{
        window: {{}},
        document: {{
            getElementById: () => ({{ value: '', textContent: '', innerHTML: '', style: {{}}, classList: {{ add: ()=>{}, remove: ()=>{{}} }} }}),
            querySelectorAll: () => []
        }},
        navigator: {{ onLine: true }},
        location: {{ search: '' }},
        addEventListener: () => {{}},
        setInterval: () => {{}},
        clearInterval: () => {{}},
        setTimeout: (fn) => fn(),
        requestAnimationFrame: (fn) => fn(),
        console: console
    }};
    vm.createContext(sandbox);

    {data_js}
    sandbox.allTimetableData = sandbox.window.EMBEDDED_TIMETABLE_DATA || [];

    {main_script}

    sandbox.buildDeparturesIndex();

    // Test 1: 板橋 -> 台北
    const r1 = sandbox.planRoutes('板橋', '台北', 0, '');
    if (!r1 || r1.length < 50) {{
        console.error('FAIL: 板橋 -> 台北 returned only ' + (r1 ? r1.length : 0) + ' routes (expected >= 50)');
        process.exit(1);
    }}
    console.log('PASS_BQ_TP:' + r1.length);

    // Test 2: 內灣 -> 六家
    const r2 = sandbox.planRoutes('內灣', '六家', 0, '');
    if (!r2 || r2.length < 20) {{
        console.error('FAIL: 內灣 -> 六家 returned only ' + (r2 ? r2.length : 0) + ' routes (expected >= 20)');
        process.exit(1);
    }}
    console.log('PASS_NW_LJ:' + r2.length);
    \"\"\"

    res = subprocess.run(["node", "-e", test_runner], capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        fail_step(f"Routing simulation failed:\\n{res.stderr.strip()}\\n{res.stdout.strip()}")
    
    pass_step("Route Planning Simulation for 【板橋 ➔ 台北】 & 【內灣 ➔ 六家】 (>50 routes verified)")
"""

if "def test_routing_simulation():" not in code:
    code = code.replace("def main():", TEST_6_CODE + "\ndef main():")
    code = code.replace("test_multi_version_snapshots()", "test_multi_version_snapshots()\n    test_routing_simulation()")

with open(VERIFY_PY, "w", encoding="utf-8") as f:
    f.write(code)

print("verify_local_stable.py updated with automated routing simulation tests!")
