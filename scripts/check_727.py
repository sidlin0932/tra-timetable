# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

t727 = next((t for t in trains if t['train_number'] == '727'), None)
if t727:
    print("727:", t727['origin'], "->", t727['dest'], t727['train_type'])
    for s in t727['stops']:
        print(f"  {s['station']}: {s['time']}")
