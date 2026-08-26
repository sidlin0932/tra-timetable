# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

# Let's inspect the entire list of 30 direct trains from 潮州 to 板橋
# And see which ones were generated from Leg 1: 台東 -> 潮州

deps_by_st = {}
for t in trains:
    for s_idx, s in enumerate(t['stops'][:-1]):
        st = s['station']
        if st not in deps_by_st: deps_by_st[st] = []
        deps_by_st[st].append({
            'train': t,
            'stopIdx': s_idx,
            'depTimeMin': time_to_min(s['time'])
        })

for st in deps_by_st:
    deps_by_st[st].sort(key=lambda x: x['depTimeMin'])

def plan_leg(f_st, t_st, min_dep=0):
    routes = []
    for d in deps_by_st.get(f_st, []):
        if d['depTimeMin'] < min_dep: continue
        t = d['train']
        s_idx = d['stopIdx']
        for j in range(s_idx + 1, len(t['stops'])):
            if t['stops'][j]['station'] == t_st:
                arr_m = time_to_min(t['stops'][j]['time'])
                if arr_m > d['depTimeMin']:
                    routes.append({
                        'train_no': t['train_number'],
                        'train_type': t['train_type'],
                        'dep': t['stops'][s_idx]['time'],
                        'arr': t['stops'][j]['time'],
                        'dep_min': d['depTimeMin'],
                        'arr_min': arr_m,
                        'duration': arr_m - d['depTimeMin']
                    })
    return routes

l1_routes = plan_leg('台東', '潮州', 0)
l2_routes = plan_leg('潮州', '板橋', 0)

print(f"Leg 1 (台東 -> 潮州): {len(l1_routes)} trains")
print(f"Leg 2 (潮州 -> 板橋): {len(l2_routes)} trains")

# Let's see: for each l1 train, what l2 trains can it connect to?
all_pairs = []
for l1 in l1_routes:
    valid_l2 = [l2 for l2 in l2_routes if l2['dep_min'] >= l1['arr_min'] + 3]
    for l2 in valid_l2:
        all_pairs.append((l1['train_no'], l1['dep'], l1['arr'], l2['train_no'], l2['dep'], l2['arr']))

print(f"\nTotal direct (1-transfer or through) combinations for 台東 -> 潮州 -> 板橋: {len(all_pairs)}")

pairs_with_154 = [p for p in all_pairs if p[3] == '154']
print(f"\nCombinations connecting to 154 (潮州 18:14 -> 板橋 22:39): {len(pairs_with_154)}")
for p in pairs_with_154:
    print(f"  台東 {p[0]} ({p[1]}->{p[2]}) connect to 154 ({p[4]}->{p[5]})")

pairs_with_152 = [p for p in all_pairs if p[3] == '152']
print(f"\nCombinations connecting to 152 (潮州 18:27 -> 板橋 23:53): {len(pairs_with_152)}")
for p in pairs_with_152:
    print(f"  台東 {p[0]} ({p[1]}->{p[2]}) connect to 152 ({p[4]}->{p[5]})")
