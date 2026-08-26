# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

# Let's inspect all trains between Fangliao and Taitung across the entire day
print("=== All Trains between 枋寮 and 台東 (Both Directions) ===")
for t in trains:
    st_names = [s['station'] for s in t['stops']]
    if '枋寮' in st_names and '台東' in st_names:
        i1 = st_names.index('枋寮')
        i2 = st_names.index('台東')
        dir_str = "枋寮 ➔ 台東 (東行)" if i1 < i2 else "台東 ➔ 枋寮 (西行)"
        tr_str = "✅ TR-PASS" if t.get('is_trpass', True) else "❌ 非TR-PASS"
        print(f"Train {t['train_number']:>4} ({t['train_type']:<12}) [{tr_str}]: {dir_str} | {t['stops'][i1]['station']} {t['stops'][i1]['time']} ➔ {t['stops'][i2]['station']} {t['stops'][i2]['time']}")
