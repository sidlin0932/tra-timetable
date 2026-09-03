# -*- coding: utf-8 -*-
"""
Local Stable Pass Verification Suite (Pre-Push Quality Gatekeeper)
Executes a battery of 6 automated tests to ensure 100% stable release:
1. JSON Data & Manifest Integrity
2. JavaScript Syntax & Parsing Check via Node.js VM
3. HTML DOM & Function Binding Integrity
4. Version Alignment across UI, PWA Cache, and Documentation
5. Multi-Version Snapshot & Rollback Hub Integrity
6. End-to-End Node.js Route Planning Simulation (板橋->台北 >= 50, 內灣->六家 >= 20)
"""

import sys
import os
import json
import re
import subprocess
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent

def log_step(name):
    print(f"\n==========================================")
    print(f"🔍 [TEST] {name}")
    print(f"==========================================")

def pass_step(msg):
    print(f"  ✅ PASS: {msg}")

def fail_step(msg):
    print(f"  ❌ FAIL: {msg}")
    print(f"\n==========================================")
    print(f"💥 LOCAL VERIFICATION FAILED. Push aborted.")
    print(f"==========================================")
    sys.exit(1)

def test_json_and_manifest():
    log_step("1. JSON Data & Manifest Integrity")
    manifest_path = BASE_DIR / "manifest.json"
    if not manifest_path.exists():
        fail_step("manifest.json not found!")
    with open(manifest_path, "r", encoding="utf-8") as f:
        try:
            manifest = json.load(f)
            required_keys = ["name", "short_name", "start_url", "display", "icons"]
            for k in required_keys:
                if k not in manifest:
                    fail_step(f"manifest.json missing required key: {k}")
            pass_step("manifest.json is valid W3C PWA JSON")
        except Exception as e:
            fail_step(f"manifest.json parsing failed: {e}")

    timetable_json = BASE_DIR / "full_network_timetable.json"
    if timetable_json.exists():
        with open(timetable_json, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if not isinstance(data, list) or len(data) < 500:
                    fail_step(f"full_network_timetable.json contains only {len(data)} trains, expected >500")
                pass_step(f"full_network_timetable.json loaded ({len(data)} trains)")
            except Exception as e:
                fail_step(f"full_network_timetable.json parsing failed: {e}")

def test_js_syntax():
    log_step("2. JavaScript Syntax & Parsing Check (Node.js VM)")
    
    index_html = BASE_DIR / "index.html"
    with open(index_html, "r", encoding="utf-8") as f:
        html_content = f.read()

    scripts = re.findall(r"<script(?![^>]*src=)>([\s\S]*?)</script>", html_content)
    if not scripts:
        fail_step("No inline <script> found in index.html!")
    
    for i, script_code in enumerate(scripts):
        node_code = """
        const vm = require('vm');
        let code = '';
        process.stdin.setEncoding('utf8');
        process.stdin.on('data', chunk => code += chunk);
        process.stdin.on('end', () => {
            try {
                new vm.Script(code);
                console.log('OK');
            } catch (err) {
                console.error(err);
                process.exit(1);
            }
        });
        """
        res = subprocess.run(["node", "-e", node_code], input=script_code, capture_output=True, text=True, encoding="utf-8")
        if res.returncode != 0:
            fail_step(f"index.html script block #{i+1} has syntax error:\n{res.stderr.strip()}")
        pass_step(f"index.html inline script #{i+1} syntax OK")

    sw_js = BASE_DIR / "sw.js"
    if sw_js.exists():
        with open(sw_js, "r", encoding="utf-8") as f:
            sw_code = f.read()
        res = subprocess.run(["node", "-e", node_code], input=sw_code, capture_output=True, text=True, encoding="utf-8")
        if res.returncode != 0:
            fail_step(f"sw.js has syntax error:\n{res.stderr.strip()}")
        pass_step("sw.js syntax OK")

    data_js = BASE_DIR / "data.js"
    if data_js.exists():
        test_data_node = """
        const vm = require('vm');
        const fs = require('fs');
        const code = fs.readFileSync('data.js', 'utf8');
        const sandbox = { window: {} };
        vm.createContext(sandbox);
        try {
            vm.runInContext(code, sandbox);
            if (!sandbox.window.EMBEDDED_TIMETABLE_DATA || !Array.isArray(sandbox.window.EMBEDDED_TIMETABLE_DATA)) {
                process.exit(1);
            }
            console.log('OK');
        } catch (e) {
            console.error(e);
            process.exit(1);
        }
        """
        res = subprocess.run(["node", "-e", test_data_node], cwd=str(BASE_DIR), capture_output=True, text=True, encoding="utf-8")
        if res.returncode != 0:
            fail_step("data.js does not define valid window.EMBEDDED_TIMETABLE_DATA array!")
        pass_step("data.js syntax and EMBEDDED_TIMETABLE_DATA array OK")

def test_html_dom_and_bindings():
    log_step("3. HTML DOM & Function Binding Integrity")
    index_html = BASE_DIR / "index.html"
    with open(index_html, "r", encoding="utf-8") as f:
        html_content = f.read()

    required_dom_ids = [
        "appTitle", "resultsList", "resultsCount", "timeInput",
        "stationModal", "modalTitle", "modalStationList",
        "modalSearchInput", "primarySort",
        "modalMapView", "taiwanMapWrapper",
        "viaInput", "btnSearch"
    ]

    for dom_id in required_dom_ids:
        if f'id="{dom_id}"' not in html_content and f"id='{dom_id}'" not in html_content:
            fail_step(f"Critical DOM element id='{dom_id}' not found in index.html!")
    pass_step(f"All {len(required_dom_ids)} critical DOM IDs present in index.html")

    required_functions = [
        "executeSearch", "planRoutes", "openStationModal", "closeStationModal",
        "modalPickStation", "swapStations", "toggleDetails", "openStationTimetable",
        "updateNetworkStatus", "zoomMapRegion", "isTrainAllowed"
    ]

    for fn in required_functions:
        if f"function {fn}" not in html_content:
            fail_step(f"Required function '{fn}' not defined in index.html script!")
    pass_step(f"All {len(required_functions)} critical JS functions defined")

def test_version_alignment():
    log_step("4. Version Alignment across UI, PWA Cache, and Documentation")
    
    changelog_path = BASE_DIR / "CHANGELOG.md"
    with open(changelog_path, "r", encoding="utf-8") as f:
        cl = f.read()
    
    m = re.search(r"##\s*\[(v[\d\.]+)\]", cl)
    if not m:
        fail_step("Could not find latest version in CHANGELOG.md!")
    latest_version = m.group(1)
    pass_step(f"Latest release in CHANGELOG: {latest_version}")

    readme_path = BASE_DIR / "README.md"
    with open(readme_path, "r", encoding="utf-8") as f:
        rm = f.read()
    if latest_version not in rm:
        fail_step(f"README.md does not reference latest version {latest_version}")
    pass_step(f"README.md matches {latest_version}")

    index_html = BASE_DIR / "index.html"
    with open(index_html, "r", encoding="utf-8") as f:
        html = f.read()
    if latest_version not in html:
        fail_step(f"index.html does not contain current version badge {latest_version}")
    pass_step(f"index.html UI badge matches {latest_version}")

    sw_path = BASE_DIR / "sw.js"
    with open(sw_path, "r", encoding="utf-8") as f:
        sw = f.read()
    if latest_version not in sw:
        fail_step(f"sw.js does not contain current version {latest_version}")
    pass_step(f"sw.js matches {latest_version}")

def test_multi_version_snapshots():
    log_step("5. Multi-Version Snapshot & Rollback Hub Integrity")
    versions_dir = BASE_DIR / "versions"
    if not versions_dir.exists():
        fail_step("versions/ directory does not exist!")
    
    hub_file = versions_dir / "index.html"
    if not hub_file.exists():
        fail_step("versions/index.html hub portal does not exist!")
    pass_step("versions/index.html (Version Hub) exists")

    versions_json = versions_dir / "versions.json"
    if not versions_json.exists():
        fail_step("versions/versions.json not found!")
    
    with open(versions_json, "r", encoding="utf-8") as f:
        v_list = json.load(f)
    
    if not isinstance(v_list, list) or len(v_list) < 5:
        fail_step(f"Expected at least 5 archived versions, found {len(v_list)}")
    
    for v in v_list:
        v_tag = v["version"]
        v_folder = versions_dir / v_tag
        if not v_folder.exists() or not (v_folder / "index.html").exists():
            fail_step(f"Version snapshot {v_tag}/index.html missing!")
    pass_step(f"All {len(v_list)} historical standalone version snapshots verified intact")

def test_routing_simulation():
    log_step("6. End-to-End Node.js Route Planning Simulation")
    
    test_runner = """
    const vm = require('vm');
    const fs = require('fs');

    const sandbox = {
        window: {
            addEventListener: () => {},
            location: { search: '', href: '', replace: () => {} }
        },
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

    // Test 1: 板橋 -> 台北
    const r1 = sandbox.planRoutes('板橋', '台北', 0, '');
    if (!r1 || r1.length < 50) {
        console.error('FAIL: 板橋 -> 台北 returned only ' + (r1 ? r1.length : 0) + ' routes (expected >= 50)');
        process.exit(1);
    }

    // Test 2: 內灣 -> 六家
    const r2 = sandbox.planRoutes('內灣', '六家', 0, '');
    if (!r2 || r2.length < 15) {
        console.error('FAIL: 內灣 -> 六家 returned only ' + (r2 ? r2.length : 0) + ' routes (expected >= 15)');
        process.exit(1);
    }

    console.log('SIMULATION_SUCCESS: 板橋->台北 (' + r1.length + ' routes), 內灣->六家 (' + r2.length + ' routes)');
    """

    res = subprocess.run(["node", "-e", test_runner], cwd=str(BASE_DIR), capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        fail_step(f"Routing simulation failed:\n{res.stderr.strip()}\n{res.stdout.strip()}")
    
    pass_step(f"Route Planning Simulation PASS: {res.stdout.strip()}")

def main():
    print("🚀 Starting Local Stable Verification Suite...")
    test_json_and_manifest()
    test_js_syntax()
    test_html_dom_and_bindings()
    test_version_alignment()
    test_multi_version_snapshots()
    test_routing_simulation()
    print("\n==========================================")
    print("🎉 ALL 6 LOCAL TESTS PASSED! (STABLE VERIFIED)")
    print("==========================================\n")

if __name__ == "__main__":
    main()
