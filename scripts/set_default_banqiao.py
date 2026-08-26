with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Change default input value from 台北 to 板橋
html = html.replace('id="originInput" class="station-input" value="台北"', 'id="originInput" class="station-input" value="板橋"')
html = html.replace('<strong id="modalOriginVal">台北</strong>', '<strong id="modalOriginVal">板橋</strong>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated default origin to 板橋!")
