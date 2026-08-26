# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

print(f"Total trains: {len(trains)}")

t154 = next((t for t in trains if t['train_number'] == '154'), None)
print("154 in JSON:", t154)

# Let's check all trains from 潮州 to 板橋
cz_deps = []
for t in trains:
    f_idx = next((i for i, s in enumerate(t['stops']) if s['station'] == '潮州'), None)
    t_idx = next((i for i, s in enumerate(t['stops']) if s['station'] == '板橋'), None)
    if f_idx is not None and t_idx is not None and f_idx < t_idx:
        cz_deps.append((t['train_number'], t['train_type'], t['stops'][f_idx]['time'], t['stops'][t_idx]['time']))

print(f"\nDirect 潮州 -> 板橋 trains: {len(cz_deps)}")
for c in cz_deps:
    print(c)
