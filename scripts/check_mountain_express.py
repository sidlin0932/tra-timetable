# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

for num in ['105', '113', '115', '117', '121', '123', '125', '170', '172', '174']:
    t = next((x for x in trains if x['train_number'] == num), None)
    if t:
        st_names = [s['station'] for s in t['stops']]
        print(f"Train {num} ({t['train_type']}): origin {t['origin']} -> dest {t['dest']} | line: {t['line']}")
        print(f"  Stops: {st_names}\n")
