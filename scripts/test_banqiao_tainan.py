import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

print(f"Total trains: {len(trains)}")

# Check trains that stop at Banqiao
banqiao_trains = []
for t in trains:
    for s in t['stops']:
        if s['station'] == '板橋':
            banqiao_trains.append((t['train_number'], t['train_type'], t['origin'], t['dest'], s['time']))

print(f"Trains stopping at Banqiao: {len(banqiao_trains)}")

# Commuter trains from Banqiao heading South
south_commuters = [t for t in banqiao_trains if t[1] in ['區間車', '區間快'] and ('北湖' in t[3] or '新竹' in t[3] or '苗栗' in t[3] or '彰化' in t[3] or '二水' in t[3] or '嘉義' in t[3] or '潮州' in t[3])]
print(f"Southbound commuters from Banqiao: {len(south_commuters)}")
for sc in south_commuters[:10]:
    print(f"  {sc[1]} {sc[0]}: {sc[2]} -> {sc[3]} (板橋 {sc[4]})")
