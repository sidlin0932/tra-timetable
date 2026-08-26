# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

# Let's inspect all TR-PASS trains on South Link (南迴線: 台東 -> 枋寮/屏東/潮州/新左營)
print("=== TR-PASS Trains from 台東 towards West (南迴線 西行) ===")
for t in trains:
    if not t.get('is_trpass', True): continue
    st_names = [s['station'] for s in t['stops']]
    if '台東' in st_names and any(w in st_names for w in ['枋寮', '潮州', '屏東', '高雄', '新左營']):
        t_idx = st_names.index('台東')
        w_idx = max(st_names.index(w) for w in ['枋寮', '潮州', '屏東', '高雄', '新左營'] if w in st_names)
        if t_idx < w_idx:
            print(f"Train {t['train_number']} ({t['train_type']}): 台東 {t['stops'][t_idx]['time']} -> {st_names[w_idx]} {t['stops'][w_idx]['time']}")

print("\n=== TR-PASS Trains from West towards 台東 (南迴線 東行) ===")
for t in trains:
    if not t.get('is_trpass', True): continue
    st_names = [s['station'] for s in t['stops']]
    if '台東' in st_names and any(w in st_names for w in ['枋寮', '潮州', '屏東', '高雄', '新左營']):
        t_idx = st_names.index('台東')
        w_idx = min(st_names.index(w) for w in ['枋寮', '潮州', '屏東', '高雄', '新左營'] if w in st_names)
        if w_idx < t_idx:
            print(f"Train {t['train_number']} ({t['train_type']}): {st_names[w_idx]} {t['stops'][w_idx]['time']} -> 台東 {t['stops'][t_idx]['time']}")
