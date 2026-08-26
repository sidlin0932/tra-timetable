# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

for num in ['154', '156', '168', '162', '164', '176', '434']:
    t = next((x for x in trains if x['train_number'] == num), None)
    if t:
        print(f"\n=== Master DB Train {num} ({t['train_type']}: {t['origin']} -> {t['dest']}) ===")
        print(f"Stops count: {len(t['stops'])}")
        print(" -> ".join([f"{s['station']}({s['time']})" for s in t['stops']]))
    else:
        print(f"\nTrain {num} NOT FOUND in Master DB!")
