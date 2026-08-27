# -*- coding: utf-8 -*-
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    tt = json.load(f)

def timeToMin(tStr):
    if not tStr: return 0
    h, m = map(int, tStr.split(':'))
    return h * 60 + m

def sort_stops_chronologically(stops):
    if not stops or len(stops) < 2: return stops
    
    # Handle midnight transitions
    # If first stop is late night (e.g. 23:00) and later stops are 00:30, 01:00
    cleaned = []
    seen = set()
    for s in stops:
        if s['station'] not in seen:
            seen.add(s['station'])
            cleaned.append(s)
            
    # Calculate continuous time with rollover
    items = []
    curr_offset = 0
    prev_m = -1
    for s in cleaned:
        m = timeToMin(s['time'])
        if prev_m != -1 and m < prev_m - 300: # gap > 5 hours backwards -> next day
            curr_offset += 1440
        items.append((curr_offset + m, s))
        prev_m = m
        
    items.sort(key=lambda x: x[0])
    return [x[1] for x in items]

fixed_tt = []
for t in tt:
    sorted_stops = sort_stops_chronologically(t['stops'])
    if len(sorted_stops) >= 2:
        t['stops'] = sorted_stops
        t['origin'] = sorted_stops[0]['station']
        t['dest'] = sorted_stops[-1]['station']
        fixed_tt.append(t)

# Check monotonic count
non_monotonic = 0
for t in fixed_tt:
    stops = t['stops']
    last_m = -1
    cross_midnight = False
    for s in stops:
        m = timeToMin(s['time'])
        if last_m != -1 and m < last_m:
            if not cross_midnight and m < 360 and last_m > 1200:
                cross_midnight = True
            elif not cross_midnight:
                non_monotonic += 1
                break
        last_m = m

print(f"Fixed database! Non-monotonic count: {non_monotonic} (out of {len(fixed_tt)} trains)")

with open('full_network_timetable.json', 'w', encoding='utf-8') as f:
    json.dump(fixed_tt, f, ensure_ascii=False, indent=2)

with open('data.js', 'w', encoding='utf-8') as f:
    f.write('window.EMBEDDED_TIMETABLE_DATA = ' + json.dumps(fixed_tt, ensure_ascii=False, indent=2) + ';')

print("Saved clean monotonic database!")
