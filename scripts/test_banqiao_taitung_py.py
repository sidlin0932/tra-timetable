# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

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

def planRoutes(orig, dest, startTimeMin, viaStation=''):
    origDeps = deps_by_st.get(orig, [])
    allResults = []

    for firstDep in origDeps:
        if firstDep['depTimeMin'] < startTimeMin: continue
        train1 = firstDep['train']
        queue = []

        for j in range(firstDep['stopIdx'] + 1, len(train1['stops'])):
            nextSt = train1['stops'][j]['station']
            arrMin = time_to_min(train1['stops'][j]['time'])
            if arrMin <= firstDep['depTimeMin']: continue

            leg1 = {
                'train_number': train1['train_number'],
                'train_type': train1['train_type'],
                'from': orig,
                'to': nextSt,
                'dep': train1['stops'][firstDep['stopIdx']]['time'],
                'arr': train1['stops'][j]['time']
            }

            if nextSt == dest:
                allResults.append({
                    'transfers': 0,
                    'dep_time': leg1['dep'],
                    'arr_time': leg1['arr'],
                    'duration': arrMin - firstDep['depTimeMin'],
                    'legs': [leg1]
                })
            elif len(queue) < 50 and (nextSt in KEY_HUBS or nextSt == viaStation or j == len(train1['stops']) - 1):
                queue.append({
                    'currentStation': nextSt,
                    'currentTimeMin': arrMin,
                    'legs': [leg1],
                    'visited': set([orig, nextSt])
                })

        for hop in range(1, 4):
            nextQueue = []
            for state in queue:
                deps = deps_by_st.get(state['currentStation'], [])
                minDep = state['currentTimeMin'] + 3
                for d in deps:
                    if d['depTimeMin'] < minDep: continue
                    if d['depTimeMin'] > minDep + 90: continue
                    train = d['train']
                    if train['train_number'] == state['legs'][-1]['train_number']: continue

                    for j in range(d['stopIdx'] + 1, len(train['stops'])):
                        nextSt = train['stops'][j]['station']
                        arrMin = time_to_min(train['stops'][j]['time'])
                        if arrMin <= d['depTimeMin']: continue
                        if nextSt in state['visited']: continue
                        if nextSt != dest and nextSt not in KEY_HUBS and nextSt != viaStation and j != len(train['stops']) - 1: continue

                        newLeg = {
                            'train_number': train['train_number'],
                            'train_type': train['train_type'],
                            'from': state['currentStation'],
                            'to': nextSt,
                            'dep': train['stops'][d['stopIdx']]['time'],
                            'arr': train['stops'][j]['time']
                        }
                        newLegs = state['legs'] + [newLeg]

                        if nextSt == dest:
                            allResults.append({
                                'transfers': len(newLegs) - 1,
                                'dep_time': newLegs[0]['dep'],
                                'arr_time': newLeg['arr'],
                                'duration': arrMin - time_to_min(newLegs[0]['dep']),
                                'legs': newLegs
                            })
                        elif hop < 3:
                            nextVis = set(state['visited'])
                            nextVis.add(nextSt)
                            nextQueue.append({
                                'currentStation': nextSt,
                                'currentTimeMin': arrMin,
                                'legs': newLegs,
                                'visited': nextVis
                            })
            queue = nextQueue
            if not queue: break

    return allResults

results = planRoutes('板橋', '台東', 300)
print(f"Total routes from 板橋 to 台東: {len(results)}")

# Sort by arr_time ascending (earliest arrival first)
results.sort(key=lambda x: (time_to_min(x['arr_time']), x['duration']))

print("\n=== Top 10 Earliest Arrivals in Python ===")
for r in results[:10]:
    legs_str = " -> ".join([f"{l['train_type']} {l['train_number']} ({l['from']} {l['dep']} -> {l['to']} {l['arr']})" for l in r['legs']])
    print(f"Dep {r['dep_time']} -> Arr {r['arr_time']} ({r['duration']}min, transfers: {r['transfers']}) | {legs_str}")
