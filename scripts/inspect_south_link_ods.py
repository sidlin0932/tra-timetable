# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd

for fname in ['XinzuoyingToFangliaoToTaitung20260701.ods', '南迴線(台東→枋寮→新左營)-20260701.ods', 'TaitungToShulin20260701.ods', 'ShulinToTaitung20260701.ods']:
    try:
        xl = pd.ExcelFile(fname, engine='odf')
        print(f"=== {fname} ===")
        print(f"Sheets: {xl.sheet_names}")
        df = xl.parse(xl.sheet_names[0], header=None)
        print(f"Shape: {df.shape}")
        print("First 8 rows, first 8 cols:")
        print(df.iloc[:8, :8])
    except Exception as e:
        print(f"Error {fname}: {e}")
