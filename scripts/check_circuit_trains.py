# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

def get_leg_trains(orig, dest, min_dep_min=0):
    res = []
    for t in trains:
        stops = t['stops']
        st_names = [s['station'] for s in stops]
        if orig in st_names and dest in st_names:
            i1 = st_names.index(orig)
            i2 = st_names.index(dest)
            if i1 < i2:
                dep_m = time_to_min(stops[i1]['time'])
                arr_m = time_to_min(stops[i2]['time'])
                if dep_m >= min_dep_min and arr_m > dep_m:
                    res.append({
                        'train_number': t['train_number'],
                        'train_type': t['train_type'],
                        'dep': stops[i1]['time'],
                        'arr': stops[i2]['time'],
                        'dep_min': dep_m,
                        'arr_min': arr_m,
                        'stops': [s['station'] for s in stops[i1:i2+1]]
                    })
    res.sort(key=lambda x: x['dep_min'])
    return res

# 1. Check all direct Chaozhou -> Banqiao trains in the evening
cz_bq = get_leg_trains('潮州', '板橋')
print(f"=== All 潮州 -> 板橋 Trains ({len(cz_bq)} trains) ===")
for c in cz_bq:
    print(f"  Train {c['train_number']} ({c['train_type']}): 潮州 {c['dep']} -> 板橋 {c['arr']}")

# 2. Check all Taitung -> Chaozhou trains
tt_cz = get_leg_trains('台東', '潮州')
print(f"\n=== All 台東 -> 潮州 Trains ({len(tt_cz)} trains) ===")
for t in tt_cz:
    print(f"  Train {t['train_number']} ({t['train_type']}): 台東 {t['dep']} -> 潮州 {t['arr']}")

# 3. Check all Banqiao -> Taitung trains
bq_tt = get_leg_trains('板橋', '台東')
print(f"\n=== All 板橋 -> 台東 Trains ({len(bq_tt)} trains) ===")
for b in bq_tt:
    print(f"  Train {b['train_number']} ({b['train_type']}): 板橋 {b['dep']} -> 台東 {b['arr']}")
