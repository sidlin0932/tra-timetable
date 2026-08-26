import json

def time_to_min(time_str):
    try:
        h, m = map(int, time_str.split(':'))
        if h < 4:
            h += 24
        return h * 60 + m
    except:
        return -1

with open('f:/Antigravity/台鐵時刻表0701/full_timetable.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

anomalies = []

for t in data['trains']:
    stops = t['stops']
    
    # 1. Too few stops
    if len(stops) < 2:
        anomalies.append(f"Train {t['train_number']}: Only {len(stops)} stop(s)")
        
    # 2. Duplicate consecutive stations (failed merge)
    for i in range(1, len(stops)):
        if stops[i]['station'] == stops[i-1]['station']:
            anomalies.append(f"Train {t['train_number']}: Consecutive identical station '{stops[i]['station']}' at index {i}")
            
    # 3. Time jumps backwards (ignoring midnight wrap because time_to_min handles it)
    for i in range(1, len(stops)):
        prev_t = time_to_min(stops[i-1].get('departure_time', stops[i-1]['arrival_time']))
        curr_t = time_to_min(stops[i]['arrival_time'])
        if prev_t > curr_t and prev_t - curr_t > 1400: # Actually if prev=23:59 and curr=00:01, handled by +24
            pass
        elif curr_t < prev_t:
            anomalies.append(f"Train {t['train_number']}: Time jumps backwards from {stops[i-1].get('departure_time')} to {stops[i]['arrival_time']} at {stops[i]['station']}")

    # 4. English noise words
    for s in stops:
        if 'ArrivalTime' in s['station'] or 'DepartureTime' in s['station']:
            anomalies.append(f"Train {t['train_number']}: Noise word in station '{s['station']}'")

    # 5. Empty or excessively garbled station names
    for s in stops:
        if not s['station'] or s['station'] == 'Unknown' or len(s['station']) < 1:
            anomalies.append(f"Train {t['train_number']}: Invalid station name '{s['station']}'")

if not anomalies:
    print("Verification Passed! No anomalies found.")
else:
    print(f"Verification Failed. Found {len(anomalies)} anomalies:")
    for a in anomalies[:20]:
        print(a)
    if len(anomalies) > 20:
        print(f"... and {len(anomalies) - 20} more.")
