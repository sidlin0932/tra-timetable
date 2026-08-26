import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

for t in trains:
    if t['train_number'] == '149':
        print('Train ' + t['train_number'] + ': ' + t['origin'] + ' -> ' + t['dest'])
        for s in t['stops']:
            print('  ' + s['station'] + ': ' + s['time'])

# Find all single character stations across entire database
single_char_stops = set()
for t in trains:
    for s in t['stops']:
        if len(s['station']) == 1:
            single_char_stops.add((s['station'], t['train_number']))

print('Single char stops found:', single_char_stops)
