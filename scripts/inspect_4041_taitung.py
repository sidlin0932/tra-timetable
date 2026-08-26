# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import pandas as pd

folder = 'f:/Antigravity/台鐵時刻表0701'
path = os.path.join(folder, '台東線-20260701.ods')
xl = pd.ExcelFile(path, engine='odf')
df = xl.parse(xl.sheet_names[0], header=None)

# Let's inspect rows 0 to 4 (station headers) and row 35 (4041)
print("Station header row 1:", df.iloc[1].dropna().tolist()[:25])
print("Station header row 2:", df.iloc[2].dropna().tolist()[:25])

# Print columns with stations for row 35
for c in range(len(df.columns)):
    st = ''.join([str(df.iloc[r, c]).strip() for r in [1, 2, 3] if pd.notna(df.iloc[r, c]) and str(df.iloc[r, c]).strip() not in ['站名', '起訖站', '備註']])
    val = df.iloc[35, c]
    if pd.notna(val):
        print(f"Col {c} ({st}): {val}")
