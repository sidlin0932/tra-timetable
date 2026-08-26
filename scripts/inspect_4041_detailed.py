# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import pandas as pd
import json

folder = 'f:/Antigravity/台鐵時刻表0701'

# Let's inspect the exact stops of 4041 in 台東線 (北上)
path = os.path.join(folder, '台東線-20260701.ods')
xl = pd.ExcelFile(path, engine='odf')
df = xl.parse(xl.sheet_names[0], header=None)

# Stations from right to left (Taitung to Hualien)
# In df, row 35 is 4041.
# Let's list non-empty columns with their station names
stops_4041_tt = []
for c in range(len(df.columns)):
    st = ''.join([str(df.iloc[r, c]).strip() for r in [1, 2, 3] if pd.notna(df.iloc[r, c]) and str(df.iloc[r, c]).strip() not in ['站名', '起訖站', '備註']])
    # Clean station name
    st = st.replace('05:52', '').replace('06:00', '').replace('06:04', '').replace('06:11', '').replace('06:17', '').replace('06:26', '').replace(' ', '').replace('\u3000', '')
    val = df.iloc[35, c]
    if pd.notna(val):
        t_str = str(val).strip().replace('.', ':')
        if ':' in t_str:
            stops_4041_tt.append({'col': c, 'station': st, 'time': t_str})

# Notice: columns are 4 (花蓮) to 30 (臺東).
# 4041 is northbound: col 30 (臺東 18:04 or 21:20?)
print("4041 in 台東線 sheet (as in columns):")
for s in stops_4041_tt:
    print(f"  Col {s['col']:2d} ({s['station']}): {s['time']}")
