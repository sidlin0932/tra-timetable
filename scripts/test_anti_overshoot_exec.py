import json
import time

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    allTimetableData = json.load(f)

def timeToMin(tStr):
    if not tStr: return 0
    parts = str(tStr).split(':')
    return int(parts[0]) * 60 + int(parts[1])

# Build departures index
KEY_HUBS = set([
    '基隆', '八堵', '七堵', '南港', '松山', '台北', '板橋', '樹林', '桃園', '中壢',
    '新竹', '竹南', '苗栗', '豐原', '台中', '彰化', '員林', '田中', '二水', '斗六',
    '嘉義', '新營', '善化', '台南', '新左營', '高雄', '鳳山', '屏東', '潮州', '枋寮',
    '瑞芳', '雙溪', '福隆', '頭城', '礁溪', '宜蘭', '羅東', '蘇澳新', '東澳', '南澳',
    '新城(太魯閣)', '花蓮', '壽豐', '鳳林', '光復', '瑞穗', '玉里', '池上', '關山', '台東',
    '知本', '枋山', '竹中', '濁水'
])

departuresByStation = {}
for t in allTimetableData:
    for sIdx, s in enumerate(t['stops']):
        if sIdx < len(t['stops']) - 1:
            st = s['station']
            if st not in departuresByStation: departuresByStation[st] = []
            departuresByStation[st].append({
                'train': t,
                'stopIdx': sIdx,
                'depTimeMin': timeToMin(s['time'])
            })

for st in departuresByStation:
    departuresByStation[st].sort(key=lambda x: x['depTimeMin'])

def planRoutes(orig, dest, startTimeMin=0):
    origDeps = departuresByStation.get(orig, [])
    directResults = []
    transferResults = []

    # 1. Direct trains
    for firstDep in origDeps:
        if firstDep['depTimeMin'] < startTimeMin: continue
        train1 = firstDep['train']
        for j in range(firstDep['stopIdx'] + 1, len(train1['stops'])):
            if train1['stops'][j]['station'] == dest:
                arrMin = timeToMin(train1['stops'][j]['time'])
                if arrMin <= firstDep['depTimeMin']: continue
                leg1 = {
                    'train_number': train1['train_number'],
                    'train_type': train1['train_type'],
                    'route_dir': train1.get('route_dir', ''),
                    'from': orig,
                    'to': dest,
                    'dep': train1['stops'][firstDep['stopIdx']]['time'],
                    'arr': train1['stops'][j]['time']
                }
                directResults.append({
                    'transfers': 0,
                    'dep_time': leg1['dep'],
                    'arr_time': leg1['arr'],
                    'duration': arrMin - firstDep['depTimeMin'],
                    'legs': [leg1]
                })

    # 2. Transfer trains with strict anti-overshoot / zero-backtrack
    maxAllowedHops = 2
    for firstDep in origDeps:
        if firstDep['depTimeMin'] < startTimeMin: continue
        train1 = firstDep['train']
        queue = []

        # Check if train1 stops at dest at or beyond stopIdx
        destIdxInTrain1 = -1
        for k in range(firstDep['stopIdx'] + 1, len(train1['stops'])):
            if train1['stops'][k]['station'] == dest:
                destIdxInTrain1 = k
                break

        for j in range(firstDep['stopIdx'] + 1, len(train1['stops'])):
            nextSt = train1['stops'][j]['station']
            arrMin = timeToMin(train1['stops'][j]['time'])
            if arrMin <= firstDep['depTimeMin']: continue
            
            # Anti-Overshoot Rule 1: If train1 stops at dest, never travel at or beyond dest to transfer!
            if destIdxInTrain1 != -1 and j >= destIdxInTrain1:
                break
            if nextSt == dest: continue

            if nextSt in KEY_HUBS or j == len(train1['stops']) - 1:
                leg1 = {
                    'train_number': train1['train_number'],
                    'train_type': train1['train_type'],
                    'route_dir': train1.get('route_dir', ''),
                    'from': orig,
                    'to': nextSt,
                    'dep': train1['stops'][firstDep['stopIdx']]['time'],
                    'arr': train1['stops'][j]['time']
                }
                queue.append({
                    'currentStation': nextSt,
                    'currentTimeMin': arrMin,
                    'legs': [leg1],
                    'visited': set([orig, nextSt])
                })

        stationVisits = {}
        for hop in range(1, maxAllowedHops + 1):
            nextQueue = []
            for state in queue:
                deps = departuresByStation.get(state['currentStation'], [])
                minDep = state['currentTimeMin'] + 3
                for d in deps:
                    if d['depTimeMin'] < minDep: continue
                    if d['depTimeMin'] > minDep + 75: break
                    if d['train']['train_number'] == state['legs'][-1]['train_number']: continue

                    train = d['train']
                    
                    # Anti-Backtracking Rule 2: train must not head back towards orig or any earlier visited station
                    # Check if train has any visited station after stopIdx
                    subsequentStops = set(s['station'] for s in train['stops'][d['stopIdx']:])
                    if any(prevSt in subsequentStops for prevSt in state['visited'] if prevSt != state['currentStation']):
                        continue # Reversing direction on same line / backtracking!

                    for j in range(d['stopIdx'] + 1, len(train['stops'])):
                        nextSt = train['stops'][j]['station']
                        arrMin = timeToMin(train['stops'][j]['time'])
                        if arrMin <= d['depTimeMin']: continue
                        if nextSt in state['visited']: continue

                        if nextSt != dest and nextSt not in KEY_HUBS and j != len(train['stops']) - 1:
                            continue

                        newLeg = {
                            'train_number': train['train_number'],
                            'train_type': train['train_type'],
                            'route_dir': train.get('route_dir', ''),
                            'from': state['currentStation'],
                            'to': nextSt,
                            'dep': train['stops'][d['stopIdx']]['time'],
                            'arr': train['stops'][j]['time']
                        }
                        newLegs = state['legs'] + [newLeg]

                        if nextSt == dest:
                            transferResults.append({
                                'transfers': len(newLegs) - 1,
                                'dep_time': newLegs[0]['dep'],
                                'arr_time': newLeg['arr'],
                                'duration': arrMin - timeToMin(newLegs[0]['dep']),
                                'legs': newLegs
                            })
                        elif hop < maxAllowedHops:
                            count = stationVisits.get(nextSt, 0)
                            if count < 3:
                                stationVisits[nextSt] = count + 1
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

    return directResults + transferResults

# Test Taipei -> Yingge
res_ty = planRoutes('台北', '鶯歌', 0)
print(f"Taipei -> Yingge total routes: {len(res_ty)}")
for r in res_ty[:10]:
    legsStr = ' ➔ '.join([f"{l['train_type']} {l['train_number']} ({l['from']} {l['dep']} -> {l['to']} {l['arr']})" for l in r['legs']])
    print(f"  [{r['dep_time']} -> {r['arr_time']} ({r['duration']}分 / 轉乘{r['transfers']}次)] {legsStr}")

# Check if any route went to Taoyuan
went_to_taoyuan = [r for r in res_ty if any(l['to'] == '桃園' or l['from'] == '桃園' for l in r['legs'])]
print(f"Routes overshooting to Taoyuan and doubling back: {len(went_to_taoyuan)} (Expected: 0)")
