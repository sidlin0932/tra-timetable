# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

# Station ordering along the round-island railway network starting from 板橋:
# Eastbound sequence (順時針: 板橋 -> 台北 -> 宜蘭 -> 花蓮 -> 台東 -> 知本 -> 金崙 -> 大武 -> 枋山 -> 枋寮 -> 潮州 -> 高雄)
# Westbound sequence (逆時針: 板橋 -> 桃園 -> 新竹 -> 苗栗 -> 台中/彰化 -> 嘉義 -> 台南 -> 高雄 -> 潮州 -> 枋寮 -> 枋山 -> 大武)

# Let's collect all unique stations in database
all_stations = set()
for t in trains:
    for s in t['stops']:
        all_stations.add(s['station'])

# Let's find for EVERY station:
# 1. Going East from 板橋: outbound legs (板橋 -> X), inbound legs (X -> 板橋), with stay >= 3 min
# 2. Going West from 板橋: outbound legs (板橋 -> X), inbound legs (X -> 板橋), with stay >= 3 min

# To distinguish Eastbound vs Westbound paths:
# Eastbound train lines / corridors: trains passing through 松山/宜蘭/花蓮
# Westbound train lines / corridors: trains passing through 桃園/中壢/新竹/台中/彰化/台南

def is_eastbound_train(t, from_st, to_st):
    st_names = [s['station'] for s in t['stops']]
    if from_st in st_names and to_st in st_names:
        i1 = st_names.index(from_st)
        i2 = st_names.index(to_st)
        if i1 < i2:
            sub = st_names[i1:i2+1]
            # If it passes through Taipei, Matsuyama, Yilan, Hualien, Taitung (heading towards East)
            if any(e in sub for e in ['松山', '七堵', '宜蘭', '羅東', '花蓮', '玉里', '台東']):
                return True
    return False

def is_westbound_train(t, from_st, to_st):
    st_names = [s['station'] for s in t['stops']]
    if from_st in st_names and to_st in st_names:
        i1 = st_names.index(from_st)
        i2 = st_names.index(to_st)
        if i1 < i2:
            sub = st_names[i1:i2+1]
            # If it passes through Taoyuan, Hsinchu, Taichung, Changhua, Tainan, Kaohsiung (heading towards West)
            if any(w in sub for w in ['桃園', '中壢', '新竹', '竹南', '苗栗', '台中', '彰化', '嘉義', '台南', '新左營', '高雄']):
                return True
    return False

# Let's test all stations for Eastbound touch-and-go (turnaround)
east_results = {}
for st in all_stations:
    if st == '板橋': continue
    # Outbound (板橋 -> st, eastbound)
    outs = []
    for t in trains:
        if is_eastbound_train(t, '板橋', st):
            i1 = [s['station'] for s in t['stops']].index('板橋')
            i2 = [s['station'] for s in t['stops']].index(st)
            m1 = time_to_min(t['stops'][i1]['time'])
            m2 = time_to_min(t['stops'][i2]['time'])
            if m2 > m1:
                outs.append({'train': t, 'dep': t['stops'][i1]['time'], 'arr': t['stops'][i2]['time'], 'dep_m': m1, 'arr_m': m2})
    
    # Inbound (st -> 板橋, heading back to Banqiao via East or West)
    ins = []
    for t in trains:
        st_names = [s['station'] for s in t['stops']]
        if st in st_names and '板橋' in st_names:
            i1 = st_names.index(st)
            i2 = st_names.index('板橋')
            if i1 < i2:
                m1 = time_to_min(t['stops'][i1]['time'])
                m2 = time_to_min(t['stops'][i2]['time'])
                if m2 > m1:
                    ins.append({'train': t, 'dep': t['stops'][i1]['time'], 'arr': t['stops'][i2]['time'], 'dep_m': m1, 'arr_m': m2})

    # Find valid turnaround with stay >= 3 min
    valid = []
    for o in outs:
        for i in ins:
            stay = i['dep_m'] - o['arr_m']
            if stay >= 3:
                valid.append((o, i, stay))
    if valid:
        # Sort by min stay (tight turnaround) or max stay
        valid.sort(key=lambda x: x[2])
        tightest = valid[0]
        longest = max(valid, key=lambda x: x[2])
        east_results[st] = {
            'tightest': tightest,
            'longest': longest,
            'count': len(valid)
        }

# Let's test all stations for Westbound touch-and-go (turnaround)
west_results = {}
for st in all_stations:
    if st == '板橋': continue
    outs = []
    for t in trains:
        if is_westbound_train(t, '板橋', st):
            i1 = [s['station'] for s in t['stops']].index('板橋')
            i2 = [s['station'] for s in t['stops']].index(st)
            m1 = time_to_min(t['stops'][i1]['time'])
            m2 = time_to_min(t['stops'][i2]['time'])
            if m2 > m1:
                outs.append({'train': t, 'dep': t['stops'][i1]['time'], 'arr': t['stops'][i2]['time'], 'dep_m': m1, 'arr_m': m2})
    
    ins = []
    for t in trains:
        st_names = [s['station'] for s in t['stops']]
        if st in st_names and '板橋' in st_names:
            i1 = st_names.index(st)
            i2 = st_names.index('板橋')
            if i1 < i2:
                m1 = time_to_min(t['stops'][i1]['time'])
                m2 = time_to_min(t['stops'][i2]['time'])
                if m2 > m1:
                    ins.append({'train': t, 'dep': t['stops'][i1]['time'], 'arr': t['stops'][i2]['time'], 'dep_m': m1, 'arr_m': m2})

    valid = []
    for o in outs:
        for i in ins:
            stay = i['dep_m'] - o['arr_m']
            if stay >= 3:
                valid.append((o, i, stay))
    if valid:
        valid.sort(key=lambda x: x[2])
        tightest = valid[0]
        longest = max(valid, key=lambda x: x[2])
        west_results[st] = {
            'tightest': tightest,
            'longest': longest,
            'count': len(valid)
        }

print(f"Total reachable stations Eastbound: {len(east_results)}")
print(f"Total reachable stations Westbound: {len(west_results)}")

# Check furthest Eastbound stations (e.g. South Link: 知本, 太麻里, 金崙, 瀧溪, 大武, 枋寮, 潮州, 高雄)
print("\n=== Furthest Eastbound Touch-and-Go Stations ===")
for st in ['花蓮', '玉里', '池上', '關山', '鹿野', '台東', '康樂', '知本', '太麻里', '金崙', '瀧溪', '大武', '枋山', '枋寮', '潮州', '高雄']:
    if st in east_results:
        t = east_results[st]['tightest']
        l = east_results[st]['longest']
        o_t, i_t, s_t = t
        print(f"📍 【{st}】可當日折返！(共 {east_results[st]['count']} 種折返組合)")
        print(f"   ⚡ 極限快閃 (停留 {s_t}分): 去程 {o_t['train']['train_type']} {o_t['train']['train_number']} (板橋 {o_t['dep']} ➔ {st} {o_t['arr']}) | 回程 {i_t['train']['train_type']} {i_t['train']['train_number']} ({st} {i_t['dep']} ➔ 板橋 {i_t['arr']})")
        print(f"   ☕ 最長漫遊 (停留 {l[2]//60}h {l[2]%60}m): 去程 {l[0]['train']['train_number']} ({l[0]['dep']}➔{l[0]['arr']}) | 回程 {l[1]['train']['train_number']} ({l[1]['dep']}➔{l[1]['arr']})\n")

print("\n=== Furthest Westbound Touch-and-Go Stations ===")
for st in ['台中', '彰化', '嘉義', '台南', '高雄', '鳳山', '屏東', '潮州', '林邊', '枋寮', '枋山', '大武', '台東']:
    if st in west_results:
        t = west_results[st]['tightest']
        l = west_results[st]['longest']
        o_t, i_t, s_t = t
        print(f"📍 【{st}】可當日折返！(共 {west_results[st]['count']} 種折返組合)")
        print(f"   ⚡ 極限快閃 (停留 {s_t}分): 去程 {o_t['train']['train_type']} {o_t['train']['train_number']} (板橋 {o_t['dep']} ➔ {st} {o_t['arr']}) | 回程 {i_t['train']['train_type']} {i_t['train']['train_number']} ({st} {i_t['dep']} ➔ 板橋 {i_t['arr']})")
        print(f"   ☕ 最長漫遊 (停留 {l[2]//60}h {l[2]%60}m): 去程 {l[0]['train']['train_number']} ({l[0]['dep']}➔{l[0]['arr']}) | 回程 {l[1]['train']['train_number']} ({l[1]['dep']}➔{l[1]['arr']})\n")
