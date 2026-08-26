# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

# Let's check 潮州 <-> 枋寮 TR-PASS connections
# Outbound: 板橋 06:37 -> 潮州 12:15 (自強 103)
# Then from 潮州 -> 枋寮:
cz_to_fl = []
for t in trains:
    if not t.get('is_trpass', True): continue
    st_names = [s['station'] for s in t['stops']]
    if '潮州' in st_names and '枋寮' in st_names:
        i1 = st_names.index('潮州')
        i2 = st_names.index('枋寮')
        if i1 < i2:
            m1 = time_to_min(t['stops'][i1]['time'])
            if m1 >= 12*60 + 15:
                cz_to_fl.append((t['train_number'], t['train_type'], t['stops'][i1]['time'], t['stops'][i2]['time']))

print("潮州 -> 枋寮 after 12:15 (TR-PASS):")
for c in cz_to_fl:
    print(" ", c)

# Then from 枋寮 -> 潮州:
# Must arrive at 潮州 before 18:27 (to catch 152 次 PP自強 at 18:27 back to 板橋)
fl_to_cz = []
for t in trains:
    if not t.get('is_trpass', True): continue
    st_names = [s['station'] for s in t['stops']]
    if '枋寮' in st_names and '潮州' in st_names:
        i1 = st_names.index('枋寮')
        i2 = st_names.index('潮州')
        if i1 < i2:
            m2 = time_to_min(t['stops'][i2]['time'])
            if m2 <= 18*60 + 27:
                fl_to_cz.append((t['train_number'], t['train_type'], t['stops'][i1]['time'], t['stops'][i2]['time']))

print("\n枋寮 -> 潮州 before 18:27 (TR-PASS):")
for c in fl_to_cz:
    print(" ", c)
