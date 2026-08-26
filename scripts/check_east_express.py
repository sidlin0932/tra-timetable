# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

for num in ['402', '406', '408', '410', '412', '418', '422', '426', '428', '432', '434']:
    t_list = [t for t in trains if t['train_number'] == num]
    print(f"\n=== Train {num} ({len(t_list)} entries) ===")
    for t in t_list:
        st_names = [s['station'] for s in t['stops']]
        has_bq = '板橋' in st_names
        has_tt = '台東' in st_names
        print(f"  Line: {t.get('line')} | {t['origin']} -> {t['dest']} | 板橋: {has_bq}, 台東: {has_tt}")
        print(f"  Stops ({len(st_names)}):", st_names)
