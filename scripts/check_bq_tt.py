# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

# Check all trains from 板橋 that stop at 台東
for t in trains:
    stops = t['stops']
    st_names = [s['station'] for s in stops]
    if '板橋' in st_names and '台東' in st_names:
        i1 = st_names.index('板橋')
        i2 = st_names.index('台東')
        t1 = stops[i1]['time']
        t2 = stops[i2]['time']
        m1 = time_to_min(t1)
        m2 = time_to_min(t2)
        print(f"Train {t['train_number']} ({t['train_type']}): 板橋 idx {i1} ({t1}, {m1}m) -> 台東 idx {i2} ({t2}, {m2}m) | i1 < i2: {i1 < i2}, m1 < m2: {m1 < m2}")
