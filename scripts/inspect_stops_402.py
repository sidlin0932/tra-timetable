# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

for num in ['402', '406', '408', '22', '472', '270']:
    t = next((x for x in trains if x['train_number'] == num), None)
    if t:
        print(f"\n=== Train {num} ({t['train_type']}: {t['origin']} -> {t['dest']}) ===")
        for s in t['stops']:
            print(f"  {s['station']} : {s['time']}")
