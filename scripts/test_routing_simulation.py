import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    timetable = json.load(f)

def time_to_min(t_str):
    if not t_str or ':' not in t_str: return -1
    h, m = map(int, t_str.split(':'))
    return h * 60 + m

# Let's test finding direct and transfer trains from Taipei to Dajia
orig = '台北'
dest = '大甲'

directs = []
for t in timetable:
    st_names = [s['station'] for s in t['stops']]
    if orig in st_names and dest in st_names:
        i_orig = st_names.index(orig)
        i_dest = st_names.index(dest)
        if i_orig < i_dest:
            directs.append({
                'num': t['train_number'],
                'type': t['train_type'],
                'line': t.get('route_dir', ''),
                'dep': t['stops'][i_orig]['time'],
                'arr': t['stops'][i_dest]['time']
            })

print(f"Direct trains from {orig} to {dest}: {len(directs)}")
for d in directs:
    print(f"  {d['type']} {d['num']} [{d['line']}]: {d['dep']} -> {d['arr']}")

# Direct trains from Taipei to Taichung
orig = '台北'
dest = '台中'
directs_tc = []
for t in timetable:
    st_names = [s['station'] for s in t['stops']]
    if orig in st_names and dest in st_names:
        i_orig = st_names.index(orig)
        i_dest = st_names.index(dest)
        if i_orig < i_dest:
            directs_tc.append({
                'num': t['train_number'],
                'type': t['train_type'],
                'line': t.get('route_dir', ''),
                'dep': t['stops'][i_orig]['time'],
                'arr': t['stops'][i_dest]['time']
            })

print(f"\nDirect trains from {orig} to {dest}: {len(directs_tc)}")
for d in directs_tc[:8]:
    print(f"  {d['type']} {d['num']} [{d['line']}]: {d['dep']} -> {d['arr']}")
