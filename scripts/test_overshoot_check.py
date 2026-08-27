import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    timetable = json.load(f)

# Let's test checking overshoot on routes
def isLegOvershooting(leg1, leg2, dest):
    # If leg2 brings the passenger to dest, but leg1 already visited or passed dest / intermediate stations
    # 1. Check if train of leg1 already contained leg2.to (dest) between leg1.from and leg1.to
    # If leg1 went from A to C, and train1 also had B (dest) between A and C, then riding to C was an overshoot past B!
    t1_stops = [s['station'] for s in leg1.get('all_stops', [])]
    if leg2['to'] in t1_stops:
        idx_from = t1_stops.index(leg1['from']) if leg1['from'] in t1_stops else 0
        idx_to = t1_stops.index(leg1['to']) if leg1['to'] in t1_stops else len(t1_stops)-1
        idx_dest = t1_stops.index(leg2['to'])
        if idx_from < idx_dest < idx_to:
            return True # leg1 passed dest to go further, then leg2 doubled back to dest!

    # 2. Check if train of leg2 has leg1.from in its remaining stops after leg2.from (i.e. leg2 is heading back towards leg1.from)
    # E.g. leg1: Taipei -> Taoyuan. leg2: Taoyuan -> Yingge (and train2 continues to Taipei/Keelung)
    t2_stops = [s['station'] for s in leg2.get('all_stops', [])]
    # If train2 reaches leg1.from after leg2.to, train2 is going in the reverse direction of leg1 on the same corridor!
    return False

print("Overshoot check defined.")
