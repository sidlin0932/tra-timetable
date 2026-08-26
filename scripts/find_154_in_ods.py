# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import pandas as pd
import json

ods_files = [f for f in os.listdir('.') if f.endswith('.ods')]
print(f"All ODS files: {ods_files}")

for fname in ods_files:
    try:
        xl = pd.ExcelFile(fname, engine='odf')
        for sheet in xl.sheet_names:
            df = xl.parse(sheet, header=None)
            for r in range(min(10, len(df))):
                for c in range(df.shape[1]):
                    val = str(df.iloc[r, c]).strip().replace('.0', '')
                    if val in ['154', '168', '156', '162', '164', '166', '170', '172', '174', '176', '178', '180', '434']:
                        print(f"Found Train {val} in file: {fname} (sheet: {sheet}, row: {r}, col: {c})")
    except Exception as e:
        pass
