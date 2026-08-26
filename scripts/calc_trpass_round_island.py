# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

# Filter only TR-PASS eligible trains
trpass_trains = [t for t in trains if t.get('is_trpass', True)]
print(f"Total trains: {len(trains)}, TR-PASS eligible: {len(trpass_trains)}")

# Function to get all direct legs between two stations for TR-PASS
def get_trpass_legs(f_st, t_st, min_time=0):
    legs = []
    for t in trpass_trains:
        stops = t['stops']
        st_names = [s['station'] for s in stops]
        if f_st in st_names and t_st in st_names:
            i1 = st_names.index(f_st)
            i2 = st_names.index(t_st)
            if i1 < i2:
                dep_m = time_to_min(stops[i1]['time'])
                arr_m = time_to_min(stops[i2]['time'])
                if dep_m >= min_time and arr_m > dep_m:
                    legs.append({
                        'train_no': t['train_number'],
                        'train_type': t['train_type'],
                        'origin': t['origin'],
                        'dest': t['dest'],
                        'from': f_st,
                        'to': t_st,
                        'dep': stops[i1]['time'],
                        'arr': stops[i2]['time'],
                        'dep_min': dep_m,
                        'arr_min': arr_m,
                        'duration': arr_m - dep_m
                    })
    legs.sort(key=lambda x: x['dep_min'])
    return legs

# Test 1: Clockwise (順時針: 台北/板橋 -> 花蓮 -> 台東 -> 枋寮/潮州/新左營 -> 台北/板橋)
# Let's test routes via major hubs
print("\n=== Checking Clockwise (順時針: 台北 -> 花蓮 -> 台東 -> 潮州 -> 台北) ===")
cw_plans = []
# Leg 1: 台北 -> 花蓮
leg1_list = get_trpass_legs('台北', '花蓮', 0)
for l1 in leg1_list:
    # Leg 2: 花蓮 -> 台東
    leg2_list = get_trpass_legs('花蓮', '台東', l1['arr_min'] + 3)
    for l2 in leg2_list:
        # Leg 3: 台東 -> 潮州
        leg3_list = get_trpass_legs('台東', '潮州', l2['arr_min'] + 3)
        for l3 in leg3_list:
            # Leg 4: 潮州 -> 台北
            leg4_list = get_trpass_legs('潮州', '台北', l3['arr_min'] + 3)
            for l4 in leg4_list:
                total_dur = l4['arr_min'] - l1['dep_min']
                cw_plans.append({
                    'dep': l1['dep'],
                    'arr': l4['arr'],
                    'dur': total_dur,
                    'legs': [l1, l2, l3, l4]
                })

print(f"Clockwise (台北 -> 花蓮 -> 台東 -> 潮州 -> 台北) complete 1-day tours: {len(cw_plans)}")
for p in cw_plans[:5]:
    print(f"\nDep {p['dep']} -> Arr {p['arr']} (Total {p['dur']//60}h {p['dur']%60}m):")
    for idx, l in enumerate(p['legs']):
        print(f"  Leg {idx+1}: {l['train_type']} {l['train_no']} ({l['from']} {l['dep']} -> {l['to']} {l['arr']})")

# Test 2: Counter-Clockwise (逆時針: 台北 -> 潮州 -> 台東 -> 花蓮 -> 台北)
print("\n=== Checking Counter-Clockwise (逆時針: 台北 -> 潮州 -> 台東 -> 花蓮 -> 台北) ===")
ccw_plans = []
# Leg 1: 台北 -> 潮州
leg1_list = get_trpass_legs('台北', '潮州', 0)
for l1 in leg1_list:
    # Leg 2: 潮州 -> 台東
    leg2_list = get_trpass_legs('潮州', '台東', l1['arr_min'] + 3)
    for l2 in leg2_list:
        # Leg 3: 台東 -> 花蓮
        leg3_list = get_trpass_legs('台東', '花蓮', l2['arr_min'] + 3)
        for l3 in leg3_list:
            # Leg 4: 花蓮 -> 台北
            leg4_list = get_trpass_legs('花蓮', '台北', l3['arr_min'] + 3)
            for l4 in leg4_list:
                total_dur = l4['arr_min'] - l1['dep_min']
                ccw_plans.append({
                    'dep': l1['dep'],
                    'arr': l4['arr'],
                    'dur': total_dur,
                    'legs': [l1, l2, l3, l4]
                })

print(f"Counter-Clockwise (台北 -> 潮州 -> 台東 -> 花蓮 -> 台北) complete 1-day tours: {len(ccw_plans)}")
for p in ccw_plans[:5]:
    print(f"\nDep {p['dep']} -> Arr {p['arr']} (Total {p['dur']//60}h {p['dur']%60}m):")
    for idx, l in enumerate(p['legs']):
        print(f"  Leg {idx+1}: {l['train_type']} {l['train_no']} ({l['from']} {l['dep']} -> {l['to']} {l['arr']})")

