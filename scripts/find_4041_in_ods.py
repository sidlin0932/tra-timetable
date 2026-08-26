# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import pandas as pd

folder = 'f:/Antigravity/台鐵時刻表0701'

for fname in os.listdir(folder):
    if fname.endswith('.ods'):
        path = os.path.join(folder, fname)
        try:
            xl = pd.ExcelFile(path, engine='odf')
            for sheet in xl.sheet_names:
                df = xl.parse(sheet, header=None)
                for r in range(len(df)):
                    for c in range(min(15, len(df.columns))):
                        val = str(df.iloc[r, c]).strip().replace('.0', '')
                        if val == '4041':
                            row_vals = [str(x) for x in df.iloc[r].dropna().tolist()]
                            print(f"\nFound 4041 in {fname} (Sheet: {sheet}, Row: {r}, Col: {c}):")
                            print("  Row data:", row_vals[:15])
        except Exception as e:
            pass
