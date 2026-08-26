import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Redesign .modal-tabs-nav and .modal-tab-pill CSS
old_tabs_css = """        .modal-tabs-nav {
            display: flex;
            overflow-x: auto;
            gap: 6px;
            padding: 10px 20px;
            background: var(--bg-subtle);
            border-bottom: 1px solid var(--border-color);
            white-space: nowrap;
        }
        .modal-tab-pill {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 5px 12px;
            border-radius: 16px;
            font-size: 0.8rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.15s;
            text-decoration: none;
        }
        .modal-tab-pill:hover, .modal-tab-pill.active {
            background: var(--primary);
            color: #fff;
            border-color: var(--primary);
        }"""

new_tabs_css = """        .modal-tabs-nav {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            padding: 10px 20px;
            background: var(--bg-subtle);
            border-bottom: 1px solid var(--border-color);
            max-height: 120px;
            overflow-y: auto;
            scrollbar-width: thin;
        }
        .modal-tabs-nav::-webkit-scrollbar {
            height: 4px;
            width: 4px;
        }
        .modal-tabs-nav::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }
        .modal-tab-pill {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 4px 10px;
            border-radius: 14px;
            font-size: 0.78rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.15s;
            text-decoration: none;
            flex-shrink: 0;
            display: inline-flex;
            align-items: center;
        }
        .modal-tab-pill:hover, .modal-tab-pill.active {
            background: var(--primary);
            color: #fff;
            border-color: var(--primary);
            transform: translateY(-1px);
            box-shadow: 0 2px 5px rgba(2, 132, 199, 0.25);
        }"""

html = html.replace(old_tabs_css, new_tabs_css, 1)

# Bump version to v3.5.1
html = html.replace('v3.5.0 (2026.07.01版)', 'v3.5.1 (2026.07.01版)')
html = html.replace('核心版本: v3.5.0', '核心版本: v3.5.1 (完美重構全台17縣市快速導航選籤 · 告別擠壓與破版)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Fixed County Navigation Tabs and updated to v3.5.1!")
