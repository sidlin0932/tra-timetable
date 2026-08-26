import os
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace any version string in index.html with v3.6.2
html = re.sub(r'v3\.\d+\.\d+', 'v3.6.2', html)
html = html.replace('data.js?v=20260701_v361', f'data.js?v=20260701_v362_{int(os.path.getmtime("index.html"))}')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html all version tags to v3.6.2!")
