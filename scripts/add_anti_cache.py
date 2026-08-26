import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add Cache-Control meta headers
cache_headers = """    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">"""

if '<meta http-equiv="Cache-Control"' not in html:
    html = html.replace('<meta name="viewport" content="width=device-width, initial-scale=1.0">', '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n' + cache_headers, 1)

# Update data.js query param
html = html.replace('data.js?v=20260701_v5', 'data.js?v=20260701_v361')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Added anti-cache headers!")
