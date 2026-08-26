# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

for t in trains:
    st_names = [s['station'] for s in t['stops']]
    if '台東' in st_names and '東澳' in st_names:
        i1 = st_names.index('台東')
        i2 = st_names.index('東澳')
        print(f"Train {t['train_number']} ({t['origin']} -> {t['dest']}): 台東 at {i1}, 東澳 at {i2} (diff: {i2 - i1})")
        print("  Stops:", [s['station'] for s in t['stops']])
