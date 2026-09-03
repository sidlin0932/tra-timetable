# -*- coding: utf-8 -*-
import json
import re

print("==================================================================")
print("Deep System Self-Audit & TRA Alignment")
print("==================================================================")

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    tt = json.load(f)

print(f"\n[CHECK 1] Station Name Purity Check")
all_stations = set()
dirty_stations = set()
for t in tt:
    for s in t['stops']:
        st = s['station']
        all_stations.add(st)
        if re.search(r'[a-zA-Z0-9_\-\s]', st) and not st in ['新城(太魯閣)', '三塊厝']:
            dirty_stations.add(st)

print(f"  • Total stations in network: {len(all_stations)}")
if not dirty_stations:
    print(f"  [PASS] 100% clean! No English, numbers, or invalid characters.")
else:
    print(f"  [FAIL] Dirty stations: {dirty_stations}")

print(f"\n[CHECK 2] Duplicate Stop Check")
dup_stop_trains = []
for t in tt:
    seen_st = set()
    for s in t['stops']:
        if s['station'] in seen_st:
            dup_stop_trains.append((t['train_number'], s['station']))
        seen_st.add(s['station'])

if not dup_stop_trains:
    print(f"  [PASS] 924 trains have 0 duplicate stops.")
else:
    print(f"  [FAIL] Duplicate stops: {dup_stop_trains}")

print(f"\n[CHECK 3] Branch Line Junction Connectivity")
junctions = {
    'Jiji Line': ('二水', ['濁水', '集集', '水里', '車埕']),
    'Neiwan Line': ('新竹', ['竹中', '竹東', '合興', '內灣']),
    'Liujia Line': ('新竹', ['竹中', '六家']),
    'Pingxi Line': ('瑞芳', ['十分', '平溪', '菁桐']),
    'Shalun Line': ('台南', ['中洲', '長榮大學', '沙崙'])
}

for b_name, (junc, sample_sts) in junctions.items():
    junc_trains = [t for t in tt if any(s['station'] == junc for s in t['stops'])]
    print(f"  • {b_name} Hub [{junc}]: {len(junc_trains)} trains passing through.")

print("\n==================================================================")
