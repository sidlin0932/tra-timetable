# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

t281_list = [t for t in trains if t['train_number'] == '281']
print(f"Total 281 entries in JSON: {len(t281_list)}")
for t in t281_list:
    print(f"\nTrain {t['train_number']} ({t['train_type']}): origin {t['origin']} -> dest {t['dest']} | model: {t.get('train_model')} | line: {t.get('line')}")
    print(f"TR-PASS: {t.get('is_trpass')}")
    print("Stops:")
    for s in t['stops']:
        print(f"  {s['station']}: {s['time']}")
