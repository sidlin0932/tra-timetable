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
                        if val == '281':
                            print(f"Found 281 in {fname} (Sheet: {sheet}, Row: {r}, Col: {c})")
        except Exception as e:
            pass
