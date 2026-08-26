# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

# Pre-indexed departures
deps_by_st = {}
for t in trains:
    for s_idx, s in enumerate(t['stops'][:-1]):
        st = s['station']
        if st not in deps_by_st: deps_by_st[st] = []
        deps_by_st[st].append({
            'train': t,
            'stopIdx': s_idx,
            'depMin': time_to_min(s['time'])
        })

for st in deps_by_st:
    deps_by_st[st].sort(key=lambda x: x['depMin'])

# Measure single leg search
def plan_single_leg(orig, dest, min_time=0):
    res = []
    for d in deps_by_st.get(orig, []):
        if d['depMin'] < min_time: continue
        t = d['train']
        s_idx = d['stopIdx']
        for j in range(s_idx + 1, len(t['stops'])):
            if t['stops'][j]['station'] == dest:
                arr_m = time_to_min(t['stops'][j]['time'])
                if arr_m > d['depMin']:
                    res.append({
                        'train_no': t['train_number'],
                        'train_type': t['train_type'],
                        'dep': t['stops'][s_idx]['time'],
                        'arr': t['stops'][j]['time'],
                        'dep_min': d['depMin'],
                        'arr_min': arr_m,
                        'duration': arr_m - d['depMin'],
                        'transfers': 0,
                        'legs': [{
                            'train_number': t['train_number'],
                            'train_type': t['train_type'],
                            'from': orig,
                            'to': dest,
                            'dep': t['stops'][s_idx]['time'],
                            'arr': t['stops'][j]['time'],
                            'all_stops': t['stops'][s_idx:j+1]
                        }]
                    })
    return res

# Multi-stop with 1 search per leg (pre-computed)
t0 = time.perf_counter()
wps = ['板橋', '台東', '潮州', '板橋']

# 1. Compute each leg once for whole day
leg_tables = []
for i in range(len(wps) - 1):
    leg_tables.append(plan_single_leg(wps[i], wps[i+1], 0))

# 2. Chain them efficiently
current_chains = [{'legs': r['legs'], 'dep_time': r['dep'], 'arr_time': r['arr'], 'duration': r['duration'], 'stopovers': []} for r in leg_tables[0]]

for i in range(1, len(wps) - 1):
    next_chains = []
    candidates = leg_tables[i]
    for itin in current_chains:
        arr_m = time_to_min(itin['arr_time'])
        earliest_dep = arr_m + 3
        # Fast filter candidates
        valid_next = [c for c in candidates if c['dep_min'] >= earliest_dep]
        for nxt in valid_next:
            stay_m = nxt['dep_min'] - arr_m
            total_dur = nxt['arr_min'] - time_to_min(itin['dep_time'])
            next_chains.append({
                'legs': itin['legs'] + nxt['legs'],
                'dep_time': itin['dep_time'],
                'arr_time': nxt['arr'],
                'duration': total_dur,
                'stopovers': itin['stopovers'] + [{'station': wps[i], 'stayMin': stay_m}]
            })
    current_chains = next_chains

t1 = time.perf_counter()
print(f"Chained planning took: {(t1 - t0)*1000:.2f} ms! Found {len(current_chains)} complete round trips.")
