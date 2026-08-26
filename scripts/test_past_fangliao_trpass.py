# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

# Filter ONLY TR-PASS trains
trpass_trains = [t for t in trains if t.get('is_trpass', True)]

south_link_stations = ['加祿', '內獅', '枋山', '大武', '瀧溪', '金崙', '太麻里', '知本', '康樂', '台東']

# Let's find all TR-PASS trains going into South Link (Eastbound / 南迴東行)
print("=== TR-PASS Eastbound Trains entering South Link ===")
for t in trpass_trains:
    st_names = [s['station'] for s in t['stops']]
    if any(w in st_names for w in ['潮州', '枋寮', '新左營', '高雄']) and any(e in st_names for e in south_link_stations):
        w_idx = min(st_names.index(w) for w in ['潮州', '枋寮', '新左營', '高雄'] if w in st_names)
        e_idx = max(st_names.index(e) for e in south_link_stations if e in st_names)
        if w_idx < e_idx:
            stops_str = ", ".join([f"{s['station']}({s['time']})" for s in t['stops'][w_idx:e_idx+1]])
            print(f"Train {t['train_number']} ({t['train_type']}): {stops_str}")

# Let's find all TR-PASS trains returning from South Link (Westbound / 南迴西行)
print("\n=== TR-PASS Westbound Trains returning from South Link ===")
for t in trpass_trains:
    st_names = [s['station'] for s in t['stops']]
    if any(e in st_names for e in south_link_stations) and any(w in st_names for w in ['潮州', '枋寮', '新左營', '高雄']):
        e_idx = min(st_names.index(e) for e in south_link_stations if e in st_names)
        w_idx = max(st_names.index(w) for w in ['潮州', '枋寮', '新左營', '高雄'] if w in st_names)
        if e_idx < w_idx:
            stops_str = ", ".join([f"{s['station']}({s['time']})" for s in t['stops'][e_idx:w_idx+1]])
            print(f"Train {t['train_number']} ({t['train_type']}): {stops_str}")

# Now, let's test for each south_link_station:
# Can we:
# 1. Start from 板橋 after 00:00 (TR-PASS)
# 2. Reach Station X via Western Line + South Link (TR-PASS)
# 3. Stay at least 3 minutes
# 4. Return to 板橋 before 24:00 (via South Link Westbound + Western Line PP 152 / others)
print("\n=== Testing Round-Trip Feasibility for South Link Stations ===")
# Outbound to Chaozhou:
# 101 次: 板橋 05:47 -> 潮州 11:20 (PP自強)
# 103 次: 板橋 06:37 -> 潮州 12:15 (PP自強)

# Returning from Chaozhou:
# 152 次: 潮州 18:27 -> 板橋 23:53 (PP自強, last train)

for st in south_link_stations:
    # Find all outbound trains from Chaozhou/Fangliao that arrive at st after 11:20 (101次) or 12:15 (103次)
    out_candidates = []
    for t in trpass_trains:
        st_names = [s['station'] for s in t['stops']]
        if '潮州' in st_names and st in st_names:
            i1 = st_names.index('潮州')
            i2 = st_names.index(st)
            if i1 < i2:
                dep_m = time_to_min(t['stops'][i1]['time'])
                arr_m = time_to_min(t['stops'][i2]['time'])
                if dep_m >= 11*60 + 20 and arr_m > dep_m:
                    out_candidates.append({'train_no': t['train_number'], 'train_type': t['train_type'], 'cz_dep': t['stops'][i1]['time'], 'st_arr': t['stops'][i2]['time'], 'arr_m': arr_m})
        elif '枋寮' in st_names and st in st_names:
            i1 = st_names.index('枋寮')
            i2 = st_names.index(st)
            if i1 < i2:
                dep_m = time_to_min(t['stops'][i1]['time'])
                arr_m = time_to_min(t['stops'][i2]['time'])
                # If connected from Chaozhou after 11:20
                if dep_m >= 12*60 and arr_m > dep_m:
                    out_candidates.append({'train_no': t['train_number'], 'train_type': t['train_type'], 'cz_dep': f"枋寮 {t['stops'][i1]['time']}", 'st_arr': t['stops'][i2]['time'], 'arr_m': arr_m})

    # Find returning trains from st to Chaozhou/Fangliao that reach Chaozhou before 18:27 (152次)
    in_candidates = []
    for t in trpass_trains:
        st_names = [s['station'] for s in t['stops']]
        if st in st_names and '潮州' in st_names:
            i1 = st_names.index(st)
            i2 = st_names.index('潮州')
            if i1 < i2:
                dep_m = time_to_min(t['stops'][i1]['time'])
                arr_m = time_to_min(t['stops'][i2]['time'])
                if arr_m <= 18*60 + 27 and dep_m < arr_m:
                    in_candidates.append({'train_no': t['train_number'], 'train_type': t['train_type'], 'st_dep': t['stops'][i1]['time'], 'cz_arr': t['stops'][i2]['time'], 'dep_m': dep_m})
        elif st in st_names and '枋寮' in st_names:
            i1 = st_names.index(st)
            i2 = st_names.index('枋寮')
            if i1 < i2:
                dep_m = time_to_min(t['stops'][i1]['time'])
                arr_m = time_to_min(t['stops'][i2]['time'])
                # Check if there is a connecting train from Fangliao to Chaozhou before 18:27
                if arr_m <= 17*60 + 30 and dep_m < arr_m:
                    in_candidates.append({'train_no': t['train_number'], 'train_type': t['train_type'], 'st_dep': t['stops'][i1]['time'], 'cz_arr': f"枋寮 {t['stops'][i2]['time']}", 'dep_m': dep_m})

    valid_pairs = []
    for o in out_candidates:
        for i in in_candidates:
            if i['dep_m'] >= o['arr_m'] + 3:
                valid_pairs.append((o, i, i['dep_m'] - o['arr_m']))

    if valid_pairs:
        tightest = min(valid_pairs, key=lambda x: x[2])
        longest = max(valid_pairs, key=lambda x: x[2])
        print(f"🎉 【{st}】TR-PASS 可以一日往返！(共 {len(valid_pairs)} 種接駁組合)")
        print(f"   去程: {tightest[0]['train_type']} {tightest[0]['train_no']} ({tightest[0]['cz_dep']} ➔ {st} {tightest[0]['st_arr']})")
        print(f"   停留: {tightest[2]} 分鐘")
        print(f"   回程: {tightest[1]['train_type']} {tightest[1]['train_no']} ({st} {tightest[1]['st_dep']} ➔ {tightest[1]['cz_arr']}) ➔ 接 152 次 (潮州 18:27 ➔ 板橋 23:53)")
    else:
        print(f"❌ 【{st}】TR-PASS 無法一日往返")
