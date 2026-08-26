import pandas as pd
import os

folder = 'f:/Antigravity/台鐵時刻表0701'
files = [f for f in os.listdir(folder) if f.endswith('.ods') and '0701' in f]

for filename in files:
    path = os.path.join(folder, filename)
    try:
        df = pd.read_excel(path, engine='odf', header=None)
    except:
        continue
        
    found = False
    for r in range(min(15, len(df))):
        for c in range(min(15, len(df.columns))):
            val = str(df.iloc[r, c]).strip()
            if '車次' in val or 'Train' in val or '車種' in val:
                print(f'{filename} -> Found \"{val}\" at Row {r}, Col {c}')
                found = True
    if not found:
        print(f'{filename} -> COULD NOT FIND 車次 or 車種')
