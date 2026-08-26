# -*- coding: utf-8 -*-
import json
import time

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    timetable = json.load(f)

KEY_HUBS = {
    '基隆', '八堵', '七堵', '南港', '松山', '台北', '板橋', '樹林', '桃園', '中壢',
    '新竹', '竹南', '苗栗', '豐原', '台中', '彰化', '員林', '田中', '二水', '斗六',
    '嘉義', '新營', '善化', '台南', '新左營', '高雄', '鳳山', '屏東', '潮州', '枋寮',
    '瑞芳', '雙溪', '福隆', '頭城', '礁溪', '宜蘭', '羅東', '蘇澳新', '東澳', '南澳',
    '新城(太魯閣)', '花蓮', '壽豐', '鳳林', '光復', '瑞穗', '玉里', '池上', '關山', '台東',
    '知本', '枋山', '竹中', '濁水', '北新竹'
}

def time_to_min(t_str):
    if not t_str: return 0
    h, m = map(int, t_str.split(':'))
    return h * 60 + m

deps_by_st = {}
for t in timetable:
    for i, s in enumerate(t['stops'][:-1]):
        st = s['station']
        if st not in deps_by_st: deps_by_st[st] = []
        deps_by_st[st].append({
            'train': t,
            'stopIdx': i,
            'depMin': time_to_min(s['time'])
        })

for st in deps_by_st:
    deps_by_st[st].sort(key=lambda x: x['depMin'])

def fast_plan_routes(orig, dest, startTimeMin):
    t0 = time.time()
    orig_deps = deps_by_st.get(orig, [])
    direct_results = []
    transfer_results = []
    
    # 1. Direct
    for d1 in orig_deps:
        if d1['depMin'] < startTimeMin: continue
        t1 = d1['train']
        for j in range(d1['stopIdx'] + 1, len(t1['stops'])):
            if t1['stops'][j]['station'] == dest:
                arr_min = time_to_min(t1['stops'][j]['time'])
                if arr_min > d1['depMin']:
                    direct_results.append({
                        'transfers': 0,
                        'dep': t1['stops'][d1['stopIdx']]['time'],
                        'arr': t1['stops'][j]['time'],
                        'duration': arr_min - d1['depMin']
                    })

    # 2. Transfers with Branching Factor Limit = 3
    max_hops = 3
    if len(direct_results) > 20:
        max_hops = 1

    for d1 in orig_deps:
        if d1['depMin'] < startTimeMin: continue
        t1 = d1['train']
        queue = []
        for j in range(d1['stopIdx'] + 1, len(t1['stops'])):
            next_st = t1['stops'][j]['station']
            arr_min = time_to_min(t1['stops'][j]['time'])
            if arr_min <= d1['depMin'] or next_st == dest: continue
            if next_st in KEY_HUBS or j == len(t1['stops']) - 1:
                queue.append({
                    'currentStation': next_st,
                    'currentTimeMin': arr_min,
                    'legs': [{'from': orig, 'to': next_st, 'dep': t1['stops'][d1['stopIdx']]['time'], 'arr': t1['stops'][j]['time']}],
                    'visited': {orig, next_st}
                })

        best_at_station = {}
        for hop in range(1, max_hops + 1):
            next_queue = []
            for state in queue:
                deps = deps_by_st.get(state['currentStation'], [])
                min_dep = state['currentTimeMin'] + 3
                
                # Take only first 3 viable departures
                viable_deps = []
                for d in deps:
                    if d['depMin'] < min_dep: continue
                    if d['depMin'] > min_dep + 75: break
                    viable_deps.append(d)
                    if len(viable_deps) >= 3: break

                for d in viable_deps:
                    t = d['train']
                    for j in range(d['stopIdx'] + 1, len(t['stops'])):
                        next_st = t['stops'][j]['station']
                        arr_min = time_to_min(t['stops'][j]['time'])
                        if arr_min <= d['depMin'] or next_st in state['visited']: continue
                        if next_st != dest and next_st not in KEY_HUBS and j != len(t['stops']) - 1: continue

                        new_legs = state['legs'] + [{'from': state['currentStation'], 'to': next_st, 'dep': t['stops'][d['stopIdx']]['time'], 'arr': t['stops'][j]['time']}]
                        if next_st == dest:
                            transfer_results.append({
                                'transfers': len(new_legs) - 1,
                                'dep': new_legs[0]['dep'],
                                'arr': new_legs[-1]['arr'],
                                'duration': arr_min - time_to_min(new_legs[0]['dep'])
                            })
                        elif hop < max_hops:
                            if next_st not in best_at_station or arr_min < best_at_station[next_st]:
                                best_at_station[next_st] = arr_min
                                next_vis = set(state['visited'])
                                next_vis.add(next_st)
                                next_queue.append({
                                    'currentStation': next_st,
                                    'currentTimeMin': arr_min,
                                    'legs': new_legs,
                                    'visited': next_vis
                                })
            queue = next_queue
            if not queue: break

    t1 = time.time()
    elapsed_ms = (t1 - t0) * 1000
    return direct_results, transfer_results, elapsed_ms

# Test 板橋 -> 台北
d, t, ms = fast_plan_routes('板橋', '台北', 300)
print(f"[Banqiao -> Taipei] Direct: {len(d)}, Transfer: {len(t)}, Time: {ms:.2f}ms")

# Test 台北 -> 內灣
d, t, ms = fast_plan_routes('台北', '內灣', 300)
print(f"[Taipei -> Neiwan] Direct: {len(d)}, Transfer: {len(t)}, Time: {ms:.2f}ms")

# Test 內灣 -> 六家
d, t, ms = fast_plan_routes('內灣', '六家', 300)
print(f"[Neiwan -> Liujia] Direct: {len(d)}, Transfer: {len(t)}, Time: {ms:.2f}ms")
