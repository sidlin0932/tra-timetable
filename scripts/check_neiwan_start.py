# -*- coding: utf-8 -*-
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    timetable = json.load(f)

departures = []
for t in timetable:
    st_names = [s['station'] for s in t['stops']]
    if len(st_names) > 0 and st_names[0] == '內灣':
        departures.append(t)

print(f"Found {len(departures)} trains starting from 內灣:")
for t in departures:
    print(f"Train {t['train_number']}: {' -> '.join([f'{s['station']}({s['time']})' for s in t['stops']])}")
