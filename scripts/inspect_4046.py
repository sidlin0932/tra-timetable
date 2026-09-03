import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

for t in trains:
    if t['train_number'] in ['4046', '1221', '1025']:
        print(f"{t['train_number']} {t['train_type']}: {t['origin']} -> {t['dest']}")
        for s in t['stops']:
            if s['station'] in ['中壢', '桃園', '鶯歌', '樹林', '板橋', '台北', '松山', '瑞芳', '頭城', '宜蘭']:
                print(f"   {s['station']}: {s['time']}")
