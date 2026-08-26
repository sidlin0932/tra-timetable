# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

tc_trains = [t for t in trains if any(s['station'] == '台中' for s in t['stops'])]
print(f"Total trains stopping at 台中: {len(tc_trains)}")
for t in tc_trains[:5]:
    st_names = [s['station'] for s in t['stops']]
    print(t['train_number'], t['train_type'], t['line'], st_names)
