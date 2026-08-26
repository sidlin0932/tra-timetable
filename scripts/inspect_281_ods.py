# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import pandas as pd

folder = 'f:/Antigravity/台鐵時刻表0701'

path = os.path.join(folder, 'NorthLink20260701.ods')
xl = pd.ExcelFile(path, engine='odf')
for sheet in xl.sheet_names:
    df = xl.parse(sheet, header=None)
    for r in range(len(df)):
        if any(str(df.iloc[r, c]).strip().replace('.0', '') == '281' for c in range(min(5, len(df.columns)))):
            print(f"Found 281 in NorthLink ({sheet}, row {r}):")
            for c in range(len(df.columns)):
                if pd.notna(df.iloc[r, c]):
                    st = ''.join([str(df.iloc[k, c]).strip() for k in [1, 2, 3] if pd.notna(df.iloc[k, c]) and str(df.iloc[k, c]).strip() not in ['站名', '起訖站', '備註']])
                    print(f"  Col {c} ({st}): {df.iloc[r, c]}")
