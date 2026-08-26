# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

for train_no in ['423', '411', '431', '441', '305', '306']:
    t = next((x for x in trains if x['train_number'] == train_no), None)
    if t:
        print(f"=== Train {train_no} ({t['origin']} -> {t['dest']}) ===")
        for s in t['stops']:
            print(f"   {s['station']} ({s['time']})")
