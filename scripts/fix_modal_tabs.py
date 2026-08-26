# -*- coding: utf-8 -*-
html_path = 'f:/Antigravity/台鐵時刻表0701/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix scrollToCounty so it properly scrolls the inner modalStationList container
old_scroll_fn = """        function scrollToCounty(id, e) {
            if (e) e.preventDefault();
            const el = document.getElementById(id);
            if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }"""

new_scroll_fn = """        function scrollToCounty(id, e) {
            if (e) {
                e.preventDefault();
                e.stopPropagation();
            }
            const el = document.getElementById(id);
            const container = document.getElementById('modalStationList');
            if (el && container) {
                const elTop = el.offsetTop;
                container.scrollTo({ top: elTop - 10, behavior: 'smooth' });
            } else if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }"""

if old_scroll_fn in content:
    content = content.replace(old_scroll_fn, new_scroll_fn)
    print("Fixed scrollToCounty implementation!")
else:
    print("Warning: old_scroll_fn not found directly")

# Fix modalTabPill styling and add active state styling
old_tab_style = """.modal-tab-pill {
            padding: 4px 10px;
            font-size: 0.78rem;
            font-weight: 700;
            border-radius: 12px;
            background: var(--bg-subtle);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            text-decoration: none;
            white-space: nowrap;
            cursor: pointer;
            transition: all 0.15s;
        }
        .modal-tab-pill:hover {
            background: var(--primary);
            color: #ffffff;
            border-color: var(--primary);
        }"""

new_tab_style = """.modal-tab-pill {
            padding: 5px 11px;
            font-size: 0.8rem;
            font-weight: 700;
            border-radius: 12px;
            background: var(--bg-subtle);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            text-decoration: none;
            white-space: nowrap;
            cursor: pointer;
            display: inline-block;
            user-select: none;
            touch-action: manipulation;
            transition: all 0.15s;
        }
        .modal-tab-pill:hover, .modal-tab-pill:active {
            background: var(--primary);
            color: #ffffff;
            border-color: var(--primary);
            transform: scale(1.05);
        }"""

if old_tab_style in content:
    content = content.replace(old_tab_style, new_tab_style)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated index.html with fixed scrollToCounty and tab buttons!")
