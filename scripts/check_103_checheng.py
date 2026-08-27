import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    tt = json.load(f)

t103 = next((t for t in tt if t['train_number'] == '103'), None)
print('Train 103 stops:')
for s in t103['stops']:
    print(f"  {s['station']}: {s['time']}")

print("\nJiji Line Trains (Down to Checheng):")
for t in tt:
    if any(s['station'] == '車埕' for s in t['stops']):
        print(f"Train {t['train_number']} {t['origin']} -> {t['dest']}:")
        for s in t['stops']:
            print(f"    {s['station']}: {s['time']}")
