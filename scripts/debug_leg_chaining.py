# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

# Let's check planRoutes('台東', '潮州', 0)
deps_by_st = {}
for t in trains:
    for s_idx, s in enumerate(t['stops'][:-1]):
        st = s['station']
        if st not in deps_by_st: deps_by_st[st] = []
        deps_by_st[st].append({
            'train': t,
            'stopIdx': s_idx,
            'depTimeMin': time_to_min(s['time'])
        })

for st in deps_by_st:
    deps_by_st[st].sort(key=lambda x: x['depTimeMin'])

KEY_HUBS = set([
    '基隆', '八堵', '七堵', '南港', '松山', '台北', '板橋', '樹林', '桃園', '中壢',
    '新竹', '竹南', '苗栗', '豐原', '台中', '彰化', '員林', '田中', '二水', '斗六',
    '嘉義', '新營', '善化', '台南', '新左營', '高雄', '鳳山', '屏東', '潮州', '枋寮',
    '瑞芳', '雙溪', '福隆', '頭城', '礁溪', '宜蘭', '羅東', '蘇澳新', '東澳', '南澳',
    '新城(太魯閣)', '花蓮', '壽豐', '鳳林', '光復', '瑞穗', '玉里', '池上', '關山', '台東',
    '知本', '枋山', '竹中', '濁水'
])

def plan_routes(orig, dest, start_min):
    orig_deps = deps_by_st.get(orig, [])
    all_results = []
    
    for first_dep in orig_deps:
        if first_dep['depTimeMin'] < start_min: continue
        train1 = first_dep['train']
        queue = []
        for j in range(first_dep['stopIdx'] + 1, len(train1['stops'])):
            next_st = train1['stops'][j]['station']
            arr_min = time_to_min(train1['stops'][j]['time'])
            if arr_min <= first_dep['depTimeMin']: continue
            
            leg1 = {
                'train_number': train1['train_number'],
                'train_type': train1['train_type'],
                'from': orig,
                'to': next_st,
                'dep': train1['stops'][first_dep['stopIdx']]['time'],
                'arr': train1['stops'][j]['time'],
                'layover': 0,
                'all_stops': train1['stops'][first_dep['stopIdx']:j+1]
            }
            if next_st == dest:
                all_results.append({
                    'transfers': 0,
                    'dep_time': leg1['dep'],
                    'arr_time': leg1['arr'],
                    'duration': arr_min - first_dep['depTimeMin'],
                    'legs': [leg1]
                })
            elif len(queue) < 100 and (next_st in KEY_HUBS or j == len(train1['stops']) - 1):
                queue.append({
                    'currentStation': next_st,
                    'currentTimeMin': arr_min,
                    'legs': [leg1],
                    'visited': set([orig, next_st])
                })
    return all_results

r1 = plan_routes('台東', '潮州', 0)
r2 = plan_routes('潮州', '板橋', 0)

print(f"Leg 1 (台東 -> 潮州): {len(r1)} routes")
for r in r1[:5]:
    print(" ", r['legs'][0]['train_number'], r['dep_time'], "->", r['arr_time'])
print("  Last 3 of Leg 1:")
for r in r1[-3:]:
    print(" ", r['legs'][0]['train_number'], r['dep_time'], "->", r['arr_time'])

print(f"\nLeg 2 (潮州 -> 板橋): {len(r2)} routes")
for r in r2:
    if r['legs'][0]['train_number'] in ['154', '152', '168', '146', '445']:
        print(" ", r['legs'][0]['train_number'], r['dep_time'], "->", r['arr_time'])
