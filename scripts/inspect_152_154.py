# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

# Check if 154 or 152 appears in planRoutes('潮州', '板橋', 0)
# Let's check exactly how departuresByStation is built in JS!

departuresByStation = {}
for t in trains:
    for s_idx, s in enumerate(t['stops'][:-1]):
        st = s['station']
        if st not in departuresByStation: departuresByStation[st] = []
        departuresByStation[st].append({
            'train': t,
            'stopIdx': s_idx,
            'depTimeMin': time_to_min(s['time'])
        })

for st in departuresByStation:
    departuresByStation[st].sort(key=lambda x: x['depTimeMin'])

print("Chaozhou departures count:", len(departuresByStation.get('潮州', [])))

# Find 154 in Chaozhou departures
cz_154 = [d for d in departuresByStation.get('潮州', []) if d['train']['train_number'] == '154']
print("154 in Chaozhou departures:", cz_154)

# Find 152 in Chaozhou departures
cz_152 = [d for d in departuresByStation.get('潮州', []) if d['train']['train_number'] == '152']
print("152 in Chaozhou departures:", cz_152)

# Check stops of 152 in JSON
t152 = next((t for t in trains if t['train_number'] == '152'), None)
print("152 stops:", t152['stops'] if t152 else None)
