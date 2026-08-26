# -*- coding: utf-8 -*-
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    timetable = json.load(f)

# Find all trains from 內灣
neiwan_trains = []
for t in timetable:
    stations = [s['station'] for s in t['stops']]
    if '內灣' in stations:
        neiwan_trains.append(t)

print(f"Total trains touching 內灣: {len(neiwan_trains)}")
for t in neiwan_trains[:5]:
    st_names = [s['station'] for s in t['stops']]
    print(f"Train {t['train_number']} ({t['train_type']}): {' -> '.join(st_names)}")

# Find all trains from 竹中 to 六家
liujia_trains = []
for t in timetable:
    stations = [s['station'] for s in t['stops']]
    if '竹中' in stations and '六家' in stations:
        idx_z = stations.index('竹中')
        idx_l = stations.index('六家')
        if idx_z < idx_l:
            liujia_trains.append(t)

print(f"\nTotal trains from 竹中 to 六家: {len(liujia_trains)}")
for t in liujia_trains[:5]:
    st_names = [s['station'] for s in t['stops']]
    print(f"Train {t['train_number']} ({t['train_type']}): {' -> '.join(st_names)}")
