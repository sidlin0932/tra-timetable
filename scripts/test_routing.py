# -*- coding: utf-8 -*-
import json

with open('f:/Antigravity/台鐵時刻表0701/full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

def plan_trip(orig, dest, start_time_min=0):
    results = []
    
    # Direct trains
    for t in trains:
        stops = t['stops']
        idx_o = -1
        idx_d = -1
        for i, s in enumerate(stops):
            if s['station'] == orig and idx_o == -1: idx_o = i
            if s['station'] == dest and idx_o != -1: idx_d = i; break
        if idx_o != -1 and idx_d != -1:
            dep = time_to_min(stops[idx_o]['time'])
            arr = time_to_min(stops[idx_d]['time'])
            if dep >= start_time_min and arr > dep:
                results.append({
                    'transfers': 0,
                    'dep_time': stops[idx_o]['time'],
                    'arr_time': stops[idx_d]['time'],
                    'duration': arr - dep,
                    'legs': [{
                        'train_number': t['train_number'],
                        'train_type': t['train_type'],
                        'train_model': t['train_model'],
                        'is_trpass': t.get('is_trpass', True),
                        'from': orig, 'to': dest,
                        'dep': stops[idx_o]['time'], 'arr': stops[idx_d]['time']
                    }]
                })
                
    # 1-Transfer (A -> T1 -> B)
    trains_from_orig = []
    for t in trains:
        stops = t['stops']
        for i, s in enumerate(stops[:-1]):
            if s['station'] == orig:
                t_dep = time_to_min(s['time'])
                if t_dep >= start_time_min:
                    for j in range(i+1, len(stops)):
                        trains_from_orig.append((t, s['time'], stops[j]['station'], stops[j]['time']))
                        
    trains_to_dest = []
    for t in trains:
        stops = t['stops']
        for j, s in enumerate(stops[1:], start=1):
            if s['station'] == dest:
                for i in range(0, j):
                    trains_to_dest.append((t, stops[i]['station'], stops[i]['time'], s['time']))
                    
    for t1, t1_dep, t1_arr_st, t1_arr_time in trains_from_orig:
        m_t1_arr = time_to_min(t1_arr_time)
        for t2, t2_dep_st, t2_dep_time, t2_arr_time in trains_to_dest:
            if t1_arr_st == t2_dep_st and t1['train_number'] != t2['train_number']:
                m_t2_dep = time_to_min(t2_dep_time)
                layover = m_t2_dep - m_t1_arr
                if 3 <= layover <= 120:
                    dur = time_to_min(t2_arr_time) - time_to_min(t1_dep)
                    results.append({
                        'transfers': 1,
                        'dep_time': t1_dep,
                        'arr_time': t2_arr_time,
                        'duration': dur,
                        'legs': [
                            {'train_number': t1['train_number'], 'train_type': t1['train_type'], 'train_model': t1['train_model'], 'is_trpass': t1.get('is_trpass', True), 'from': orig, 'to': t1_arr_st, 'dep': t1_dep, 'arr': t1_arr_time},
                            {'train_number': t2['train_number'], 'train_type': t2['train_type'], 'train_model': t2['train_model'], 'is_trpass': t2.get('is_trpass', True), 'from': t2_dep_st, 'to': dest, 'dep': t2_dep_time, 'arr': t2_arr_time, 'layover': layover}
                        ]
                    })
                    
    # 2-Transfer (A -> H1 -> H2 -> B)
    key_hubs = {'新竹', '北新竹', '竹中', '樹林', '板橋', '台北', '松山', '南港', '七堵', '八堵', '瑞芳', '宜蘭', '羅東', '花蓮', '二水', '彰化', '台中', '嘉義', '台南', '新左營', '高雄', '屏東', '潮州', '枋寮', '台東'}
    for t1, t1_dep, h1, t1_arr_time in trains_from_orig:
        if h1 not in key_hubs: continue
        m_t1_arr = time_to_min(t1_arr_time)
        
        for t3, h2, t3_dep_time, t3_arr_time in trains_to_dest:
            if h2 not in key_hubs or h1 == h2: continue
            m_t3_dep = time_to_min(t3_dep_time)
            if m_t3_dep <= m_t1_arr + 10: continue
            
            for t2 in trains:
                stops = t2['stops']
                idx_h1 = -1
                idx_h2 = -1
                for k, s in enumerate(stops):
                    if s['station'] == h1 and idx_h1 == -1: idx_h1 = k
                    if s['station'] == h2 and idx_h1 != -1: idx_h2 = k; break
                if idx_h1 != -1 and idx_h2 != -1:
                    m_t2_dep = time_to_min(stops[idx_h1]['time'])
                    m_t2_arr = time_to_min(stops[idx_h2]['time'])
                    layover1 = m_t2_dep - m_t1_arr
                    layover2 = m_t3_dep - m_t2_arr
                    if 3 <= layover1 <= 75 and 3 <= layover2 <= 75:
                        dur = time_to_min(t3_arr_time) - time_to_min(t1_dep)
                        results.append({
                            'transfers': 2,
                            'dep_time': t1_dep,
                            'arr_time': t3_arr_time,
                            'duration': dur,
                            'legs': [
                                {'train_number': t1['train_number'], 'train_type': t1['train_type'], 'train_model': t1['train_model'], 'is_trpass': t1.get('is_trpass', True), 'from': orig, 'to': h1, 'dep': t1_dep, 'arr': t1_arr_time},
                                {'train_number': t2['train_number'], 'train_type': t2['train_type'], 'train_model': t2['train_model'], 'is_trpass': t2.get('is_trpass', True), 'from': h1, 'to': h2, 'dep': stops[idx_h1]['time'], 'arr': stops[idx_h2]['time'], 'layover': layover1},
                                {'train_number': t3['train_number'], 'train_type': t3['train_type'], 'train_model': t3['train_model'], 'is_trpass': t3.get('is_trpass', True), 'from': h2, 'to': dest, 'dep': t3_dep_time, 'arr': t3_arr_time, 'layover': layover2}
                            ]
                        })
                        
    # Sort results
    results.sort(key=lambda r: (time_to_min(r['arr_time']), r['duration'], r['transfers']))
    return results

routes = plan_trip('\u5167\u7063', '\u5e73\u6eaa', start_time_min=300) # 內灣 -> 平溪 from 05:00
print(f'Total routes found from Neiwan to Pingxi: {len(routes)}')
for i, r in enumerate(routes[:5]):
    print(f"方案 {i+1}: 出發 {r['dep_time']} -> 抵達 {r['arr_time']} (總歷時: {r['duration']}分鐘, 轉乘 {r['transfers']}次)")
    for leg in r['legs']:
        lo = f" (在 {leg['from']} 等候 {leg['layover']}分鐘)" if 'layover' in leg else ""
        print(f"   * [{leg['train_type']} {leg['train_number']}] {leg['from']} {leg['dep']} -> {leg['to']} {leg['arr']}{lo}")
