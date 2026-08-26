# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import pandas as pd

folder = 'f:/Antigravity/台鐵時刻表0701'

path = os.path.join(folder, 'TaitungToShulin20260701.ods')
xl = pd.ExcelFile(path, engine='odf')
df = xl.parse(xl.sheet_names[0], header=None)

t_row = 3
type_row = 0
for c in range(8, df.shape[1]):
    val = str(df.iloc[t_row, c]).strip().replace('.0', '')
    if val == '281':
        print(f"Found 281 in TaitungToShulin Col {c}:")
        for r in range(13, len(df)):
            t_val = df.iloc[r, c]
            if pd.notna(t_val):
                st = df.iloc[r, 0]
                print(f"  Row {r} ({st}): {t_val}")
