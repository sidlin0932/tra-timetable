# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import pandas as pd
import json

folder = 'f:/Antigravity/台鐵時刻表0701'

def clean_time(val):
    if pd.isna(val): return ''
    s = str(val).strip().replace('.', ':').replace(';', ':')
    if len(s) == 4 and s.isdigit():
        return f"{s[:2]}:{s[2:]}"
    parts = s.split(':')
    if len(parts) == 2:
        try:
            h = int(parts[0])
            m = int(parts[1])
            if 0 <= h <= 24 and 0 <= m < 60:
                return f"{h:02d}:{m:02d}"
        except:
            return ''
    return ''

def t_min(t_str):
    if not t_str or ':' not in t_str: return 0
    h, m = map(int, t_str.split(':'))
    return h * 60 + m

# Master dictionary: train_key -> train_dict
all_trains_map = {}

def sort_stops_chronologically(stops):
    # Detect if train starts in afternoon/evening (e.g. after 12:00) and continues past midnight (e.g. 00:xx, 01:xx)
    # Convert times with midnight offset
    if not stops: return []
    
    # First, let's see if we have evening stops and midnight stops
    has_evening = any(t_min(s['time']) >= 12 * 60 for s in stops)
    has_midnight = any(t_min(s['time']) < 4 * 60 for s in stops)
    
    def get_sort_min(s):
        m = t_min(s['time'])
        if has_evening and has_midnight and m < 4 * 60:
            return m + 1440 # Push next-day midnight stops to after 24:00
        return m
        
    return sorted(stops, key=get_sort_min)

def add_or_merge_train(t_num, t_type, t_model, is_tr, line, stops):
    if not t_num or len(stops) < 2: return
    valid_stops = []
    seen_st = set()
    for s in stops:
        st = s['station']
        if st and st not in seen_st and st not in ['站名', '起訖站', '備註']:
            valid_stops.append(s)
            seen_st.add(st)
    if len(valid_stops) < 2: return

    is_express = any(x in t_type for x in ['自強', '普悠瑪', '太魯閣', '莒光']) or (t_num.isdigit() and int(t_num) < 1000)
    key = t_num if is_express else f"{t_num}_{line}"

    if key not in all_trains_map:
        sorted_stops = sort_stops_chronologically(valid_stops)
        all_trains_map[key] = {
            'train_number': t_num,
            'train_type': t_type,
            'train_model': t_model,
            'is_trpass': is_tr,
            'origin': sorted_stops[0]['station'],
            'dest': sorted_stops[-1]['station'],
            'line': line,
            'stops': sorted_stops
        }
    else:
        existing = all_trains_map[key]
        base_stops = list(existing['stops'])
        for s in valid_stops:
            if not any(bs['station'] == s['station'] for bs in base_stops):
                base_stops.append(s)

        sorted_stops = sort_stops_chronologically(base_stops)
        existing['stops'] = sorted_stops
        existing['origin'] = sorted_stops[0]['station']
        existing['dest'] = sorted_stops[-1]['station']
        if is_express and '自強' in t_type:
            existing['train_type'] = t_type
            existing['train_model'] = t_model
            existing['is_trpass'] = is_tr

print("Function sort_stops_chronologically defined.")
