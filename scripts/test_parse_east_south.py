# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import re

def clean_time(val):
    if pd.isna(val): return None
    s = str(val).strip()
    if s.endswith('.0'): s = s[:-2]
    match = re.search(r'(\d{1,2}):(\d{2})', s)
    if match:
        h, m = int(match.group(1)), int(match.group(2))
        return f"{h:02d}:{m:02d}"
    return None

def normalize_station(st):
    st = st.replace('臺', '台').replace('\u3000', '').replace(' ', '').strip()
    st = re.sub(r'[\d:\-－\s]+', '', st)
    return st

for fname in ['XinzuoyingToFangliaoToTaitung20260701.ods', '南迴線(台東→枋寮→新左營)-20260701.ods', 'TaitungToShulin20260701.ods', 'ShulinToTaitung20260701.ods']:
    xl = pd.ExcelFile(fname, engine='odf')
    df = xl.parse(xl.sheet_names[0], header=None)
    
    # Train numbers are in row 3
    t_row = 3
    
    # Stations are in rows 13+
    stations = []
    for r in range(13, len(df)):
        raw_st = str(df.iloc[r, 0]).strip()
        st = normalize_station(raw_st)
        if st and st not in ['nan', 'None']:
            stations.append((r, st))
            
    print(f"=== {fname} ===")
    print(f"Found {len(stations)} stations: {[s[1] for s in stations[:6]]}")
    
    # Train numbers in cols 8..df.shape[1]
    parsed_trains = 0
    for c in range(8, df.shape[1]):
        t_num = str(df.iloc[t_row, c]).strip().replace('.0', '')
        if t_num.isdigit():
            parsed_trains += 1
    print(f"Found {parsed_trains} trains in {fname}")
