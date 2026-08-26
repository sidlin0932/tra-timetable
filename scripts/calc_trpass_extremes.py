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
print(f"Total TR-PASS eligible trains: {len(trpass_trains)}")

# Build departure index for TR-PASS trains only
deps_by_st = {}
for t in trpass_trains:
    for s_idx, s in enumerate(t['stops'][:-1]):
        st = s['station']
        if st not in deps_by_st: deps_by_st[st] = []
        deps_by_st[st].append({
            'train': t,
            'stopIdx': s_idx,
            'depMin': time_to_min(s['time']),
            'depTime': s['time']
        })

for st in deps_by_st:
    deps_by_st[st].sort(key=lambda x: x['depMin'])

# Function to search TR-PASS routes between orig and dest (max 3 transfers)
def find_trpass_routes(orig, dest, start_m=0, max_transfers=2):
    results = []
    queue = []
    
    # 0 transfers (direct)
    for d in deps_by_st.get(orig, []):
        if d['depMin'] < start_m: continue
        t = d['train']
        s_idx = d['stopIdx']
        for j in range(s_idx + 1, len(t['stops'])):
            nxt_st = t['stops'][j]['station']
            arr_m = time_to_min(t['stops'][j]['time'])
            if arr_m <= d['depMin']: continue
            leg = {
                'train_no': t['train_number'],
                'train_type': t['train_type'],
                'from': orig,
                'to': nxt_st,
                'dep': t['stops'][s_idx]['time'],
                'arr': t['stops'][j]['time'],
                'dep_m': d['depMin'],
                'arr_m': arr_m
            }
            if nxt_st == dest:
                results.append([leg])
            elif max_transfers > 0 and len(queue) < 100:
                queue.append({'current': nxt_st, 'arr_m': arr_m, 'legs': [leg], 'visited': set([orig, nxt_st])})

    # 1 or 2 transfers
    for hop in range(max_transfers):
        next_queue = []
        for state in queue:
            for d in deps_by_st.get(state['current'], []):
                if d['depMin'] < state['arr_m'] + 3: continue
                if d['depMin'] > state['arr_m'] + 90: continue
                t = d['train']
                if t['train_number'] == state['legs'][-1]['train_no']: continue
                s_idx = d['stopIdx']
                for j in range(s_idx + 1, len(t['stops'])):
                    nxt_st = t['stops'][j]['station']
                    arr_m = time_to_min(t['stops'][j]['time'])
                    if arr_m <= d['depMin']: continue
                    if nxt_st in state['visited']: continue
                    leg = {
                        'train_no': t['train_number'],
                        'train_type': t['train_type'],
                        'from': state['current'],
                        'to': nxt_st,
                        'dep': t['stops'][s_idx]['time'],
                        'arr': t['stops'][j]['time'],
                        'dep_m': d['depMin'],
                        'arr_m': arr_m
                    }
                    new_legs = state['legs'] + [leg]
                    if nxt_st == dest:
                        results.append(new_legs)
                    elif hop < max_transfers - 1 and len(next_queue) < 100:
                        next_vis = set(state['visited'])
                        next_vis.add(nxt_st)
                        next_queue.append({'current': nxt_st, 'arr_m': arr_m, 'legs': new_legs, 'visited': next_vis})
        queue = next_queue
        if not queue: break

    return results

# Let's test all candidate stations in East and West
east_candidates = ['花蓮', '吉安', '志學', '壽豐', '鳳林', '光復', '瑞穗', '玉里', '富里', '池上', '關山', '鹿野', '台東', '知本', '太麻里', '金崙', '大武', '枋寮']
west_candidates = ['台中', '彰化', '員林', '斗六', '嘉義', '新營', '台南', '新左營', '高雄', '鳳山', '屏東', '潮州', '南州', '林邊', '佳冬', '枋寮', '加祿', '內獅', '枋山']

print("\n=== Testing TR-PASS Eastbound Round-Trips from 板橋 ===")
east_trpass_results = {}
for st in east_candidates:
    # Outbound (板橋 -> st)
    outs = find_trpass_routes('板橋', st, start_m=0, max_transfers=2)
    # Inbound (st -> 板橋)
    ins = find_trpass_routes(st, '板橋', start_m=0, max_transfers=2)
    
    valid_trips = []
    for o in outs:
        arr_st_m = o[-1]['arr_m']
        for i in ins:
            dep_st_m = i[0]['dep_m']
            stay_m = dep_st_m - arr_st_m
            if stay_m >= 3 and i[-1]['arr_m'] <= 1440:
                valid_trips.append((o, i, stay_m))
    
    if valid_trips:
        valid_trips.sort(key=lambda x: x[2]) # tightest first
        tightest = valid_trips[0]
        longest = max(valid_trips, key=lambda x: x[2])
        east_trpass_results[st] = {
            'tightest': tightest,
            'longest': longest,
            'count': len(valid_trips)
        }
        print(f"✅ 【{st}】可 TR-PASS 當日折返！(共 {len(valid_trips)} 種組合, 停留 {tightest[2]}分 ~ {longest[2]//60}h {longest[2]%60}m)")
    else:
        print(f"❌ 【{st}】TR-PASS 無法一日折返")

print("\n=== Testing TR-PASS Westbound Round-Trips from 板橋 ===")
west_trpass_results = {}
for st in west_candidates:
    outs = find_trpass_routes('板橋', st, start_m=0, max_transfers=2)
    ins = find_trpass_routes(st, '板橋', start_m=0, max_transfers=2)
    
    valid_trips = []
    for o in outs:
        arr_st_m = o[-1]['arr_m']
        for i in ins:
            dep_st_m = i[0]['dep_m']
            stay_m = dep_st_m - arr_st_m
            if stay_m >= 3 and i[-1]['arr_m'] <= 1440:
                valid_trips.append((o, i, stay_m))
    
    if valid_trips:
        valid_trips.sort(key=lambda x: x[2])
        tightest = valid_trips[0]
        longest = max(valid_trips, key=lambda x: x[2])
        west_trpass_results[st] = {
            'tightest': tightest,
            'longest': longest,
            'count': len(valid_trips)
        }
        print(f"✅ 【{st}】可 TR-PASS 當日折返！(共 {len(valid_trips)} 種組合, 停留 {tightest[2]}分 ~ {longest[2]//60}h {longest[2]%60}m)")
    else:
        print(f"❌ 【{st}】TR-PASS 無法一日折返")
