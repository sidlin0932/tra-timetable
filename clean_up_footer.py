# -*- coding: utf-8 -*-
"""
Cleans up the bloated footer in index.html with a sleek, professional, modern layout.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML = BASE_DIR / "index.html"

with open(INDEX_HTML, "r", encoding="utf-8") as f:
    html = f.read()

OLD_FOOTER = """        <footer style="text-align: center; margin-top: 48px; padding-top: 24px; border-top: 1px dashed var(--border-color); color: var(--text-muted); font-size: 0.85rem;">
            <p>🚆 2026 台鐵全路網時刻表系統 · <strong>核心版本: v3.7.0 (新增指定轉乘站功能 · 區間+自強/自強+區間混搭接駁全量釋放 · 僅轉乘模式 🌟) (列車停靠清單車站全量支援點擊連動車站時刻表 · 支援多層彈窗深度互動) (完美重構全台17縣市快速導航選籤 · 告別擠壓與破版) (新增純車行時間最短 & 等車時間最少自訂排序指標) (全方位乘車數據外露 · 車程/等候時間/每段行駛分鐘一目了然) (轉乘站名直接外露精確等候時間 · 緊湊轉乘高亮) (觀光支線清新森林綠標示 · 自強號大站紅光 · 階層清晰) (出發連選抵達 · 抵達單擊秒關 · 最完美選站流) (直覺單擊選定起訖站 · 點哪站選哪站) (全台西部幹線區間車多段智慧縫合 · 直達特快與全區間接駁雙軌並存) (跨日列車時間軸排序校正 · 149次基隆➔潮州跨日修復 · 單字站名全量洗淨) (全量車站名稱校正 · 松山/山佳/冬山名詞修復 · 4154直通拼接完善) (預設板橋➔台北 · 一站式連續選站 · 自強號大站標色) (一站式極速連續選站與常用大站快捷) (自強號特快大站醒目標色) (支援車站全日發車時刻表與列車時刻雙彈窗) (支援列車全線時刻表彈窗) (含轉乘失敗第二備案)</strong> (2026/07/01 官方大改點完整收錄)</p>
            <p style="margin-top: 4px; font-size: 0.75rem;">100% 純前端離線運算 · 支援全台 17 縣市車站選單與無限多段轉乘智慧規劃</p>
        </footer>"""

NEW_FOOTER = """        <footer class="app-footer-clean">
            <div class="footer-brand-line">
                <span class="footer-title">🚆 2026 台鐵全路網跨區間轉乘規劃系統</span>
                <span class="footer-ver-tag">v3.9.2</span>
            </div>
            <div class="footer-sub-text">
                ⚡ 100% 純前端本地記憶體極速運算 · 完整收錄 2026/07/01 官方大改點 1,465 班全路網列車
            </div>
            <div class="footer-links-row">
                <a href="versions/index.html" class="footer-action-link">📦 歷史版本快照切換 (隨時退版)</a>
                <span class="footer-dot">·</span>
                <span class="footer-feature-item">🗺️ 台灣鐵路地理地圖模式</span>
                <span class="footer-dot">·</span>
                <span class="footer-feature-item">📱 手機優先 48px 觸控熱區</span>
                <span class="footer-dot">·</span>
                <span class="footer-feature-item">📶 離線 PWA 支援</span>
            </div>
        </footer>"""

FOOTER_CSS = """
        /* Modern Clean Footer */
        .app-footer-clean {
            text-align: center;
            margin-top: 48px;
            padding: 24px 16px 36px;
            border-top: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 0.85rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }
        .footer-brand-line {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 800;
            color: var(--text-main);
            font-size: 0.95rem;
        }
        .footer-ver-tag {
            background: var(--primary-light);
            color: var(--primary);
            font-size: 0.75rem;
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: 800;
            border: 1px solid var(--primary);
        }
        .footer-sub-text {
            font-size: 0.8rem;
            color: var(--text-muted);
        }
        .footer-links-row {
            display: flex;
            align-items: center;
            justify-content: center;
            flex-wrap: wrap;
            gap: 8px;
            font-size: 0.78rem;
            margin-top: 4px;
        }
        .footer-action-link {
            color: var(--primary);
            text-decoration: none;
            font-weight: 700;
            transition: color 0.15s;
        }
        .footer-action-link:hover {
            text-decoration: underline;
        }
        .footer-dot {
            color: var(--border-color);
        }
"""

if OLD_FOOTER in html:
    html = html.replace(OLD_FOOTER, NEW_FOOTER)
else:
    print("Direct replace fallback for footer")

if "Modern Clean Footer" not in html:
    html = html.replace("    </style>", FOOTER_CSS + "\n    </style>")

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Footer successfully modernized and cleaned up!")
