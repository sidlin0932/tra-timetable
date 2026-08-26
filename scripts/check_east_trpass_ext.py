# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

# East Coast TR-PASS Exploration:
# Outbound: 板橋 07:08 -> 花蓮 10:40 (自強 272)
# Or: 板橋 08:35 -> 花蓮 12:53 (自強 270)
# Returning TR-PASS from 花蓮 to 板橋:
# 1. 莒光號 653: 花蓮 15:09 -> 板橋 19:31
# 2. 自強號 281: 花蓮 16:30 -> 板橋 19:40
# 3. 自強號 235: 花蓮 17:50 -> 板橋 21:05
# 4. 自強號 247: 花蓮 20:30 -> 板橋 23:45 (last TR-PASS train to Banqiao)

print("TR-PASS trains from 花蓮 to Banqiao in evening:")
for t in trains:
    if not t.get('is_trpass', True): continue
    st_names = [s['station'] for s in t['stops']]
    if '花蓮' in st_names and '板橋' in st_names:
        i1 = st_names.index('花蓮')
        i2 = st_names.index('板橋')
        if i1 < i2:
            m1 = time_to_min(t['stops'][i1]['time'])
            m2 = time_to_min(t['stops'][i2]['time'])
            if m1 >= 14*60:
                print(f"  {t['train_type']} {t['train_number']}: 花蓮 {t['stops'][i1]['time']} -> 板橋 {t['stops'][i2]['time']}")

# Now let's see: from 花蓮 after 10:40, how far south can we go (e.g. 壽豐, 鳳林, 光復, 瑞穗, 玉里)
# and get back to 花蓮 before 20:30?
for target in ['吉安', '志學', '壽豐', '鳳林', '光復', '瑞穗', '玉里', '池上', '關山', '台東']:
    hl_to_tgt = []
    for t in trains:
        if not t.get('is_trpass', True): continue
        st_names = [s['station'] for s in t['stops']]
        if '花蓮' in st_names and target in st_names:
            i1 = st_names.index('花蓮')
            i2 = st_names.index(target)
            if i1 < i2:
                m1 = time_to_min(t['stops'][i1]['time'])
                if m1 >= 10*60 + 40:
                    hl_to_tgt.append((t['train_number'], t['train_type'], t['stops'][i1]['time'], t['stops'][i2]['time']))
    
    tgt_to_hl = []
    for t in trains:
        if not t.get('is_trpass', True): continue
        st_names = [s['station'] for s in t['stops']]
        if target in st_names and '花蓮' in st_names:
            i1 = st_names.index(target)
            i2 = st_names.index('花蓮')
            if i1 < i2:
                m2 = time_to_min(t['stops'][i2]['time'])
                if m2 <= 20*60 + 30:
                    tgt_to_hl.append((t['train_number'], t['train_type'], t['stops'][i1]['time'], t['stops'][i2]['time']))

    valid_hl_pairs = []
    for o in hl_to_tgt:
        arr_tgt_m = time_to_min(o[3])
        for i in tgt_to_hl:
            dep_tgt_m = time_to_min(i[2])
            if dep_tgt_m >= arr_tgt_m + 3:
                valid_hl_pairs.append((o, i, dep_tgt_m - arr_tgt_m))
    
    if valid_hl_pairs:
        tightest = min(valid_hl_pairs, key=lambda x: x[2])
        longest = max(valid_hl_pairs, key=lambda x: x[2])
        print(f"\n✅ TR-PASS 花蓮南下延伸 【{target}】: 可行！(共 {len(valid_hl_pairs)} 種接駁, 停留 {tightest[2]}分 ~ {longest[2]//60}h {longest[2]%60}m)")
        print(f"   去程: {tightest[0][1]} {tightest[0][0]} (花蓮 {tightest[0][2]} ➔ {target} {tightest[0][3]})")
        print(f"   回程: {tightest[1][1]} {tightest[1][0]} ({target} {tightest[1][2]} ➔ 花蓮 {tightest[1][3]})")
    else:
        print(f"\n❌ TR-PASS 花蓮南下延伸 【{target}】: 無法接駁當日返回花蓮")
