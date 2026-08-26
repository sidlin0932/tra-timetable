# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

# Fare table / calculation by train type
# 區間車/區間快 (Local): 1.46 NT$/km
# 莒光號 (Chu-Kwang): 1.75 NT$/km
# 自強號/新自強/普悠瑪 (Tze-Chiang): 2.27 NT$/km

def get_fare(train_type, from_st, to_st):
    # Official station distances (approx)
    # Let's map standard TRA fares between major junctions
    fares = {
        ('板橋', '花蓮'): {'自強號': 440, '新自強(EMU3000)': 440, '普悠瑪': 440, '太魯閣': 440, '莒光號': 340, '區間車': 283, '區間快': 283},
        ('板橋', '台東'): {'自強號': 783, '新自強(EMU3000)': 783, '普悠瑪': 783, '太魯閣': 783, '莒光號': 604, '區間車': 502, '區間快': 502},
        ('花蓮', '台東'): {'自強號': 343, '新自強(EMU3000)': 343, '普悠瑪': 343, '太魯閣': 343, '莒光號': 264, '區間車': 219, '區間快': 219},
        ('台東', '潮州'): {'自強號': 246, '新自強(EMU3000)': 246, '普悠瑪': 246, '太魯閣': 246, '莒光號': 190, '區間車': 158, '區間快': 158},
        ('台東', '枋寮'): {'自強號': 189, '新自強(EMU3000)': 189, '普悠瑪': 189, '太魯閣': 189, '莒光號': 146, '區間車': 122, '區間快': 122},
        ('台東', '新左營'): {'自強號': 349, '新自強(EMU3000)': 349, '普悠瑪': 349, '太魯閣': 349, '莒光號': 269, '區間車': 224, '區間快': 224},
        ('台東', '高雄'): {'自強號': 331, '新自強(EMU3000)': 331, '普悠瑪': 331, '太魯閣': 331, '莒光號': 255, '區間車': 212, '區間快': 212},
        ('枋寮', '潮州'): {'自強號': 57, '新自強(EMU3000)': 57, '普悠瑪': 57, '太魯閣': 57, '莒光號': 44, '區間車': 37, '區間快': 37},
        ('潮州', '板橋'): {'自強號': 905, '新自強(EMU3000)': 905, '普悠瑪': 905, '太魯閣': 905, '莒光號': 698, '區間車': 582, '區間快': 582},
        ('新左營', '板橋'): {'自強號': 824, '新自強(EMU3000)': 824, '普悠瑪': 824, '太魯閣': 824, '莒光號': 635, '區間車': 530, '區間快': 530},
        ('高雄', '板橋'): {'自強號': 843, '新自強(EMU3000)': 843, '普悠瑪': 843, '太魯閣': 843, '莒光號': 650, '區間車': 542, '區間快': 542},
        ('台東', '板橋'): {'自強號': 1151, '新自強(EMU3000)': 1151, '普悠瑪': 1151, '太魯閣': 1151, '莒光號': 888, '區間車': 740, '區間快': 740}, # via South Link
    }
    # Reverse lookup if needed
    if (from_st, to_st) in fares:
        return fares[(from_st, to_st)].get(train_type, 200)
    elif (to_st, from_st) in fares:
        return fares[(to_st, from_st)].get(train_type, 200)
    return 200

# Let's search ALL valid True 360° Circular Chains
# 1. Clockwise (順時針: 板橋 -> (花蓮/台東) -> (台東/潮州/新左營) -> 板橋)
print("=== 順時針真環島方案搜尋 (板橋 ➔ 東部 ➔ 南迴 ➔ 西部 ➔ 板橋) ===")
# Outbound East (板橋 -> 台東 direct, or 板橋 -> 花蓮 -> 台東)
cw_circuits = []

# Sub-option A: 板橋 -> 台東 (direct)
for t1 in trains:
    st1 = [s['station'] for s in t1['stops']]
    if '板橋' in st1 and '台東' in st1:
        i_b = st1.index('板橋')
        i_t = st1.index('台東')
        # Check if eastbound (passing Taipei/Yilan/Hualien)
        if i_b < i_t and any(h in st1[i_b:i_t] for h in ['台北', '松山', '宜蘭', '花蓮']):
            dep1_m = time_to_min(t1['stops'][i_b]['time'])
            arr1_m = time_to_min(t1['stops'][i_t]['time'])
            if arr1_m > dep1_m:
                leg1 = {'train_no': t1['train_number'], 'train_type': t1['train_type'], 'from': '板橋', 'to': '台東', 'dep': t1['stops'][i_b]['time'], 'arr': t1['stops'][i_t]['time'], 'dep_m': dep1_m, 'arr_m': arr1_m, 'fare': get_fare(t1['train_type'], '板橋', '台東')}
                
                # Now from 台東 -> 板橋 via South Link / Western
                # Could be direct (like 168次), or via 潮州/新左營/高雄
                for t2 in trains:
                    st2 = [s['station'] for s in t2['stops']]
                    if '台東' in st2 and '板橋' in st2:
                        i2_t = st2.index('台東')
                        i2_b = st2.index('板橋')
                        if i2_t < i2_b and any(w in st2[i2_t:i2_b] for w in ['潮州', '高雄', '台南']):
                            dep2_m = time_to_min(t2['stops'][i2_t]['time'])
                            arr2_m = time_to_min(t2['stops'][i2_b]['time'])
                            if dep2_m >= arr1_m + 3 and arr2_m > dep2_m:
                                leg2 = {'train_no': t2['train_number'], 'train_type': t2['train_type'], 'from': '台東', 'to': '板橋', 'dep': t2['stops'][i2_t]['time'], 'arr': t2['stops'][i2_b]['time'], 'dep_m': dep2_m, 'arr_m': arr2_m, 'fare': get_fare(t2['train_type'], '台東', '板橋')}
                                total_fare = leg1['fare'] + leg2['fare']
                                cw_circuits.append({'type': '順時針2段直通', 'legs': [leg1, leg2], 'total_fare': total_fare, 'dep': leg1['dep'], 'arr': leg2['arr'], 'dur': arr2_m - dep1_m})

                    # Or 台東 -> 潮州 / 新左營 -> 板橋
                    elif '台東' in st2 and any(w in st2 for w in ['潮州', '新左營']):
                        mid_st = '潮州' if '潮州' in st2 else '新左營'
                        i2_t = st2.index('台東')
                        i2_m = st2.index(mid_st)
                        if i2_t < i2_m:
                            dep2_m = time_to_min(t2['stops'][i2_t]['time'])
                            arr2_m = time_to_min(t2['stops'][i2_m]['time'])
                            if dep2_m >= arr1_m + 3 and arr2_m > dep2_m:
                                leg2 = {'train_no': t2['train_number'], 'train_type': t2['train_type'], 'from': '台東', 'to': mid_st, 'dep': t2['stops'][i2_t]['time'], 'arr': t2['stops'][i2_m]['time'], 'dep_m': dep2_m, 'arr_m': arr2_m, 'fare': get_fare(t2['train_type'], '台東', mid_st)}
                                
                                # Leg 3: mid_st -> 板橋
                                for t3 in trains:
                                    st3 = [s['station'] for s in t3['stops']]
                                    if mid_st in st3 and '板橋' in st3:
                                        i3_m = st3.index(mid_st)
                                        i3_b = st3.index('板橋')
                                        if i3_m < i3_b:
                                            dep3_m = time_to_min(t3['stops'][i3_m]['time'])
                                            arr3_m = time_to_min(t3['stops'][i3_b]['time'])
                                            if dep3_m >= arr2_m + 3 and arr3_m > dep3_m:
                                                leg3 = {'train_no': t3['train_number'], 'train_type': t3['train_type'], 'from': mid_st, 'to': '板橋', 'dep': t3['stops'][i3_m]['time'], 'arr': t3['stops'][i3_b]['time'], 'dep_m': dep3_m, 'arr_m': arr3_m, 'fare': get_fare(t3['train_type'], mid_st, '板橋')}
                                                total_fare = leg1['fare'] + leg2['fare'] + leg3['fare']
                                                cw_circuits.append({'type': '順時針3段接駁', 'legs': [leg1, leg2, leg3], 'total_fare': total_fare, 'dep': leg1['dep'], 'arr': leg3['arr'], 'dur': arr3_m - dep1_m})

print(f"Total True 360° Circular Circuits: {len(cw_circuits)}")

# Sort by lowest total fare
cw_circuits.sort(key=lambda x: (x['total_fare'], x['dur']))

print("\n=== Top 5 Lowest Cost True 360° Round-Island Itineraries ===")
for c in cw_circuits[:5]:
    print(f"\n💰 總票價: NT$ {c['total_fare']} | 總耗時: {c['dur']//60}h {c['dur']%60}m (板橋 {c['dep']} ➔ 板橋 {c['arr']})")
    for idx, l in enumerate(c['legs']):
        print(f"  第 {idx+1} 段 (NT$ {l['fare']}): {l['train_type']} {l['train_no']} ({l['from']} {l['dep']} ➔ {l['to']} {l['arr']})")

# Let's check TR-PASS feasibility on true circle
# TR-PASS General 3-day (NT$ 1800) covers all PP Tze-Chiang, Chu-Kwang, Local.
# If leg 1 is Puyuma/EMU3000 (NT$ 783) and legs 2 & 3 are TR-PASS:
# 783 + 599 (Student TR-PASS) = NT$ 1382!
