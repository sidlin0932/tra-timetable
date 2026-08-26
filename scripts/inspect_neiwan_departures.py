# -*- coding: utf-8 -*-
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    timetable = json.load(f)

for t in timetable:
    st_names = [s['station'] for s in t['stops']]
    if '內灣' in st_names:
        print(f"Train {t['train_number']}: {' -> '.join([f'{s['station']}({s['time']})' for s in t['stops']])}")
