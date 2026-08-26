# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

t101 = next((t for t in trains if t['train_number'] == '101'), None)
if t101:
    print("101:", t101['origin'], "->", t101['dest'], t101['train_type'])
    for s in t101['stops']:
        if s['station'] in ['板橋', '新左營', '高雄', '屏東', '潮州']:
            print(f"  {s['station']}: {s['time']}")
