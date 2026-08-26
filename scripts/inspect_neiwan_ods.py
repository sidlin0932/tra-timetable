# -*- coding: utf-8 -*-
import pandas as pd

sheets = pd.read_excel('Neiwan20260701.ods', sheet_name=None, engine='odf')
print("Sheets in Neiwan20260701.ods:", list(sheets.keys()))

for name, df in sheets.items():
    print(f"\n--- Sheet: {name} (shape {df.shape}) ---")
    print(df.iloc[:15, :10])
