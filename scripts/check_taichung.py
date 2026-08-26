# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

# Check trains between 板橋 and 台中
tc_trains = []
for t in trains:
    st_names = [s['station'] for s in t['stops']]
    if '板橋' in st_names and '台中' in st_names:
        i1 = st_names.index('板橋')
        i2 = st_names.index('台中')
        tc_trains.append((t['train_number'], t['train_type'], i1, i2, t['stops'][i1]['time'], t['stops'][i2]['time']))

print(f"Total trains connecting 板橋 and 台中: {len(tc_trains)}")
for tc in tc_trains[:10]:
    print(tc)
