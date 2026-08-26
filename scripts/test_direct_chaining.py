# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

# Let's test the clean leg-based planner
def get_leg_options(f_st, t_st, min_time=0):
    directs = []
    for t in trains:
        stops = t['stops']
        st_names = [s['station'] for s in stops]
        if f_st in st_names and t_st in st_names:
            i1 = st_names.index(f_st)
            i2 = st_names.index(t_st)
            if i1 < i2:
                dep_m = time_to_min(stops[i1]['time'])
                arr_m = time_to_min(stops[i2]['time'])
                if dep_m >= min_time and arr_m > dep_m:
                    directs.append({
                        'train_number': t['train_number'],
                        'train_type': t['train_type'],
                        'train_model': t.get('train_model', ''),
                        'is_trpass': t.get('is_trpass', True),
                        'origin': t['origin'],
                        'dest': t['dest'],
                        'from': f_st,
                        'to': t_st,
                        'dep': stops[i1]['time'],
                        'arr': stops[i2]['time'],
                        'dep_min': dep_m,
                        'arr_min': arr_m,
                        'layover': 0,
                        'all_stops': stops[i1:i2+1]
                    })
    directs.sort(key=lambda x: x['dep_min'])
    return directs

wps = ['台東', '潮州', '板橋']

leg0 = get_leg_options(wps[0], wps[1], 0)
leg1 = get_leg_options(wps[1], wps[2], 0)

print(f"Leg 0 ({wps[0]} -> {wps[1]}): {len(leg0)} direct trains")
print(f"Leg 1 ({wps[1]} -> {wps[2]}): {len(leg1)} direct trains")

chained = []
for l0 in leg0:
    for l1 in leg1:
        if l1['dep_min'] >= l0['arr_min'] + 3:
            stay_m = l1['dep_min'] - l0['arr_min']
            is_through = (l0['train_number'] == l1['train_number'])
            chained.append({
                'dep_time': l0['dep'],
                'arr_time': l1['arr'],
                'duration': l1['arr_min'] - l0['dep_min'],
                'transfers': 0 if is_through else 1,
                'is_through': is_through,
                'legs': [l0, l1]
            })

print(f"\nTotal clean chained itineraries: {len(chained)}")

# Sort by arr_time descending (latest arrival first)
chained.sort(key=lambda x: time_to_min(x['arr_time']), reverse=True)

print("\n=== Top 5 Latest Arrivals ===")
for c in chained[:5]:
    l0, l1 = c['legs']
    print(f"Dep {c['dep_time']} -> Arr {c['arr_time']} ({c['duration']}min) | Leg1: {l0['train_type']} {l0['train_number']} ({l0['dep']}->{l0['arr']}) -> Leg2: {l1['train_type']} {l1['train_number']} ({l1['dep']}->{l1['arr']})")

has_154 = any(c['legs'][1]['train_number'] == '154' for c in chained)
has_152 = any(c['legs'][1]['train_number'] == '152' for c in chained)
has_168 = any(c['legs'][1]['train_number'] == '168' for c in chained)

print(f"\nHas 154: {has_154}")
print(f"Has 152 (PP自強): {has_152}")
print(f"Has 168: {has_168}")
