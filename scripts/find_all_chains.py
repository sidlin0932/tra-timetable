# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

def min_to_time(m):
    return f"{m//60:02d}:{m%60:02d}"

def get_trains(f_st, t_st, min_time=0):
    res = []
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
                    res.append({
                        'train_no': t['train_number'],
                        'train_type': t['train_type'],
                        'dep': stops[i1]['time'],
                        'arr': stops[i2]['time'],
                        'dep_m': dep_m,
                        'arr_m': arr_m
                    })
    res.sort(key=lambda x: x['dep_m'])
    return res

wps = ['板橋', '台東', '潮州', '板橋']

leg1 = get_trains(wps[0], wps[1], 0)
print(f"Leg 1 ({wps[0]} -> {wps[1]}): {len(leg1)} options")

all_chains = []

for l1 in leg1:
    # After arriving at 台東, min stay 15m
    leg2 = get_trains(wps[1], wps[2], l1['arr_m'] + 15)
    for l2 in leg2:
        leg3 = get_trains(wps[2], wps[3], l2['arr_m'] + 15)
        for l3 in leg3:
            all_chains.append({
                'l1': l1,
                'l2': l2,
                'l3': l3,
                'dep': l1['dep'],
                'arr': l3['arr'],
                'duration': l3['arr_m'] - l1['dep_m']
            })

print(f"Total complete round-trip itineraries found: {len(all_chains)}")

# Look for chains with Train 154 or Train 152 in Leg 3
chains_with_154 = [c for c in all_chains if c['l3']['train_no'] == '154']
chains_with_152 = [c for c in all_chains if c['l3']['train_no'] == '152']
chains_with_168 = [c for c in all_chains if c['l3']['train_no'] == '168']

print(f"Chains with Train 154: {len(chains_with_154)}")
for c in chains_with_154[:3]:
    print(f"  {c['l1']['train_no']} ({c['l1']['dep']}->{c['l1']['arr']}) + {c['l2']['train_no']} ({c['l2']['dep']}->{c['l2']['arr']}) + 154 ({c['l3']['dep']}->{c['l3']['arr']})")

print(f"Chains with Train 152 (PP自強): {len(chains_with_152)}")
for c in chains_with_152[:3]:
    print(f"  {c['l1']['train_no']} ({c['l1']['dep']}->{c['l1']['arr']}) + {c['l2']['train_no']} ({c['l2']['dep']}->{c['l2']['arr']}) + 152 ({c['l3']['dep']}->{c['l3']['arr']})")

print(f"Chains with Train 168: {len(chains_with_168)}")
