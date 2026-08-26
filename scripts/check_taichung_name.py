# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

# Find all station names containing '中'
tc_names = set()
for t in trains:
    for s in t['stops']:
        if '中' in s['station']:
            tc_names.add(s['station'])

print("Stations with 中:", tc_names)
