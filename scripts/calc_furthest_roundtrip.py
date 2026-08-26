# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

def min_to_t(m):
    return f"{m//60:02d}:{m%60:02d}"

# Check 1-day round trips from 板橋 to target stations
# 1. Going East (東部幹線 / 南迴)
east_targets = ['宜蘭', '羅東', '花蓮', '玉里', '池上', '關山', '台東', '知本', '太麻里', '金崙', '大武', '枋寮']
west_targets = ['台中', '彰化', '員林', '斗六', '嘉義', '新營', '台南', '新左營', '高雄', '屏東', '潮州', '枋寮']

def test_out_and_back(orig, target, min_stay_m=60, trpass_only=False):
    # Outbound legs
    out_trains = []
    for t in trains:
        if trpass_only and not t.get('is_trpass', True): continue
        st_names = [s['station'] for s in t['stops']]
        if orig in st_names and target in st_names:
            i1 = st_names.index(orig)
            i2 = st_names.index(target)
            if i1 < i2:
                m1 = time_to_min(t['stops'][i1]['time'])
                m2 = time_to_min(t['stops'][i2]['time'])
                if m2 > m1:
                    out_trains.append({
                        'train_no': t['train_number'],
                        'train_type': t['train_type'],
                        'dep': t['stops'][i1]['time'],
                        'arr': t['stops'][i2]['time'],
                        'dep_m': m1,
                        'arr_m': m2
                    })
    out_trains.sort(key=lambda x: x['dep_m'])

    # Inbound legs
    in_trains = []
    for t in trains:
        if trpass_only and not t.get('is_trpass', True): continue
        st_names = [s['station'] for s in t['stops']]
        if target in st_names and orig in st_names:
            i1 = st_names.index(target)
            i2 = st_names.index(orig)
            if i1 < i2:
                m1 = time_to_min(t['stops'][i1]['time'])
                m2 = time_to_min(t['stops'][i2]['time'])
                if m2 > m1:
                    in_trains.append({
                        'train_no': t['train_number'],
                        'train_type': t['train_type'],
                        'dep': t['stops'][i1]['time'],
                        'arr': t['stops'][i2]['time'],
                        'dep_m': m1,
                        'arr_m': m2
                    })
    in_trains.sort(key=lambda x: x['dep_m'])

    valid_pairs = []
    for o in out_trains:
        for i in in_trains:
            stay = i['dep_m'] - o['arr_m']
            if stay >= min_stay_m:
                valid_pairs.append({
                    'out': o,
                    'in': i,
                    'stay_m': stay,
                    'total_span_m': i['arr_m'] - o['dep_m']
                })
    return valid_pairs

print("=== 1. 全車種（含新自強/普悠瑪）東部往返極限 ===")
for target in east_targets:
    res = test_out_and_back('板橋', target, min_stay_m=60, trpass_only=False)
    if res:
        # Find max stay option
        max_stay = max(res, key=lambda x: x['stay_m'])
        o, i = max_stay['out'], max_stay['in']
        print(f"✅ 板橋 ➔ {target} ➔ 板橋: 可行 (共 {len(res)} 種往返組合, 最大停留: {max_stay['stay_m']//60}h {max_stay['stay_m']%60}m)")
        print(f"   去程: {o['train_type']} {o['train_no']} (板橋 {o['dep']} ➔ {target} {o['arr']})")
        print(f"   回程: {i['train_type']} {i['train_no']} ({target} {i['dep']} ➔ 板橋 {i['arr']})")
    else:
        print(f"❌ 板橋 ➔ {target} ➔ 板橋: 無法一日往返")

print("\n=== 2. 全車種（含新自強/普悠瑪）西部往返極限 ===")
for target in west_targets:
    res = test_out_and_back('板橋', target, min_stay_m=60, trpass_only=False)
    if res:
        max_stay = max(res, key=lambda x: x['stay_m'])
        o, i = max_stay['out'], max_stay['in']
        print(f"✅ 板橋 ➔ {target} ➔ 板橋: 可行 (共 {len(res)} 種往返組合, 最大停留: {max_stay['stay_m']//60}h {max_stay['stay_m']%60}m)")
        print(f"   去程: {o['train_type']} {o['train_no']} (板橋 {o['dep']} ➔ {target} {o['arr']})")
        print(f"   回程: {i['train_type']} {i['train_no']} ({target} {i['dep']} ➔ 板橋 {i['arr']})")
    else:
        print(f"❌ 板橋 ➔ {target} ➔ 板橋: 無法一日往返")

print("\n=== 3. TR-PASS 專用（僅 PP自強/莒光/區間）東部往返極限 ===")
for target in east_targets:
    res = test_out_and_back('板橋', target, min_stay_m=60, trpass_only=True)
    if res:
        max_stay = max(res, key=lambda x: x['stay_m'])
        o, i = max_stay['out'], max_stay['in']
        print(f"✅ [TR-PASS] 板橋 ➔ {target} ➔ 板橋: 可行 (最大停留: {max_stay['stay_m']//60}h {max_stay['stay_m']%60}m)")
        print(f"   去程: {o['train_type']} {o['train_no']} (板橋 {o['dep']} ➔ {target} {o['arr']}) | 回程: {i['train_type']} {i['train_no']} ({target} {i['dep']} ➔ 板橋 {i['arr']})")
    else:
        print(f"❌ [TR-PASS] 板橋 ➔ {target} ➔ 板橋: 無法一日往返 (無直達或接駁不及)")

print("\n=== 4. TR-PASS 專用（僅 PP自強/莒光/區間）西部往返極限 ===")
for target in west_targets:
    res = test_out_and_back('板橋', target, min_stay_m=60, trpass_only=True)
    if res:
        max_stay = max(res, key=lambda x: x['stay_m'])
        o, i = max_stay['out'], max_stay['in']
        print(f"✅ [TR-PASS] 板橋 ➔ {target} ➔ 板橋: 可行 (最大停留: {max_stay['stay_m']//60}h {max_stay['stay_m']%60}m)")
        print(f"   去程: {o['train_type']} {o['train_no']} (板橋 {o['dep']} ➔ {target} {o['arr']}) | 回程: {i['train_type']} {i['train_no']} ({target} {i['dep']} ➔ 板橋 {i['arr']})")
    else:
        print(f"❌ [TR-PASS] 板橋 ➔ {target} ➔ 板橋: 無法一日往返")

