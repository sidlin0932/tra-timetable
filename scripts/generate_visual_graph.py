import json
import os
import datetime

# 1. Load the JSON data
with open('f:/Antigravity/台鐵時刻表0701/full_timetable.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# The specific sequence of stations we want to plot (North to South)
target_stations = ['台北', '板橋', '桃園', '中壢', '新竹', '竹南', '苗栗', '豐原', '台中']
# Handle alternate spellings
station_aliases = {
    '臺北': '台北', '臺中': '台中', '臺南': '台南', '臺東': '台東'
}

def normalize_station(name):
    for k, v in station_aliases.items():
        if k in name:
            name = name.replace(k, v)
    return name

# 2. Filter trains that travel from Taipei to Taichung (Southbound)
plot_trains = []
for t in data['trains']:
    stops = t['stops']
    
    # Filter only relevant stops for this graph
    graph_stops = []
    for s in stops:
        s_norm = normalize_station(s['station'])
        for ts in target_stations:
            if ts in s_norm:
                graph_stops.append({
                    'station': ts,
                    'time': s['departure_time']
                })
                break
                
    # Sort them by time to ensure chronological order
    def get_time_val(time_str):
        h, m = map(int, time_str.split(':'))
        if h < 4: h += 24
        return h * 60 + m
        
    graph_stops.sort(key=lambda x: get_time_val(x['time']))
    
    # Check if this train goes from Taipei -> Taichung
    tpe_idx = -1
    txg_idx = -1
    for i, gs in enumerate(graph_stops):
        if gs['station'] == '台北': tpe_idx = i
        if gs['station'] == '台中': txg_idx = i
        
    if tpe_idx != -1 and txg_idx != -1 and tpe_idx < txg_idx:
        # Keep only stops between Taipei and Taichung inclusive
        valid_stops = graph_stops[tpe_idx:txg_idx+1]
        
        # Is it TR-PASS eligible? (Exclude EMU3000, Puyuma, Taroko)
        model = t['train_model']
        is_trpass = not any(x in model for x in ['3000', '普悠瑪', '太魯閣'])
        
        plot_trains.append({
            'train': t['train_number'],
            'type': t['train_type'],
            'model': model,
            'is_trpass': is_trpass,
            'stops': valid_stops
        })

print(f"Found {len(plot_trains)} direct trains from Taipei to Taichung.")

# 3. Generate HTML with Apache ECharts
series_data = []
# Y-axis inversion (Taichung at bottom, Taipei at top)
reversed_stations = target_stations[::-1]

for pt in plot_trains:
    train_data = []
    for s in pt['stops']:
        # Format time to standard ISO for ECharts (using 2026-07-01 as dummy date)
        # Handle cross-midnight (h < 4 -> 2026-07-02)
        h, m = map(int, s['time'].split(':'))
        day = '01'
        if h < 4:
            day = '02'
            # h is kept 0-3 for ISO string
        time_str = f"2026-07-{day}T{h:02d}:{m:02d}:00"
        train_data.append({
            'name': s['station'],
            'value': [time_str, reversed_stations.index(s['station'])]
        })
        
    color = '#1f77b4' # TR-PASS OK (Blue)
    if not pt['is_trpass']:
        color = '#cccccc' # TR-PASS NOT OK (Grey)
    elif '自強' in pt['type'] or '莒光' in pt['type']:
        color = '#d62728' # TR-PASS OK but specific type (Red for express)
    elif '區間' in pt['type']:
        color = '#2ca02c' # TR-PASS OK (Green for local)
        
    series = {
        'name': f"{pt['train']} ({pt['type']})",
        'type': 'line',
        'data': train_data,
        'smooth': False,
        'symbol': 'circle',
        'symbolSize': 6,
        'itemStyle': {'color': color},
        'lineStyle': {'width': 2, 'color': color},
        # Tooltip formatting for this specific train
        'tooltip': {
            'formatter': f"車次: {pt['train']}<br/>車種: {pt['type']}<br/>車型: {pt['model']}<br/>TR-PASS: {'✅ 可用' if pt['is_trpass'] else '❌ 禁用'}"
        }
    }
    series_data.append(series)

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>台北-台中 乘車節點圖 (Marey Chart)</title>
    <!-- Include ECharts -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body, html {{ margin: 0; padding: 0; height: 100%; width: 100%; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #fff; }}
        #main {{ width: 100%; height: 90vh; }}
        #header {{ height: 10vh; padding: 10px 20px; box-sizing: border-box; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; }}
        .legend {{ display: flex; gap: 20px; font-size: 14px; }}
        .legend-item {{ display: flex; align-items: center; gap: 5px; }}
        .color-box {{ width: 15px; height: 15px; border-radius: 3px; }}
        .note {{ font-size: 12px; color: #888; }}
    </style>
</head>
<body>
    <div id="header">
        <div>
            <h2 style="margin: 0; color: #fff;">台北 ➔ 台中 列車時刻節點圖</h2>
            <div class="note">已修復台中站名，成功繪製正統山線時刻！滑鼠懸停於線條上可查看車次與 TR-PASS 資格，點擊圖例可隱藏/顯示特定車種。X軸可拖曳縮放。</div>
        </div>
        <div class="legend">
            <div class="legend-item"><div class="color-box" style="background: #2ca02c;"></div> TR-PASS 區間/區間快</div>
            <div class="legend-item"><div class="color-box" style="background: #d62728;"></div> TR-PASS 莒光/PP自強</div>
            <div class="legend-item"><div class="color-box" style="background: #cccccc;"></div> 禁用 (EMU3000/普悠瑪/太魯閣)</div>
        </div>
    </div>
    <div id="main"></div>
    <script>
        var chartDom = document.getElementById('main');
        var myChart = echarts.init(chartDom, 'dark');
        var option;

        const stations = {json.dumps(reversed_stations, ensure_ascii=False)};
        
        option = {{
            backgroundColor: '#121212',
            tooltip: {{
                trigger: 'item',
                formatter: function (params) {{
                    let time = new Date(params.value[0]);
                    let h = time.getHours().toString().padStart(2, '0');
                    let m = String(time.getMinutes()).padStart(2, '0');
                    return params.marker + ' <b>' + params.seriesName + '</b><br/>' +
                           params.name + ' ' + h + ':' + m + '<br/><br/>' +
                           params.seriesOption.tooltip.formatter;
                }}
            }},
            dataZoom: [
                {{ type: 'inside', xAxisIndex: 0, filterMode: 'none' }},
                {{ type: 'slider', xAxisIndex: 0, filterMode: 'none', bottom: 10 }}
            ],
            grid: {{
                left: '5%',
                right: '5%',
                bottom: '10%',
                top: '5%',
                containLabel: true
            }},
            xAxis: {{
                type: 'time',
                splitLine: {{ show: true, lineStyle: {{ color: '#333', type: 'dashed' }} }},
                axisLabel: {{
                    formatter: '{{HH}}:{{mm}}',
                    color: '#aaa'
                }},
                min: '2026-07-01T05:00:00',
                max: '2026-07-02T01:00:00'
            }},
            yAxis: {{
                type: 'category',
                data: stations,
                boundaryGap: false,
                splitLine: {{ show: true, lineStyle: {{ color: '#333' }} }},
                axisLabel: {{ color: '#ddd', fontSize: 14 }}
            }},
            series: {json.dumps(series_data, ensure_ascii=False)}
        }};

        myChart.setOption(option);
        
        window.addEventListener('resize', function() {{
            myChart.resize();
        }});
    </script>
</body>
</html>
"""

with open('f:/Antigravity/台鐵時刻表0701/interactive_timetable.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Created interactive_timetable.html successfully.")
