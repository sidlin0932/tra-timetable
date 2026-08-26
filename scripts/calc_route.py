import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    if not t or ':' not in t: return -1
    h, m = map(int, t.split(':'))
    return h * 60 + m

orig = '平溪'
dest = '內灣'
h1_set = {'八堵', '七堵', '瑞芳'}
h2_set = {'新竹', '北新竹', '竹中'}

trains_from_pingxi = []
for t in trains:
    for i, s in enumerate(t['stops']):
        if s['station'] == orig:
            for j in range(i + 1, len(t['stops'])):
                st_name = t['stops'][j]['station']
                if st_name in h1_set:
                    trains_from_pingxi.append({
                        'train': t,
                        'dep': s['time'],
                        'arr_st': st_name,
                        'arr': t['stops'][j]['time'],
                    })

trains_to_neiwan = []
for t in trains:
    for j, s in enumerate(t['stops']):
        if s['station'] == dest:
            for i in range(j):
                st_name = t['stops'][i]['station']
                if st_name in h2_set:
                    trains_to_neiwan.append({
                        'train': t,
                        'dep_st': st_name,
                        'dep': t['stops'][i]['time'],
                        'arr': s['time'],
                    })

routes = []
for leg1 in trains_from_pingxi:
    h1 = leg1['arr_st']
    arr1_min = time_to_min(leg1['arr'])

    for leg3 in trains_to_neiwan:
        h2 = leg3['dep_st']
        dep3_min = time_to_min(leg3['dep'])
        if dep3_min <= arr1_min + 30: continue

        for t2 in trains:
            idx1 = -1
            idx2 = -1
            for k, s in enumerate(t2['stops']):
                if s['station'] == h1 and idx1 == -1: idx1 = k
                if s['station'] == h2 and idx1 != -1: idx2 = k; break

            if idx1 != -1 and idx2 != -1:
                dep2_min = time_to_min(t2['stops'][idx1]['time'])
                arr2_min = time_to_min(t2['stops'][idx2]['time'])
                lay1 = dep2_min - arr1_min
                lay2 = dep3_min - arr2_min

                if 3 <= lay1 <= 80 and 3 <= lay2 <= 80:
                    routes.append({
                        'dep': leg1['dep'],
                        'arr': leg3['arr'],
                        'duration': time_to_min(leg3['arr']) - time_to_min(leg1['dep']),
                        'leg1_name': f"{leg1['train']['train_type']} {leg1['train']['train_number']}次",
                        'leg1_time': f"{orig} {leg1['dep']} ➔ {h1} {leg1['arr']}",
                        'h1': h1,
                        'lay1': lay1,
                        'leg2_name': f"{t2['train_type']} {t2['train_number']}次",
                        'leg2_time': f"{h1} {t2['stops'][idx1]['time']} ➔ {h2} {t2['stops'][idx2]['time']}",
                        'h2': h2,
                        'lay2': lay2,
                        'leg3_name': f"{leg3['train']['train_type']} {leg3['train']['train_number']}次",
                        'leg3_time': f"{h2} {leg3['dep']} ➔ {dest} {leg3['arr']}"
                    })

routes.sort(key=lambda r: time_to_min(r['dep']))

seen = set()
unique_routes = []
for r in routes:
    key = (r['dep'], r['arr'])
    if key not in seen:
        seen.add(key)
        unique_routes.append(r)

with open('pingxi_to_neiwan_result.txt', 'w', encoding='utf-8') as out:
    out.write(f"=== 平溪 ➔ 內灣 完整接駁方案（共 {len(unique_routes)} 組）===\n\n")
    for idx, r in enumerate(unique_routes):
        h = r['duration'] // 60
        m = r['duration'] % 60
        out.write(f"【方案 {idx+1}】平溪 {r['dep']} 出發 ➔ 內灣 {r['arr']} 抵達 (總耗時 {h}小時{m}分)\n")
        out.write(f"  1. 平溪線: {r['leg1_name']} [{r['leg1_time']}]\n")
        out.write(f"     ⏳ 在【{r['h1']}】站轉乘，等候 {r['lay1']} 分鐘\n")
        out.write(f"  2. 西部幹線: {r['leg2_name']} [{r['leg2_time']}]\n")
        out.write(f"     ⏳ 在【{r['h2']}】站轉乘，等候 {r['lay2']} 分鐘\n")
        out.write(f"  3. 內灣線: {r['leg3_name']} [{r['leg3_time']}]\n\n")

print(f"Calculated {len(unique_routes)} routes successfully!")
