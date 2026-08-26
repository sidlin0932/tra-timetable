# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd

for fname in ['XinzuoyingToFangliaoToTaitung20260701.ods', '南迴線(台東→枋寮→新左營)-20260701.ods', 'TaitungToShulin20260701.ods']:
    xl = pd.ExcelFile(fname, engine='odf')
    df = xl.parse(xl.sheet_names[0], header=None)
    print(f"\n=================== {fname} ===================")
    for r in range(min(20, len(df))):
        row_vals = [f"c{c}:{df.iloc[r, c]}" for c in range(min(20, df.shape[1])) if pd.notna(df.iloc[r, c])]
        if row_vals:
            print(f"Row {r}: " + " | ".join(row_vals[:8]))
