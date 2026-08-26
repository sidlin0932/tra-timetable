# -*- coding: utf-8 -*-
import pandas as pd

df = pd.read_excel('Neiwan20260701.ods', engine='odf', header=None)
print("Rows 60 to 75:")
for r in range(60, min(75, len(df))):
    row_vals = [f"Col{c}:{df.iloc[r, c]}" for c in range(df.shape[1]) if pd.notna(df.iloc[r, c])]
    print(f"Row {r}: {', '.join(row_vals)}")
