import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    if not t or ':' not in t: return -1
    h, m = map(int, t.split(':'))
    return h * 60 + m

orig = '平溪'
dest = '內灣'

# Step 1: Pingxi to Hub1 (瑞芳, 八堵)
leg1_list = []
for t in trains:
    for i, s in enumerate(t['stops']):
        if s['station'] == orig:
            for j in range(i + 1, len(t['stops'])):
                if t['stops'][j]['station'] in ['瑞芳', '八堵']:
                    leg1_list.append({
                        't': t,
                        'dep': s['time'],
                        'h1': t['stops'][j]['station'],
                        'arr1': t['stops'][j]['time']
                    })

# Step 4: Hub3 (竹中, 新竹, 北新竹) to Neiwan
leg4_list = []
for t in trains:
    for i, s in enumerate(t['stops']):
        if s['station'] in ['竹中', '新竹', '北新竹']:
            for j in range(i + 1, len(t['stops'])):
                if t['stops'][j]['station'] == dest:
                    leg4_list.append({
                        't': t,
                        'h3': s['station'],
                        'dep4': s['time'],
                        'arr': t['stops'][j]['time']
                    })

all_combos = []

for l1 in leg1_list:
    h1 = l1['h1']
    arr1 = time_to_min(l1['arr1'])

    for l4 in leg4_list:
        h3 = l4['h3']
        dep4 = time_to_min(l4['dep4'])
        if dep4 <= arr1 + 60: continue

        # 2-transfer path: H1 -> H3 direct
        for t2 in trains:
            idx1 = -1
            idx2 = -1
            for k, s in enumerate(t2['stops']):
                if s['station'] == h1 and idx1 == -1: idx1 = k
                if s['station'] == h3 and idx1 != -1: idx2 = k; break
            if idx1 != -1 and idx2 != -1:
                dep2 = time_to_min(t2['stops'][idx1]['time'])
                arr2 = time_to_min(t2['stops'][idx2]['time'])
                if 5 <= dep2 - arr1 <= 90 and 5 <= dep4 - arr2 <= 90:
                    all_combos.append({
                        'dep': l1['dep'],
                        'arr': l4['arr'],
                        'transfers': 2,
                        'dur': time_to_min(l4['arr']) - time_to_min(l1['dep']),
                        'detail': f"{orig} ({l1['dep']}) ➔ {h1} ➔ {h3} ➔ {dest} ({l4['arr']})"
                    })

        # 3-transfer path: H1 -> H2 (新竹/北新竹) -> H3 (竹中) -> Neiwan
        if h3 == '竹中':
            for t2 in trains:
                idx1 = -1
                idx2 = -1
                for k, s in enumerate(t2['stops']):
                    if s['station'] == h1 and idx1 == -1: idx1 = k
                    if s['station'] in ['新竹', '北新竹'] and idx1 != -1: idx2 = k; break
                if idx1 != -1 and idx2 != -1:
                    dep2 = time_to_min(t2['stops'][idx1]['time'])
                    arr2 = time_to_min(t2['stops'][idx2]['time'])
                    h2 = t2['stops'][idx2]['station']
                    if 5 <= dep2 - arr1 <= 90:
                        for t3 in trains:
                            idx3a = -1
                            idx3b = -1
                            for m, s in enumerate(t3['stops']):
                                if s['station'] == h2 and idx3a == -1: idx3a = m
                                if s['station'] == h3 and idx3a != -1: idx3b = m; break
                            if idx3a != -1 and idx3b != -1:
                                dep3 = time_to_min(t3['stops'][idx3a]['time'])
                                arr3 = time_to_min(t3['stops'][idx3b]['time'])
                                if 5 <= dep3 - arr2 <= 60 and 5 <= dep4 - arr3 <= 60:
                                    all_combos.append({
                                        'dep': l1['dep'],
                                        'arr': l4['arr'],
                                        'transfers': 3,
                                        'dur': time_to_min(l4['arr']) - time_to_min(l1['dep']),
                                        'detail': f"{orig} ({l1['dep']}) ➔ {h1} ➔ {h2} ➔ {h3}(竹中) ➔ {dest} ({l4['arr']})"
                                    })

seen = set()
unique = []
all_combos.sort(key=lambda x: time_to_min(x['dep']))
for c in all_combos:
    k = (c['dep'], c['arr'])
    if k not in seen:
        seen.add(k)
        unique.append(c)

with open('full_chain_result.txt', 'w', encoding='utf-8') as out:
    out.write(f"平溪 ➔ 內灣 完整全日方案（共 {len(unique)} 組）:\n\n")
    for idx, u in enumerate(unique):
        h = u['dur'] // 60
        m = u['dur'] % 60
        out.write(f"{idx+1}. 平溪 {u['dep']} ➔ 內灣 {u['arr']} (耗時 {h}小時{m}分, 轉乘 {u['transfers']} 次)\n   路線: {u['detail']}\n\n")

print(f"Generated {len(unique)} total transfer routes!")
