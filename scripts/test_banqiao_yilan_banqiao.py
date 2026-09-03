# -*- coding: utf-8 -*-
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t_str):
    if not t_str: return 0
    h, m = map(int, t_str.split(':'))
    return h * 60 + m

# Let's test segment 1: 板橋 -> 宜蘭 from 06:00
seg1 = []
for t in trains:
    stops = t['stops']
    st_names = [s['station'] for s in stops]
    if '板橋' in st_names and '宜蘭' in st_names:
        i1 = st_names.index('板橋')
        i2 = st_names.index('宜蘭')
        if i1 < i2:
            d_min = time_to_min(stops[i1]['time'])
            a_min = time_to_min(stops[i2]['time'])
            if d_min >= 360:
                seg1.append({'no': t['train_number'], 'type': t['train_type'], 'dep': stops[i1]['time'], 'arr': stops[i2]['time'], 'dep_min': d_min, 'arr_min': a_min})

seg1.sort(key=lambda x: x['dep_min'])
print(f'Seg1 count: {len(seg1)}')

# For each seg1 train, find seg2: 宜蘭 -> 板橋 with minStay = 30
chains = []
for s1 in seg1[:10]:
    earliest_dep = s1['arr_min'] + 30
    seg2 = []
    for t in trains:
        stops = t['stops']
        st_names = [s['station'] for s in stops]
        if '宜蘭' in st_names and '板橋' in st_names:
            i1 = st_names.index('宜蘭')
            i2 = st_names.index('板橋')
            if i1 < i2:
                d_min = time_to_min(stops[i1]['time'])
                a_min = time_to_min(stops[i2]['time'])
                if d_min >= earliest_dep:
                    seg2.append({'no': t['train_number'], 'type': t['train_type'], 'dep': stops[i1]['time'], 'arr': stops[i2]['time'], 'dep_min': d_min, 'arr_min': a_min})
    seg2.sort(key=lambda x: x['dep_min'])
    for s2 in seg2[:3]:
        stay = s2['dep_min'] - s1['arr_min']
        chains.append({
            'dep': s1['dep'],
            'arr': s2['arr'],
            'train1': f"{s1['type']} {s1['no']} ({s1['dep']} to {s1['arr']})",
            'stay': stay,
            'train2': f"{s2['type']} {s2['no']} ({s2['dep']} to {s2['arr']})"
        })

print(f'Total chained routes found: {len(chains)}')
for c in chains[:8]:
    print(f"  {c['dep']} ~ {c['arr']} | 1: {c['train1']} | 停留 {c['stay']}分 | 2: {c['train2']}")
