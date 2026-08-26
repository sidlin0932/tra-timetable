import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add Anti-Cache Meta Tags in <head>
anti_cache_tags = """    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">"""

html = html.replace('<meta name="viewport" content="width=device-width, initial-scale=1.0">', '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n' + anti_cache_tags, 1)

# 2. Set default destination to 台北
html = html.replace('id="destInput" class="station-input" value="內灣"', 'id="destInput" class="station-input" value="台北"')
html = html.replace('<strong id="modalDestVal">請選擇</strong>', '<strong id="modalDestVal">台北</strong>')
html = html.replace('<strong id="modalDestVal">內灣</strong>', '<strong id="modalDestVal">台北</strong>')

# 3. Bump version to v3.0.0
html = html.replace('v2.9.0 (2026.07.01版)', 'v3.0.0 (2026.07.01版)')
html = html.replace('v2.8.0 (2026.07.01版)', 'v3.0.0 (2026.07.01版)')
html = html.replace('核心版本: v2.9.0', '核心版本: v3.0.0 (預設板橋➔台北 · 一站式連續選站 · 自強號大站標色)')
html = html.replace('核心版本: v2.8.0', '核心版本: v3.0.0 (預設板橋➔台北 · 一站式連續選站 · 自強號大站標色)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated to v3.0.0 with default destination = 台北 and anti-cache meta tags!")
