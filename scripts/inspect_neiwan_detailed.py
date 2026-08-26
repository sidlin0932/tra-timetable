# -*- coding: utf-8 -*-
import pandas as pd

df = pd.read_excel('Neiwan20260701.ods', engine='odf', header=None)
print(f"Shape: {df.shape}")

print("Header row 0 to 4:")
for r in range(min(5, len(df))):
    row_vals = [f"Col{c}:{df.iloc[r, c]}" for c in range(df.shape[1]) if pd.notna(df.iloc[r, c])]
    print(f"Row {r}: {', '.join(row_vals)}")

print("\nData samples (rows 4 to 15):")
for r in range(4, min(15, len(df))):
    row_vals = [f"Col{c}:{df.iloc[r, c]}" for c in range(df.shape[1]) if pd.notna(df.iloc[r, c])]
    print(f"Row {r}: {', '.join(row_vals)}")
