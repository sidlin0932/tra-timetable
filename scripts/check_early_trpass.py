# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

# Check how to reach Chaozhou before 11:55 from Banqiao using TR-PASS
# 1. Direct trains from Banqiao to Chaozhou/Xinzuoying/Kaohsiung
# 2. Or transfers
for t in trains:
    if not t.get('is_trpass', True): continue
    st_names = [s['station'] for s in t['stops']]
    if '板橋' in st_names and any(st in st_names for st in ['新左營', '高雄', '屏東', '潮州']):
        i1 = st_names.index('板橋')
        dep_t = t['stops'][i1]['time']
        dep_m = time_to_min(dep_t)
        if dep_m < 8*60:
            for target in ['新左營', '高雄', '屏東', '潮州']:
                if target in st_names:
                    i2 = st_names.index(target)
                    if i1 < i2:
                        print(f"Train {t['train_number']} ({t['train_type']}): 板橋 {dep_t} -> {target} {t['stops'][i2]['time']}")
