import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t_str):
    if not t_str: return 0
    h, m = map(int, t_str.split(':'))
    return h * 60 + m

def plan_leg(orig, dest, start_min=0):
    res = []
    for t in trains:
        stops = t['stops']
        st_names = [s['station'] for s in stops]
        if orig in st_names and dest in st_names:
            i1 = st_names.index(orig)
            i2 = st_names.index(dest)
            if i1 < i2:
                d_min = time_to_min(stops[i1]['time'])
                a_min = time_to_min(stops[i2]['time'])
                if d_min >= start_min:
                    res.append({
                        'train_number': t['train_number'],
                        'train_type': t['train_type'],
                        'dep': stops[i1]['time'],
                        'arr': stops[i2]['time'],
                        'dep_min': d_min,
                        'arr_min': a_min,
                        'duration': a_min - d_min,
                        'transfers': 0,
                        'legs': [{
                            'train_number': t['train_number'],
                            'train_type': t['train_type'],
                            'from': orig,
                            'to': dest,
                            'dep': stops[i1]['time'],
                            'arr': stops[i2]['time'],
                            'layover': 0
                        }]
                    })
    res.sort(key=lambda x: x['dep_min'])
    return res

def plan_multi_stop(wps, start_min=0):
    if len(wps) < 2: return []
    candidate_chains = plan_leg(wps[0]['station'], wps[1]['station'], start_min)
    
    for seg in range(1, len(wps) - 1):
        seg_orig = wps[seg]['station']
        seg_dest = wps[seg + 1]['station']
        min_stay = int(wps[seg].get('minStay', 0))
        next_chains = []
        for chain in candidate_chains:
            arr_min = chain['arr_min']
            earliest_dep = arr_min + min_stay
            viable_next = plan_leg(seg_orig, seg_dest, earliest_dep)[:3]
            for n_route in viable_next:
                stay_actual = n_route['dep_min'] - arr_min
                new_legs = chain['legs'] + [{
                    **n_route['legs'][0],
                    'stayBefore': stay_actual,
                    'layover': stay_actual
                }]
                next_chains.append({
                    'transfers': chain['transfers'] + n_route['transfers'] + 1,
                    'dep_time': chain['dep'],
                    'arr_time': n_route['arr'],
                    'dep_min': chain['dep_min'],
                    'arr_min': n_route['arr_min'],
                    'duration': n_route['arr_min'] - chain['dep_min'],
                    'stopovers': chain.get('stopovers', []) + [{'station': seg_orig, 'stayMin': stay_actual}],
                    'legs': new_legs
                })
        candidate_chains = next_chains
        if not candidate_chains: break
    return candidate_chains

# Test 1: 板橋 ➔ 宜蘭 ➔ 板橋 (stay 30 min)
r1 = plan_multi_stop([{'station': '板橋'}, {'station': '宜蘭', 'minStay': 30}, {'station': '板橋'}], 360)
print(f"Test 1 (板橋 ➔ 宜蘭 ➔ 板橋): found {len(r1)} routes")
for r in r1[:3]:
    print(f"  出發: {r['dep_time']} ➔ 抵達: {r['arr_time']} | 車程: {r['duration']}分 | 第1班: {r['legs'][0]['train_type']} {r['legs'][0]['train_number']} ({r['legs'][0]['dep']}~{r['legs'][0]['arr']}) ➔ 宜蘭停留 {r['legs'][1]['stayBefore']}分 ➔ 第2班: {r['legs'][1]['train_type']} {r['legs'][1]['train_number']} ({r['legs'][1]['dep']}~{r['legs'][1]['arr']})")

# Test 2: 台北 ➔ 台中 ➔ 台北 (stay 60 min)
r2 = plan_multi_stop([{'station': '台北'}, {'station': '台中', 'minStay': 60}, {'station': '台北'}], 420)
print(f"\nTest 2 (台北 ➔ 台中 ➔ 台北): found {len(r2)} routes")
for r in r2[:3]:
    print(f"  出發: {r['dep_time']} ➔ 抵達: {r['arr_time']} | 車程: {r['duration']}分 | 第1班: {r['legs'][0]['train_type']} {r['legs'][0]['train_number']} ({r['legs'][0]['dep']}~{r['legs'][0]['arr']}) ➔ 台中停留 {r['legs'][1]['stayBefore']}分 ➔ 第2班: {r['legs'][1]['train_type']} {r['legs'][1]['train_number']} ({r['legs'][1]['dep']}~{r['legs'][1]['arr']})")

assert len(r1) > 0
assert len(r2) > 0
print("\nAll tests passed successfully!")
