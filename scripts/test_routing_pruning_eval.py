import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    allTimetableData = json.load(f)

def timeToMin(tStr):
    if not tStr: return 0
    parts = str(tStr).split(':')
    return int(parts[0]) * 60 + int(parts[1])

def getNormalizedArr(dMin, aMin):
    if aMin < dMin: return aMin + 1440
    return aMin

def pruneDominatedRoutes(routes):
    if not routes or len(routes) == 0: return []

    def parseMin(t):
        if not t: return 0
        parts = str(t).split(':')
        return int(parts[0]) * 60 + int(parts[1])

    # 1. Direct routes are always preserved
    directRoutes = [r for r in routes if r['transfers'] == 0]
    directTrainNos = set(str(r['legs'][0]['train_number']) for r in directRoutes)

    # 2. Transfer routes: filter out routes that board a direct train after start (fake transfer)
    validTransferRoutes = []
    for r in routes:
        if r['transfers'] > 0 and len(r['legs']) > 1:
            lastTrainNo = str(r['legs'][-1]['train_number'])
            if lastTrainNo not in directTrainNos:
                validTransferRoutes.append(r)

    # 3. Prune dominated transfer routes (against direct AND against other transfer routes)
    # A route A is dominated by route B if:
    # dep(B) >= dep(A) AND arr(B) <= arr(A)
    # AND (dep(B) > dep(A) OR arr(B) < arr(A) OR transfers(B) < transfers(A))
    allCandidates = directRoutes + validTransferRoutes
    nonDominatedTransfers = []

    for i, r1 in enumerate(validTransferRoutes):
        dep1 = parseMin(r1['dep_time'])
        rawArr1 = parseMin(r1['arr_time'])
        arr1 = getNormalizedArr(dep1, rawArr1)
        tx1 = r1['transfers']
        trainSeq1 = [l['train_number'] for l in r1['legs']]

        dominated = False
        for j, r2 in enumerate(allCandidates):
            if r1 is r2: continue
            dep2 = parseMin(r2['dep_time'])
            rawArr2 = parseMin(r2['arr_time'])
            arr2 = getNormalizedArr(dep2, rawArr2)
            tx2 = r2['transfers']
            trainSeq2 = [l['train_number'] for l in r2['legs']]

            # Check if r2 dominates r1
            if dep2 >= dep1 and arr2 <= arr1:
                # 1) r2 leaves later and arrives same/earlier -> r1 strictly wasted time (slower)
                if dep2 > dep1 and arr2 <= arr1:
                    dominated = True
                    break
                # 2) r2 leaves same and arrives earlier -> r1 strictly slower
                if dep2 == dep1 and arr2 < arr1:
                    dominated = True
                    break
                # 3) r2 leaves same and arrives same
                if dep2 == dep1 and arr2 == arr1:
                    # If r2 has fewer transfers, r1 is worse
                    if tx2 < tx1:
                        dominated = True
                        break
                    # If same transfers, but exact same train sequence, r1 is duplicate
                    elif tx2 == tx1 and trainSeq1 == trainSeq2:
                        dominated = True
                        break
                    # If same departure, same arrival, same transfer count, but DIFFERENT intermediate train/leg:
                    # Keep both as viable alternative options!
                    
        if not dominated:
            nonDominatedTransfers.append(r1)

    return directRoutes + nonDominatedTransfers

# Let's test routing Banqiao to Tainan
print("Testing routing Banqiao -> Tainan...")
# Let's test building the departures index and routing
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

def planRoutes(orig, dest, startTimeMin, viaStation=''):
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

    # 2. Transfer trains (up to 2 transfers = 3 legs)
    maxAllowedHops = 2
    for firstDep in origDeps:
        if firstDep['depTimeMin'] < startTimeMin: continue
        train1 = firstDep['train']

        train1ReachesDest = any(s['station'] == dest for s in train1['stops'][firstDep['stopIdx'] + 1:])
        queue = []

        for j in range(firstDep['stopIdx'] + 1, len(train1['stops'])):
            nextSt = train1['stops'][j]['station']
            arrMin = timeToMin(train1['stops'][j]['time'])
            if arrMin <= firstDep['depTimeMin']: continue
            if train1ReachesDest and nextSt == dest: break
            if nextSt == dest: continue

            if nextSt in KEY_HUBS or nextSt == viaStation or j == len(train1['stops']) - 1:
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
                    for j in range(d['stopIdx'] + 1, len(train['stops'])):
                        nextSt = train['stops'][j]['station']
                        arrMin = timeToMin(train['stops'][j]['time'])
                        if arrMin <= d['depTimeMin']: continue
                        if nextSt in state['visited']: continue

                        if nextSt != dest and nextSt not in KEY_HUBS and nextSt != viaStation and j != len(train['stops']) - 1:
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

    combined = directResults + transferResults
    return pruneDominatedRoutes(combined)

routes = planRoutes('板橋', '台南', timeToMin('06:00'))
print(f"Total optimal routes from 板橋 to 台南 (06:00起): {len(routes)}")
for r in routes[:15]:
    legsStr = ' ➔ '.join([f"{l['train_type']} {l['train_number']}{'['+l['route_dir']+']' if l['route_dir'] else ''} ({l['from']} {l['dep']} -> {l['to']} {l['arr']})" for l in r['legs']])
    print(f"  [{r['dep_time']} -> {r['arr_time']} ({r['duration']}分 / 轉乘{r['transfers']}次)] {legsStr}")
