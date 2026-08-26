# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

trpass_trains = [t for t in trains if t.get('is_trpass', True)]

# Let's search all possible starting stations for 1-day circular tour
# We want to visit: Northern Mainline -> Western Mainline -> South Link Line -> Taitung Line -> North Link Line -> Northern Mainline

# Let's test from Taipei, Taichung, Kaohsiung, Hualien
# Let's build a general network search for circular tours
def search_circular(start_st, hubs_cw, hubs_ccw):
    print(f"\n==========================================")
    print(f"Searching 1-Day Circular Tours for: {start_st}")
    print(f"==========================================")

    # 1. Clockwise
    cw_success = []
    def dfs_cw(cur_st_idx, cur_time, path):
        if cur_st_idx == len(hubs_cw) - 1:
            # We reached final destination
            last_leg = path[-1]
            cw_success.append(path)
            return

        from_st = hubs_cw[cur_st_idx]
        to_st = hubs_cw[cur_st_idx + 1]

        # Find all direct TR-PASS trains from from_st to to_st
        candidates = []
        for t in trpass_trains:
            st_names = [s['station'] for s in t['stops']]
            if from_st in st_names and to_st in st_names:
                i1 = st_names.index(from_st)
                i2 = st_names.index(to_st)
                if i1 < i2:
                    dep_m = time_to_min(t['stops'][i1]['time'])
                    arr_m = time_to_min(t['stops'][i2]['time'])
                    if dep_m >= cur_time and arr_m > dep_m:
                        candidates.append({
                            'train_no': t['train_number'],
                            'train_type': t['train_type'],
                            'from': from_st,
                            'to': to_st,
                            'dep': t['stops'][i1]['time'],
                            'arr': t['stops'][i2]['time'],
                            'dep_m': dep_m,
                            'arr_m': arr_m
                        })
        for c in candidates:
            dfs_cw(cur_st_idx + 1, c['arr_m'] + 3, path + [c])

    dfs_cw(0, 0, [])
    print(f"Clockwise successful 1-day tours: {len(cw_success)}")
    for s in cw_success[:3]:
        print(f"  Dep {s[0]['dep']} -> Arr {s[-1]['arr']} (Total {(s[-1]['arr_m'] - s[0]['dep_m'])//60}h {(s[-1]['arr_m'] - s[0]['dep_m'])%60}m):")
        for idx, leg in enumerate(s):
            print(f"    Leg {idx+1}: {leg['train_type']} {leg['train_no']} ({leg['from']} {leg['dep']} -> {leg['to']} {leg['arr']})")

    # 2. Counter-Clockwise
    ccw_success = []
    def dfs_ccw(cur_st_idx, cur_time, path):
        if cur_st_idx == len(hubs_ccw) - 1:
            ccw_success.append(path)
            return

        from_st = hubs_ccw[cur_st_idx]
        to_st = hubs_ccw[cur_st_idx + 1]

        candidates = []
        for t in trpass_trains:
            st_names = [s['station'] for s in t['stops']]
            if from_st in st_names and to_st in st_names:
                i1 = st_names.index(from_st)
                i2 = st_names.index(to_st)
                if i1 < i2:
                    dep_m = time_to_min(t['stops'][i1]['time'])
                    arr_m = time_to_min(t['stops'][i2]['time'])
                    if dep_m >= cur_time and arr_m > dep_m:
                        candidates.append({
                            'train_no': t['train_number'],
                            'train_type': t['train_type'],
                            'from': from_st,
                            'to': to_st,
                            'dep': t['stops'][i1]['time'],
                            'arr': t['stops'][i2]['time'],
                            'dep_m': dep_m,
                            'arr_m': arr_m
                        })
        for c in candidates:
            dfs_ccw(cur_st_idx + 1, c['arr_m'] + 3, path + [c])

    dfs_ccw(0, 0, [])
    print(f"Counter-Clockwise successful 1-day tours: {len(ccw_success)}")
    for s in ccw_success[:3]:
        print(f"  Dep {s[0]['dep']} -> Arr {s[-1]['arr']} (Total {(s[-1]['arr_m'] - s[0]['dep_m'])//60}h {(s[-1]['arr_m'] - s[0]['dep_m'])%60}m):")
        for idx, leg in enumerate(s):
            print(f"    Leg {idx+1}: {leg['train_type']} {leg['train_no']} ({leg['from']} {leg['dep']} -> {leg['to']} {leg['arr']})")

# Let's test from Taipei (台北 -> 花蓮 -> 台東 -> 新左營 -> 台北)
search_circular('台北', ['台北', '花蓮', '台東', '新左營', '台北'], ['台北', '新左營', '台東', '花蓮', '台北'])

# Let's test from Kaohsiung (高雄 / 新左營 -> 台北 -> 花蓮 -> 台東 -> 高雄)
search_circular('新左營', ['新左營', '台北', '花蓮', '台東', '新左營'], ['新左營', '台東', '花蓮', '台北', '新左營'])

# Let's test from Hualien (花蓮 -> 台東 -> 新左營 -> 台北 -> 花蓮)
search_circular('花蓮', ['花蓮', '台東', '新左營', '台北', '花蓮'], ['花蓮', '台北', '新左營', '台東', '花蓮'])
