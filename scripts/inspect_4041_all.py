# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import pandas as pd

folder = 'f:/Antigravity/台鐵時刻表0701'

# NorthLink 4041
path = os.path.join(folder, 'NorthLink20260701.ods')
xl = pd.ExcelFile(path, engine='odf')
df = xl.parse('北迴線', header=None)
print("=== NorthLink 4041 ===")
for c in range(len(df.columns)):
    st = ''.join([str(df.iloc[r, c]).strip() for r in [1, 2, 3] if pd.notna(df.iloc[r, c]) and str(df.iloc[r, c]).strip() not in ['站名', '起訖站', '備註']])
    val = df.iloc[42, c]
    if pd.notna(val):
        print(f"  Col {c} ({st}): {val}")

# SuaoToBadu 4041
path = os.path.join(folder, 'SuaoToBadu20260701.ods')
xl = pd.ExcelFile(path, engine='odf')
df = xl.parse(xl.sheet_names[0], header=None)
print("\n=== SuaoToBadu 4041 ===")
for c in range(len(df.columns)):
    st = ''.join([str(df.iloc[r, c]).strip() for r in [1, 2, 3] if pd.notna(df.iloc[r, c]) and str(df.iloc[r, c]).strip() not in ['站名', '起訖站', '備註']])
    val = df.iloc[73, c]
    if pd.notna(val):
        print(f"  Col {c} ({st}): {val}")

# KeelungToHsinchu 4041
path = os.path.join(folder, '基隆→新竹-20260701(0608修).ods')
xl = pd.ExcelFile(path, engine='odf')
df = xl.parse(xl.sheet_names[0], header=None)
print("\n=== KeelungToHsinchu 4041 ===")
for c in range(len(df.columns)):
    st = ''.join([str(df.iloc[r, c]).strip() for r in [1, 2, 3] if pd.notna(df.iloc[r, c]) and str(df.iloc[r, c]).strip() not in ['站名', '起訖站', '備註']])
    val = df.iloc[122, c]
    if pd.notna(val):
        print(f"  Col {c} ({st}): {val}")
