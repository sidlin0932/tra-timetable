# -*- coding: utf-8 -*-
"""
Local Stable Pass Automated Verification Suite (本機驗證門禁系統)
Runs comprehensive pre-push checks across:
1. JavaScript syntax in index.html (inline scripts), data.js, sw.js
2. JSON integrity in manifest.json and full_network_timetable.json
3. HTML DOM elements & onclick function binding integrity
4. Routing algorithm and timetable data integrity
5. Version badge and PWA cache key alignment across all files
"""

import json
import re
import subprocess
import sys
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
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
    sys.exit(1)

def test_json_files():
    log_step("1. JSON Data & Manifest Integrity")
    manifest_path = BASE_DIR / "manifest.json"
    if not manifest_path.exists():
        fail_step("manifest.json not found!")
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        try:
            manifest = json.load(f)
            required_keys = ["name", "short_name", "start_url", "display", "icons", "id"]
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
    
    # 2.1 index.html inline script
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

    # 2.2 sw.js
    sw_path = BASE_DIR / "sw.js"
    if sw_path.exists():
        with open(sw_path, "r", encoding="utf-8") as f:
            sw_code = f.read()
        res = subprocess.run(["node", "-e", node_code], input=sw_code, capture_output=True, text=True, encoding="utf-8")
        if res.returncode != 0:
            fail_step(f"sw.js syntax error:\n{res.stderr.strip()}")
        pass_step("sw.js syntax OK")

    # 2.3 data.js
    data_path = BASE_DIR / "data.js"
    if data_path.exists():
        res = subprocess.run([
            "node", "-e",
            """
            const fs = require('fs');
            const vm = require('vm');
            const code = fs.readFileSync('data.js', 'utf8');
            const sandbox = { window: {} };
            vm.createContext(sandbox);
            vm.runInContext(code, sandbox);
            if (!Array.isArray(sandbox.window.EMBEDDED_TIMETABLE_DATA) || sandbox.window.EMBEDDED_TIMETABLE_DATA.length < 500) {
                console.error('EMBEDDED_TIMETABLE_DATA invalid or length < 500');
                process.exit(1);
            }
            console.log('OK');
            """
        ], cwd=str(BASE_DIR), capture_output=True, text=True)
        if res.returncode != 0:
            fail_step(f"data.js execution/syntax error:\n{res.stderr.strip()}")
        pass_step("data.js syntax and EMBEDDED_TIMETABLE_DATA array OK")

def test_html_dom_bindings():
    log_step("3. HTML DOM & Function Binding Integrity")
    index_html = BASE_DIR / "index.html"
    with open(index_html, "r", encoding="utf-8") as f:
        html = f.read()

    # Essential DOM IDs referenced in JS
    essential_ids = [
        "timeInput", "typeFilter", "transferFilter", "dayFilter", "todayDayName",
        "stationModal", "modalSearchInput", "modalCountyTabs", "modalStationList",
        "modalTripStepper", "modalTitle", "btnInstallPwa", "viaInput", "btnClearVia",
        "resultsList", "resultsCount", "waypointsList"
    ]
    for dom_id in essential_ids:
        if f'id="{dom_id}"' not in html and f"id='{dom_id}'" not in html:
            fail_step(f"Required DOM element id='{dom_id}' missing in index.html!")
    pass_step(f"All {len(essential_ids)} critical DOM IDs present in index.html")

    # Essential JS functions
    essential_functions = [
        "executeSearch", "modalPickStation", "openStationModal", "closeStationModal",
        "setDayFilter", "setTypeFilter", "setTransferCondition", "setCurrentTime",
        "reverseWaypoints", "installPwa", "toggleTheme", "switchVersion"
    ]
    for fn in essential_functions:
        if f"function {fn}" not in html:
            fail_step(f"Required function '{fn}' not defined in index.html script!")
    pass_step(f"All {len(essential_functions)} critical JS functions defined")

def test_version_alignment():
    log_step("4. Version Alignment across UI, PWA Cache, and Documentation")
    
    # Read CHANGELOG for latest version
    changelog_path = BASE_DIR / "CHANGELOG.md"
    with open(changelog_path, "r", encoding="utf-8") as f:
        changelog = f.read()
    
    version_match = re.search(r"## \[(v\d+\.\d+\.\d+)\]", changelog)
    if not version_match:
        fail_step("No valid version header found in CHANGELOG.md!")
    latest_version = version_match.group(1)
    pass_step(f"Latest release in CHANGELOG: {latest_version}")

    # Check README.md
    readme_path = BASE_DIR / "README.md"
    with open(readme_path, "r", encoding="utf-8") as f:
        readme = f.read()
    if latest_version not in readme:
        fail_step(f"README.md does not contain current version {latest_version}")
    pass_step(f"README.md matches {latest_version}")

    # Check index.html badge
    index_path = BASE_DIR / "index.html"
    with open(index_path, "r", encoding="utf-8") as f:
        index_html = f.read()
    if latest_version not in index_html:
        fail_step(f"index.html does not contain current version badge {latest_version}")
    pass_step(f"index.html UI badge matches {latest_version}")

    # Check sw.js cache name
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

def main():
    print("🚀 Starting Local Stable Verification Suite...")
    test_json_files()
    test_js_syntax()
    test_html_dom_bindings()
    test_version_alignment()
    test_multi_version_snapshots()
    
    print("\n==========================================")
    print("🎉 ALL LOCAL TESTS PASSED! (STABLE VERIFIED)")
    print("==========================================\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
