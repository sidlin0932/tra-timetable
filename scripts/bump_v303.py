import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Update version strings to v3.0.3
html = html.replace('v3.0.2 (2026.07.01版)', 'v3.0.3 (2026.07.01版)')
html = html.replace('data.js?v=20260701_v4', 'data.js?v=20260701_v5')
html = html.replace('核心版本: v3.0.2', '核心版本: v3.0.3 (跨日列車時間軸排序校正 · 149次基隆➔潮州跨日修復 · 單字站名全量洗淨)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Bumped version to v3.0.3!")
