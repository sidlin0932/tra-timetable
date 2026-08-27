import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    allTimetableData = json.load(f)

# Let's test checking if a transfer route is an overshoot
def isRouteBacktracking(legs, orig, dest):
    # Check if any leg travels backwards towards origin or previous stations
    visited_stations = set([orig])
    for i, leg in enumerate(legs):
        from_st = leg['from']
        to_st = leg['to']
        train_no = str(leg['train_number'])
        
        # Find train in DB
        tr = next((t for t in allTimetableData if str(t['train_number']) == train_no), None)
        if not tr: continue
        
        stops = [s['station'] for s in tr['stops']]
        if from_st in stops and to_st in stops:
            i_from = stops.index(from_st)
            i_to = stops.index(to_st)
            
            # 1. Check if this leg passed dest before reaching to_st (e.g. skipped dest and went further)
            if dest in stops:
                i_dest = stops.index(dest)
                if i_from < i_dest < i_to:
                    return True # Overshot past dest!
            
            # 2. Check if train after to_st continues back towards orig or previous visited stations
            # (indicating it reversed direction on the same line)
            subsequent_stops = set(stops[i_to:])
            if any(prev_st in subsequent_stops for prev_st in visited_stations if prev_st != to_st):
                return True # Backtracking towards origin / earlier stations!
                
        visited_stations.add(to_st)
    return False

print("Backtracking checker test ready.")
