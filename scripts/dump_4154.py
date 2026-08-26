import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

with open('check_4154.txt', 'w', encoding='utf-8') as out:
    for t in trains:
        if t['train_number'] == '4154':
            out.write('Train: ' + t['train_number'] + ' ' + t['train_type'] + ' (' + t['origin'] + ' -> ' + t['dest'] + ')\n')
            for idx, s in enumerate(t['stops']):
                out.write(str(idx + 1) + ': ' + s['station'] + ' (' + s['time'] + ')\n')

print('Written check_4154.txt')
