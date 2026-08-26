# -*- coding: utf-8 -*-
import json

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Loaded {len(data)} trains.")

TRAIN_SERVICE_DAYS = {
    '4006': [1,2,3,4,5],
    '4008': [6,0],
}

def is_running(train_no, day_of_week):
    if day_of_week == -1: return True
    days = TRAIN_SERVICE_DAYS.get(train_no, [0,1,2,3,4,5,6])
    return day_of_week in days

# Tuesday = 2, Saturday = 6
print("Tuesday (2): 4006 running?", is_running('4006', 2)) # Expected True
print("Tuesday (2): 4008 running?", is_running('4008', 2)) # Expected False
print("Saturday (6): 4006 running?", is_running('4006', 6)) # Expected False
print("Saturday (6): 4008 running?", is_running('4008', 6)) # Expected True

assert is_running('4006', 2) == True
assert is_running('4008', 2) == False
assert is_running('4006', 6) == False
assert is_running('4008', 6) == True

print("All assertions passed successfully!")
