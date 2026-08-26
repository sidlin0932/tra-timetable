# -*- coding: utf-8 -*-
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

print(f"Total trains: {len(trains)}")

def time_to_min(t):
    if not t: return 0
    h, m = map(int, t.split(':'))
    return h * 60 + m

# Let's find trains from 板橋 to 潮州
bq_cz = []
for t in trains:
    stops = t['stops']
    st_names = [s['station'] for s in stops]
    if '板橋' in st_names and '潮州' in st_names:
        i1 = st_names.index('板橋')
        i2 = st_names.index('潮州')
        if i1 < i2:
            bq_cz.append((t['train_number'], t['train_type'], stops[i1]['time'], stops[i2]['time']))

print(f"Direct 板橋 -> 潮州 trains: {len(bq_cz)}")
for b in bq_cz[:5]:
    print(" ", b)

# Trains from 潮州 to 台東
cz_tt = []
for t in trains:
    stops = t['stops']
    st_names = [s['station'] for s in stops]
    if '潮州' in st_names and '台東' in st_names:
        i1 = st_names.index('潮州')
        i2 = st_names.index('台東')
        if i1 < i2:
            cz_tt.append((t['train_number'], t['train_type'], stops[i1]['time'], stops[i2]['time']))

print(f"Direct 潮州 -> 台東 trains: {len(cz_tt)}")
for c in cz_tt[:5]:
    print(" ", c)

# Trains from 台東 to 板橋
tt_bq = []
for t in trains:
    stops = t['stops']
    st_names = [s['station'] for s in stops]
    if '台東' in st_names and '板橋' in st_names:
        i1 = st_names.index('台東')
        i2 = st_names.index('板橋')
        if i1 < i2:
            tt_bq.append((t['train_number'], t['train_type'], stops[i1]['time'], stops[i2]['time']))

print(f"Direct 台東 -> 板橋 trains: {len(tt_bq)}")
for d in tt_bq[:5]:
    print(" ", d)
