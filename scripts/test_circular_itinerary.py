# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

print(f"Total trains: {len(trains)}")

def get_trains_between(orig, dest):
    res = []
    for t in trains:
        stops = t['stops']
        st_names = [s['station'] for s in stops]
        if orig in st_names and dest in st_names:
            i1 = st_names.index(orig)
            i2 = st_names.index(dest)
            if i1 < i2:
                res.append((t['train_number'], t['train_type'], stops[i1]['time'], stops[i2]['time']))
    return res

l1 = get_trains_between('板橋', '潮州')
l2 = get_trains_between('潮州', '台東')
l3 = get_trains_between('台東', '板橋')

print(f"\n1. 板橋 ➔ 潮州: {len(l1)} direct trains")
for x in l1[:3]: print("  ", x)

print(f"\n2. 潮州 ➔ 台東: {len(l2)} direct trains")
for x in l2[:5]: print("  ", x)

print(f"\n3. 台東 ➔ 板橋: {len(l3)} direct trains")
for x in l3[:5]: print("  ", x)

assert len(l1) > 0
assert len(l2) > 0
assert len(l3) > 0

print("\nSUCCESS: All 3 legs have ample direct trains!")
