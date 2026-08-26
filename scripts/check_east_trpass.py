# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

trpass_trains = [t for t in trains if t.get('is_trpass', True)]

print("=== TR-PASS Trains from 台北 to 花蓮 ===")
for t in trpass_trains:
    st_names = [s['station'] for s in t['stops']]
    if '台北' in st_names and '花蓮' in st_names:
        i1 = st_names.index('台北')
        i2 = st_names.index('花蓮')
        if i1 < i2:
            print(f"Train {t['train_number']} ({t['train_type']}): 台北 {t['stops'][i1]['time']} -> 花蓮 {t['stops'][i2]['time']}")

print("\n=== TR-PASS Trains from 花蓮 to 台東 ===")
for t in trpass_trains:
    st_names = [s['station'] for s in t['stops']]
    if '花蓮' in st_names and '台東' in st_names:
        i1 = st_names.index('花蓮')
        i2 = st_names.index('台東')
        if i1 < i2:
            print(f"Train {t['train_number']} ({t['train_type']}): 花蓮 {t['stops'][i1]['time']} -> 台東 {t['stops'][i2]['time']}")
