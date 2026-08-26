# -*- coding: utf-8 -*-
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

# Find all trains that stop at 台東
tt_trains = [t for t in trains if any(s['station'] == '台東' for s in t['stops'])]
print(f"Trains stopping at 台東: {len(tt_trains)}")

# Sample of where they go
for t in tt_trains[:10]:
    st_names = [s['station'] for s in t['stops']]
    print(f"Train {t['train_number']} ({t['train_type']}): {t['origin']} -> {t['dest']} | stops: {len(st_names)} stations")
    print(f"   First 3: {st_names[:3]} ... Last 3: {st_names[-3:]}")

# Check 潮州 -> 台東
cz_to_tt = []
for t in trains:
    st_names = [s['station'] for s in t['stops']]
    if '潮州' in st_names and '台東' in st_names:
        i1 = st_names.index('潮州')
        i2 = st_names.index('台東')
        if i1 < i2:
            cz_to_tt.append(t)
print(f"\nTrains with both 潮州 and 台東 (in order): {len(cz_to_tt)}")

# Check transfers: 潮州 -> X -> 台東
cz_deps = []
for t in trains:
    st_names = [s['station'] for s in t['stops']]
    if '潮州' in st_names:
        idx = st_names.index('潮州')
        for s in t['stops'][idx+1:]:
            cz_deps.append((s['station'], t['train_number']))

print(f"Destinations reachable from 潮州: {len(set(c[0] for c in cz_deps))}")

# Check 台東 -> 板橋
tt_to_bq = []
for t in trains:
    st_names = [s['station'] for s in t['stops']]
    if '台東' in st_names and '板橋' in st_names:
        i1 = st_names.index('台東')
        i2 = st_names.index('板橋')
        if i1 < i2:
            tt_to_bq.append((t['train_number'], t['train_type'], t['stops'][i1]['time'], t['stops'][i2]['time']))
print(f"\nTrains 台東 -> 板橋 (in order): {len(tt_to_bq)}")
for b in tt_to_bq:
    print(" ", b)

# Check transfers: 台東 -> X -> 板橋 (e.g. 台東 -> 花蓮 -> 板橋)
tt_to_hl = []
for t in trains:
    st_names = [s['station'] for s in t['stops']]
    if '台東' in st_names and '花蓮' in st_names:
        i1 = st_names.index('台東')
        i2 = st_names.index('花蓮')
        if i1 < i2:
            tt_to_hl.append(t['train_number'])
print(f"Trains 台東 -> 花蓮: {len(tt_to_hl)}")

hl_to_bq = []
for t in trains:
    st_names = [s['station'] for s in t['stops']]
    if '花蓮' in st_names and '板橋' in st_names:
        i1 = st_names.index('花蓮')
        i2 = st_names.index('板橋')
        if i1 < i2:
            hl_to_bq.append(t['train_number'])
print(f"Trains 花蓮 -> 板橋: {len(hl_to_bq)}")
