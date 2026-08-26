import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Update version strings to v3.0.2
html = html.replace('v3.0.1 (2026.07.01版)', 'v3.0.2 (2026.07.01版)')
html = html.replace('v3.0.0 (2026.07.01版)', 'v3.0.2 (2026.07.01版)')
html = html.replace('data.js?v=20260701_v3', 'data.js?v=20260701_v4')
html = html.replace('核心版本: v3.0.1 (完美修復一站式選站點擊)', '核心版本: v3.0.2 (全量車站名稱校正 · 松山/山佳/冬山名詞修復 · 4154直通拼接完善)')
html = html.replace('核心版本: v3.0.0', '核心版本: v3.0.2 (全量車站名稱校正 · 松山/山佳/冬山名詞修復 · 4154直通拼接完善)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Bumped version to v3.0.2!")
