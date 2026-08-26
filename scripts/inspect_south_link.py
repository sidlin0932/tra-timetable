# -*- coding: utf-8 -*-
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

# Look at South-link line trains (新左營 -> 台東 / 花蓮)
south_link_eastbound = []
for t in trains:
    st_names = [s['station'] for s in t['stops']]
    if any(s in st_names for s in ['高雄', '新左營', '屏東', '潮州']) and any(s in st_names for s in ['台東', '知本', '枋寮']):
        south_link_eastbound.append((t['train_number'], t['origin'], t['dest'], st_names[:5], st_names[-5:]))

print(f"South Link Eastbound/Westbound candidates: {len(south_link_eastbound)}")
for s in south_link_eastbound:
    print(s)
