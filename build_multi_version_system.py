# -*- coding: utf-8 -*-
"""
Multi-Version Archiver & Release System for TRA Timetable
Automates the creation and maintenance of historical version snapshots under versions/<version_tag>/
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VERSIONS_DIR = BASE_DIR / "versions"

# Fix Windows console UTF-8 output
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# List of key historical release commits mapped to version tags
HISTORICAL_COMMITS = [
    {"version": "v3.9.9", "commit": "HEAD",    "date": "2026-08-25", "desc": "發布獨立【極速極簡版 SuperLite】與雙版本一鍵切換"},
    {"version": "v3.9.8", "commit": "HEAD",    "date": "2026-08-25", "desc": "補齊 openStationModalForWaypoint 函式 ＆ 選站點擊 100% 恢復"},
    {"version": "v3.9.7", "commit": "HEAD",    "date": "2026-08-25", "desc": "完美修復按鈕點選失效 ＆ 全面接軌選站與輸入系統"},
    {"version": "v3.9.6", "commit": "HEAD",    "date": "2026-08-25", "desc": "即時快取更新 (Network-First) ＆ DOM 虛擬渲染 (解決卡頓)"},
    {"version": "v3.9.5", "commit": "HEAD",    "date": "2026-08-25", "desc": "完整選站互動修復 ＆ 真實 X/Y 列車進度條清晰呈現"},
    {"version": "v3.9.4", "commit": "HEAD",    "date": "2026-08-25", "desc": "介面 60 FPS 非同步零延遲排程 ＆ LRU 記憶體快取極速引擎"},
    {"version": "v3.9.3", "commit": "HEAD",    "date": "2026-08-25", "desc": "真實 X / Y 列車算路進度條 ＆ 枝葉剪枝極速路由引擎 (微秒直出)"},
    {"version": "v3.9.2", "commit": "321dfd6", "date": "2026-08-25", "desc": "手機優先 48px 觸控熱區、全島地圖 6 大分區縮放與頁尾現代化重構"},
    {"version": "v3.9.1", "commit": "37db8cb", "date": "2026-08-25", "desc": "內灣/六家線西行班次全量補齊 (69方案) & Modal 滾動條鎖死徹底修復"},
    {"version": "v3.9.0", "commit": "HEAD~5",  "date": "2026-08-25", "desc": "台灣鐵路全島互動式路線圖與點選連動選站系統"},
    {"version": "v3.8.15", "commit": "04b2084", "date": "2026-08-25", "desc": "深色主題車站時刻表字體對比度優化 (WCAG AAA 規範)"},
    {"version": "v3.8.14", "commit": "c10e6a8", "date": "2026-08-25", "desc": "100% 純離線保證架構 (啟用 ignoreSearch、導航保底攔截與字體優雅降級)"},
    {"version": "v3.8.13", "commit": "48a67d7", "date": "2026-08-25", "desc": "多版本隨時回退與切換架構 (支援導航列下拉選單、URL ?v= 參數與獨立快照封裝)"},
    {"version": "v3.8.12", "commit": "be674ef", "date": "2026-08-25", "desc": "修復 JS 語法崩潰阻斷 & 建立 Local Stable 本機門禁自動化測試"},
    {"version": "v3.8.11", "commit": "e7e4637", "date": "2026-08-25", "desc": "PWA 離線手機 App 化成功技術總結與 Manifest 語法優化"},
    {"version": "v3.8.10", "commit": "46f4464", "date": "2026-08-25", "desc": "W3C 標準 PWA App ID 與 Scope 升級"},
    {"version": "v3.8.9",  "commit": "e3e3f72", "date": "2026-08-25", "desc": "圖示與 Favicon 全面升級 (阻絕 GitHub 黑底預設圖示)"},
    {"version": "v3.8.8",  "commit": "6f2984b", "date": "2026-08-25", "desc": "Android WebAPK 專屬優化與 start_url 相對路徑規範"},
    {"version": "v3.8.7",  "commit": "53f35df", "date": "2026-08-25", "desc": "每次 Push 必跳 Patch（Patch-as-Build）快取即時失效政策"},
    {"version": "v3.8.6",  "commit": "c9c067e", "date": "2026-08-25", "desc": "車站與列車全日時刻表升級「到站時間」與「開車時間」雙時序欄位"},
    {"version": "v3.8.5",  "commit": "0e47998", "date": "2026-08-24", "desc": "全路網多中繼站智慧轉乘與極速記憶化引擎 (1,402 班車全收錄)"},
]

def extract_git_file(commit, file_path):
    cmd = ["git", "show", f"{commit}:{file_path}"]
    res = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True)
    if res.returncode == 0:
        return res.stdout
    return None

def build_versions():
    print(f"📦 Initializing Multi-Version Directory: {VERSIONS_DIR}")
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)

    # Copy shared icons
    for icon_name in ["icon-192.png", "icon-512.png"]:
        src_icon = BASE_DIR / icon_name
        if src_icon.exists():
            shutil.copy2(src_icon, VERSIONS_DIR / icon_name)

    manifest_data = []

    for item in HISTORICAL_COMMITS:
        v_tag = item["version"]
        commit = item["commit"]
        v_dir = VERSIONS_DIR / v_tag
        v_dir.mkdir(parents=True, exist_ok=True)
        print(f"  🔨 Building snapshot for {v_tag} (commit: {commit})...")

        # Copy icons to version folder
        for icon_name in ["icon-192.png", "icon-512.png"]:
            src_icon = BASE_DIR / icon_name
            if src_icon.exists():
                shutil.copy2(src_icon, v_dir / icon_name)

        if commit == "HEAD":
            shutil.copy2(BASE_DIR / "index.html", v_dir / "index.html")
            shutil.copy2(BASE_DIR / "data.js", v_dir / "data.js")
            shutil.copy2(BASE_DIR / "sw.js", v_dir / "sw.js")
            shutil.copy2(BASE_DIR / "manifest.json", v_dir / "manifest.json")
            print(f"    -> Copied directly from current workspace HEAD")
        else:
            # Extract index.html
            html_bytes = extract_git_file(commit, "index.html")
            if html_bytes:
                html_text = html_bytes.decode("utf-8", errors="ignore")
                if "alert('📱 提示：" in html_text and "\\n" not in html_text:
                    html_text = html_text.replace(
                        "alert('📱 提示：\n在 iPhone/iPad 請點擊 Safari 下方「分享」按鈕，選擇「加入主畫面」即可安裝為離線 App！\n在 Android/Chrome 請點擊右上角選單選擇「安裝應用程式」。');",
                        "alert('📱 提示：\\n在 iPhone/iPad 請點擊 Safari 下方「分享」按鈕，選擇「加入主畫面」即可安裝為離線 App！\\n在 Android/Chrome 請點擊右上角選單選擇「安裝應用程式」。');"
                    )
                with open(v_dir / "index.html", "w", encoding="utf-8") as f:
                    f.write(html_text)
                print(f"    -> index.html extracted ({len(html_text)} chars)")

            # Extract data.js
            data_bytes = extract_git_file(commit, "data.js")
            if data_bytes:
                with open(v_dir / "data.js", "wb") as f:
                    f.write(data_bytes)
                print(f"    -> data.js extracted ({len(data_bytes)} bytes)")
            else:
                shutil.copy2(BASE_DIR / "data.js", v_dir / "data.js")

            # Extract sw.js
            sw_bytes = extract_git_file(commit, "sw.js")
            if sw_bytes:
                with open(v_dir / "sw.js", "wb") as f:
                    f.write(sw_bytes)
            else:
                shutil.copy2(BASE_DIR / "sw.js", v_dir / "sw.js")

            # Extract manifest.json
            manifest_bytes = extract_git_file(commit, "manifest.json")
            if manifest_bytes:
                with open(v_dir / "manifest.json", "wb") as f:
                    f.write(manifest_bytes)
            else:
                shutil.copy2(BASE_DIR / "manifest.json", v_dir / "manifest.json")

        manifest_data.append(item)

    # Save versions.json
    with open(VERSIONS_DIR / "versions.json", "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, ensure_ascii=False, indent=2)
    print("  ✅ Created versions/versions.json")

    # Generate Version Hub index.html (Historical Portal)
    generate_hub_page(manifest_data)

def generate_hub_page(versions_list):
    hub_html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#0284c7">
    <title>台鐵時刻表系統 - 多版本歷史發布中心 (Version Archive Hub)</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700;900&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #0284c7;
            --primary-hover: #0369a1;
            --bg-page: #f8fafc;
            --bg-card: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border-color: #e2e8f0;
            --card-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.07), 0 2px 4px -2px rgb(0 0 0 / 0.05);
            --radius: 12px;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Noto Sans TC', -apple-system, sans-serif; }}
        body {{ background: var(--bg-page); color: var(--text-main); line-height: 1.6; padding: 30px 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 35px; }}
        .header h1 {{ font-size: 2rem; font-weight: 900; color: #0284c7; margin-bottom: 8px; }}
        .header p {{ color: var(--text-muted); font-size: 1rem; }}
        .btn-latest {{
            display: inline-flex; align-items: center; gap: 8px;
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            color: #fff; text-decoration: none; padding: 12px 24px; border-radius: 10px;
            font-weight: 700; margin-top: 18px; box-shadow: 0 4px 12px rgba(2,132,199,0.3);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .btn-latest:hover {{ transform: translateY(-2px); box-shadow: 0 6px 16px rgba(2,132,199,0.4); }}
        .version-list {{ display: flex; flex-direction: column; gap: 16px; }}
        .version-card {{
            background: var(--bg-card); border: 1px solid var(--border-color);
            border-radius: var(--radius); padding: 20px 24px; box-shadow: var(--card-shadow);
            display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;
            transition: all 0.2s ease;
        }}
        .version-card:hover {{ border-color: var(--primary); transform: translateY(-2px); }}
        .version-info {{ flex: 1; min-width: 260px; }}
        .version-badge {{
            display: inline-block; font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 0.95rem;
            background: #e0f2fe; color: #0284c7; padding: 3px 10px; border-radius: 8px; margin-bottom: 6px;
        }}
        .version-badge.latest {{ background: #10b981; color: #fff; }}
        .version-date {{ font-size: 0.85rem; color: var(--text-muted); margin-left: 8px; }}
        .version-desc {{ font-size: 0.95rem; color: var(--text-main); font-weight: 500; }}
        .version-actions {{ display: flex; gap: 10px; }}
        .btn-open {{
            display: inline-flex; align-items: center; gap: 6px;
            background: var(--primary); color: #fff; text-decoration: none; padding: 8px 18px;
            border-radius: 8px; font-weight: 700; font-size: 0.9rem; transition: background 0.2s;
        }}
        .btn-open:hover {{ background: var(--primary-hover); }}
        .footer {{ text-align: center; margin-top: 40px; color: var(--text-muted); font-size: 0.85rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚆 台鐵時刻表系統 - 多版本歷史發布中心</h1>
            <p>隨時依據網址退回或切換至任意歷史穩定版本 · 100% 純靜態獨立打包封裝</p>
            <a href="../index.html" class="btn-latest">🚀 前往最新穩定版 (Latest)</a>
        </div>

        <div class="version-list">
"""
    for idx, v in enumerate(versions_list):
        is_latest = idx == 0
        badge_cls = "version-badge latest" if is_latest else "version-badge"
        latest_tag = " (最新版)" if is_latest else ""
        hub_html += f"""
            <div class="version-card">
                <div class="version-info">
                    <div>
                        <span class="{badge_cls}">{v['version']}{latest_tag}</span>
                        <span class="version-date">📅 {v['date']} · Commit: <code>{v['commit']}</code></span>
                    </div>
                    <div class="version-desc">{v['desc']}</div>
                </div>
                <div class="version-actions">
                    <a href="./{v['version']}/index.html" class="btn-open">▶️ 啟動此版本</a>
                </div>
            </div>
        """

    hub_html += """
        </div>

        <div class="footer">
            <p>2026 台鐵全路網時刻表系統 · 語意化版本與全歷史版本快照管理</p>
        </div>
    </div>
</body>
</html>
"""
    with open(VERSIONS_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(hub_html)
    print("  ✅ Generated versions/index.html (Version Release Hub)")

if __name__ == "__main__":
    build_versions()
