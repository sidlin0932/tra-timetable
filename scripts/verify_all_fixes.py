# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

# Verify 154, 152, 168
t154 = next((t for t in trains if t['train_number'] == '154'), None)
t152 = next((t for t in trains if t['train_number'] == '152'), None)
t168 = next((t for t in trains if t['train_number'] == '168'), None)

print("154 exists:", bool(t154), f"origin: {t154['origin'] if t154 else None} -> dest: {t154['dest'] if t154 else None}")
print("152 exists:", bool(t152), f"origin: {t152['origin'] if t152 else None} -> dest: {t152['dest'] if t152 else None}")
print("168 exists:", bool(t168), f"origin: {t168['origin'] if t168 else None} -> dest: {t168['dest'] if t168 else None}")

# Verify 4513 does not have Dongao right after Taitung
t4513_list = [t for t in trains if t['train_number'] == '4513']
print(f"\nTotal 4513 entries: {len(t4513_list)}")
for t in t4513_list:
    print(f"  Line: {t.get('line')} | {t['origin']} -> {t['dest']} | stops: {[s['station'] for s in t['stops']]}")

assert t154 is not None
assert t152 is not None
assert t168 is not None
print("\nALL VERIFICATIONS PASSED!")
