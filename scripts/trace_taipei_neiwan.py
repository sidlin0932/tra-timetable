# -*- coding: utf-8 -*-
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    timetable = json.load(f)

print(f"Total trains: {len(timetable)}")

# Let's inspect planRoutes for 台北 -> 內灣
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

orig = '台北'
dest = '內灣'
startTimeMin = 300 # 05:00

# Let's trace how 台北 -> 內灣 runs
all_results = []
orig_deps = deps_by_st.get(orig, [])

for d1 in orig_deps:
    if d1['depMin'] < startTimeMin: continue
    t1 = d1['train']
    queue = []
    
    for j in range(d1['stopIdx'] + 1, len(t1['stops'])):
        next_st = t1['stops'][j]['station']
        arr_min = time_to_min(t1['stops'][j]['time'])
        if arr_min <= d1['depMin']: continue
        
        leg1 = {'from': orig, 'to': next_st, 'dep': t1['stops'][d1['stopIdx']]['time'], 'arr': t1['stops'][j]['time'], 'train': t1['train_number']}
        
        if next_st == dest:
            all_results.append([leg1])
        elif next_st in KEY_HUBS or j == len(t1['stops']) - 1:
            queue.append({
                'currentStation': next_st,
                'currentTimeMin': arr_min,
                'legs': [leg1],
                'visited': {orig, next_st}
            })
            
    # BFS hops
    best_at_station = {}
    for hop in range(1, 4):
        next_queue = []
        for state in queue:
            deps = deps_by_st.get(state['currentStation'], [])
            min_dep = state['currentTimeMin'] + 3
            
            for d in deps:
                if d['depMin'] < min_dep: continue
                if d['depMin'] > min_dep + 90: break
                t = d['train']
                if t['train_number'] == state['legs'][-1]['train']: continue
                
                for j in range(d['stopIdx'] + 1, len(t['stops'])):
                    next_st = t['stops'][j]['station']
                    arr_min = time_to_min(t['stops'][j]['time'])
                    if arr_min <= d['depMin']: continue
                    if next_st in state['visited']: continue
                    
                    if next_st != dest and next_st not in KEY_HUBS and j != len(t['stops']) - 1:
                        continue
                        
                    new_leg = {'from': state['currentStation'], 'to': next_st, 'dep': t['stops'][d['stopIdx']]['time'], 'arr': t['stops'][j]['time'], 'train': t['train_number']}
                    new_legs = state['legs'] + [new_leg]
                    
                    if next_st == dest:
                        all_results.append(new_legs)
                    elif hop < 3:
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

print(f"Found {len(all_results)} routes from 台北 to 內灣!")
for r in all_results[:5]:
    path = " -> ".join([f"{l['from']}({l['dep']})-[{l['train']}]->{l['to']}({l['arr']})" for l in r])
    print(f"  Route: {path}")
