# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

# Check 402 in departuresByStation
bq_deps = []
for t in trains:
    for s_idx, s in enumerate(t['stops'][:-1]):
        if s['station'] == '板橋':
            bq_deps.append({
                'train': t,
                'stopIdx': s_idx,
                'depTimeMin': time_to_min(s['time']),
                'depTime': s['time']
            })

bq_deps.sort(key=lambda x: x['depTimeMin'])

print(f"Total Banqiao departures: {len(bq_deps)}")

# Look for 402, 406, 408
for d in bq_deps:
    num = d['train']['train_number']
    if num in ['402', '406', '408', '22', '410', '472', '270']:
        print(f"  Train {num} ({d['train']['train_type']}): dep 板橋 at {d['depTime']} ({d['depTimeMin']}m), dest: {d['train']['dest']}")
        # Check if 台東 is after 板橋
        stops = d['train']['stops']
        st_after = [s['station'] for s in stops[d['stopIdx']+1:]]
        print(f"    Stops after 板橋 ({len(st_after)}): contains 台東 = {'台東' in st_after}")
