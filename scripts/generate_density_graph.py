import json

def time_to_minutes(time_str):
    if not time_str or ':' not in time_str: return -1
    parts = time_str.split(':')
    try:
        h = int(parts[0])
        m = int(parts[1][:2])
        return h * 60 + m
    except:
        return -1

def minutes_to_time(m):
    return f"{(m//60)%24:02d}:{m%60:02d}"

with open('f:/Antigravity/台鐵時刻表0701/full_timetable.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Initialize counts for 1440 minutes (24 hours)
minute_counts = [0] * 1440

for t in data['trains']:
    stops = t['stops']
    if not stops: continue
    
    start_min = time_to_minutes(stops[0].get('arrival_time', ''))
    end_min = time_to_minutes(stops[-1].get('arrival_time', ''))
    
    if start_min == -1 or end_min == -1: continue
    
    # Handle overnight trains
    if end_min < start_min:
        end_min += 24 * 60
        
    for m in range(start_min, end_min + 1):
        actual_m = m % 1440
        minute_counts[actual_m] += 1

trains_js = []
for t in data['trains']:
    stops = t['stops']
    if not stops: continue
    start_min = time_to_minutes(stops[0].get('arrival_time', ''))
    end_min = time_to_minutes(stops[-1].get('arrival_time', ''))
    if start_min == -1 or end_min == -1: continue
    
    trains_js.append({
        'n': t['train_number'],
        't': t['train_type'],
        's': stops[0].get('station', ''),
        'e': stops[-1].get('station', ''),
        't0': start_min,
        't1': end_min
    })

# Prepare data for ECharts
x_data = []
y_data = []
max_val = 0
max_idx = 0
for m in range(1440):
    x_data.append(minutes_to_time(m))
    count = minute_counts[m]
    y_data.append(count)
    if count > max_val:
        max_val = count
        max_idx = m

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>台鐵全日運行列車數量分佈圖</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #1e1e1e;
            color: #fff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
        }}
        #header {{
            padding: 20px;
            text-align: center;
        }}
        .note {{
            font-size: 14px;
            color: #aaa;
            margin-top: 5px;
        }}
        .controls {{
            margin-top: 10px;
        }}
        .controls label {{
            cursor: pointer;
            user-select: none;
            background: #333;
            padding: 8px 15px;
            border-radius: 20px;
            border: 1px solid #555;
            transition: all 0.2s;
        }}
        .controls label:hover {{
            background: #444;
        }}
        .controls input[type="checkbox"] {{
            margin-right: 8px;
            accent-color: #4caf50;
        }}
        #main {{
            width: 95%;
            flex-grow: 1;
            margin-bottom: 20px;
        }}
        
        /* Modal Styles */
        #trainModal {{
            display: none; 
            position: fixed; 
            z-index: 1000; 
            left: 0; 
            top: 0; 
            width: 100%; 
            height: 100%; 
            background-color: rgba(0,0,0,0.7);
            backdrop-filter: blur(5px);
        }}
        .modal-content {{
            background-color: #2c2c2c;
            margin: 5% auto; 
            padding: 20px;
            border: 1px solid #444;
            border-radius: 12px;
            width: 80%;
            max-width: 600px;
            max-height: 80vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        .close {{
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }}
        .close:hover {{
            color: #fff;
        }}
        .train-list {{
            overflow-y: auto;
            margin-top: 15px;
            padding-right: 10px;
        }}
        .train-item {{
            background: #3a3a3a;
            margin-bottom: 8px;
            padding: 12px 15px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-left: 4px solid #4caf50;
        }}
        .train-id {{ font-size: 16px; font-weight: bold; color: #4caf50; }}
        .train-type {{ font-size: 14px; color: #ddd; margin-left: 10px; }}
        .train-route {{ font-size: 14px; color: #aaa; }}
        
        /* Scrollbar */
        .train-list::-webkit-scrollbar {{ width: 8px; }}
        .train-list::-webkit-scrollbar-track {{ background: #2c2c2c; }}
        .train-list::-webkit-scrollbar-thumb {{ background: #555; border-radius: 4px; }}
        .train-list::-webkit-scrollbar-thumb:hover {{ background: #777; }}
    </style>
</head>
<body>
    <div id="header">
        <h2 style="margin: 0;">台鐵全日運行列車數量分佈圖 (每分鐘)</h2>
        <div class="note">點擊圖表上的任一點，即可查看該時間點正在運行的所有車次明細！最高峰出現在 <span id="peakLabel">{minutes_to_time(max_idx)} ({max_val} 班)</span>。</div>
        <div class="controls">
            <label>
                <input type="checkbox" id="toggleExtraTrains" checked>
                包含假日/特殊加班車 (5xxx/6xxx 車次)
            </label>
        </div>
    </div>
    <div id="main"></div>

    <!-- The Modal -->
    <div id="trainModal">
        <div class="modal-content">
            <div>
                <span class="close" onclick="closeModal()">&times;</span>
                <h3 id="modalTitle" style="margin-top: 0; color: #fff;">運行中列車明細</h3>
            </div>
            <div class="train-list" id="trainList">
                <!-- Train items will be injected here -->
            </div>
        </div>
    </div>

    <script>
        var allTrains = {json.dumps(trains_js)};
        var chartDom = document.getElementById('main');
        var myChart = echarts.init(chartDom, 'dark');
        var option;

        option = {{
            backgroundColor: 'transparent',
            tooltip: {{
                trigger: 'axis',
                axisPointer: {{
                    type: 'cross',
                    label: {{
                        backgroundColor: '#6a7985'
                    }}
                }}
            }},
            toolbox: {{
                feature: {{
                    saveAsImage: {{ title: '儲存圖片' }}
                }}
            }},
            grid: {{
                left: '3%',
                right: '4%',
                bottom: '8%',
                containLabel: true
            }},
            xAxis: [
                {{
                    type: 'category',
                    boundaryGap: false,
                    data: {json.dumps(x_data)},
                    axisLabel: {{
                        interval: 59, // Show roughly every hour
                        formatter: function (value) {{
                            return value;
                        }}
                    }}
                }}
            ],
            yAxis: [
                {{
                    type: 'value',
                    name: '同時運行班次',
                    min: 0,
                    splitLine: {{
                        lineStyle: {{
                            color: '#333'
                        }}
                    }}
                }}
            ],
            dataZoom: [
                {{
                    type: 'inside',
                    start: 0,
                    end: 100
                }},
                {{
                    start: 0,
                    end: 100
                }}
            ],
            series: [
                {{
                    name: '運行班次',
                    type: 'line',
                    smooth: true,
                    lineStyle: {{
                        width: 3,
                        color: '#4caf50'
                    }},
                    showSymbol: false,
                    areaStyle: {{
                        opacity: 0.8,
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            {{
                                offset: 0,
                                color: 'rgba(76, 175, 80, 0.8)'
                            }},
                            {{
                                offset: 1,
                                color: 'rgba(76, 175, 80, 0.1)'
                            }}
                        ])
                    }},
                    emphasis: {{
                        focus: 'series'
                    }},
                    data: {json.dumps(y_data)},
                    markPoint: {{
                        data: [
                            {{ type: 'max', name: '全日最高峰' }},
                            {{ 
                                name: '早高峰', 
                                coord: ['08:09', {minute_counts[time_to_minutes("08:09")]}], 
                                value: {minute_counts[time_to_minutes("08:09")]}
                            }}
                        ],
                        label: {{
                            color: '#fff',
                            fontWeight: 'bold'
                        }}
                    }},
                    markLine: {{
                        data: [
                            {{ type: 'average', name: '平均值' }}
                        ]
                    }}
                }}
            ]
        }};

        option && myChart.setOption(option);
        
        // Recalculate graph logic
        function updateGraph() {{
            var includeExtra = document.getElementById('toggleExtraTrains').checked;
            
            var newCounts = new Array(1440).fill(0);
            var maxV = 0;
            var maxI = 0;
            var peakMorningV = 0;
            
            allTrains.forEach(function(t) {{
                // Filter out 5xxx and 6xxx if not included
                if (!includeExtra && t.n.length === 4 && (t.n.startsWith('5') || t.n.startsWith('6'))) {{
                    return;
                }}
                
                var start = t.t0;
                var end = t.t1 < t.t0 ? t.t1 + 1440 : t.t1;
                for (var m = start; m <= end; m++) {{
                    var am = m % 1440;
                    newCounts[am]++;
                }}
            }});
            
            for(var m=0; m<1440; m++) {{
                if (newCounts[m] > maxV) {{ maxV = newCounts[m]; maxI = m; }}
                if (m >= 420 && m <= 540) {{ // 7AM to 9AM
                    if (newCounts[m] > peakMorningV) peakMorningV = newCounts[m];
                }}
            }}
            
            var hh = String(Math.floor(maxI/60)).padStart(2, '0');
            var mm = String(maxI%60).padStart(2, '0');
            document.getElementById('peakLabel').innerText = hh + ':' + mm + ' (' + maxV + ' 班)';
            
            myChart.setOption({{
                series: [{{
                    data: newCounts,
                    markPoint: {{
                        data: [
                            {{ type: 'max', name: '全日最高峰' }},
                            {{ 
                                name: '早高峰', 
                                coord: ['08:09', peakMorningV], 
                                value: peakMorningV
                            }}
                        ]
                    }}
                }}]
            }});
        }}
        
        document.getElementById('toggleExtraTrains').addEventListener('change', updateGraph);
        
        // Add click event listener
        myChart.on('click', function(params) {{
            var clickedMin = params.dataIndex; // 0 to 1439
            var timeStr = params.name;
            var count = params.value;
            var includeExtra = document.getElementById('toggleExtraTrains').checked;
            
            // Filter trains active at this minute
            var activeTrains = allTrains.filter(function(t) {{
                if (!includeExtra && t.n.length === 4 && (t.n.startsWith('5') || t.n.startsWith('6'))) {{
                    return false;
                }}
                if (t.t0 <= t.t1) {{
                    return clickedMin >= t.t0 && clickedMin <= t.t1;
                }} else {{
                    return clickedMin >= t.t0 || clickedMin <= (t.t1 % 1440);
                }}
            }});
            
            // Sort by train number
            activeTrains.sort(function(a, b) {{ return a.n.localeCompare(b.n); }});
            
            // Render modal
            document.getElementById('modalTitle').innerText = timeStr + ' 運行中列車 (' + count + '班)';
            var listHtml = '';
            activeTrains.forEach(function(t) {{
                listHtml += `
                    <div class="train-item">
                        <div>
                            <span class="train-id">車次 ${{t.n}}</span>
                            <span class="train-type">${{t.t}}</span>
                        </div>
                        <div class="train-route">
                            ${{t.s}} ➔ ${{t.e}}
                        </div>
                    </div>
                `;
            }});
            document.getElementById('trainList').innerHTML = listHtml;
            document.getElementById('trainModal').style.display = 'block';
        }});
        
        function closeModal() {{
            document.getElementById('trainModal').style.display = 'none';
        }}
        
        // Close modal when clicking outside
        window.onclick = function(event) {{
            var modal = document.getElementById('trainModal');
            if (event.target == modal) {{
                modal.style.display = 'none';
            }}
        }}

        window.addEventListener('resize', function() {{
            myChart.resize();
        }});
    </script>
</body>
</html>
"""

with open('f:/Antigravity/台鐵時刻表0701/daily_train_density.html', 'w', encoding='utf-8') as out:
    out.write(html_content)
    
print("Chart generated successfully at f:/Antigravity/台鐵時刻表0701/daily_train_density.html")
