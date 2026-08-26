import pandas as pd
import os

files = [
    'BaduToSuao20260701.ods',
    'SuaoToBadu20260701.ods',
    'HsinchuToKeelung20260701.ods',
    '基隆→新竹-20260701(0608修).ods',
    'HsinchuToChanghua20260701.ods',
    'ChanghuaToHsinchu20260701.ods',
    'ChanghuaToChiayi20260701.ods',
    'ChiayiToChanghua20260701.ods',
    'ChiayiToKaohsiung20260701.ods',
    'KaohsiungToChiayi20260701.ods',
    'XinzuoyingToFangliao20260701.ods',
    'FangliaoToXinzuoying20260701.ods',
    '台東線-20260701.ods',
    'PingxiToShenao20260701.ods',
    'Neiwan20260701.ods',
    'JIJI20260701.ods',
    'Shalun2026070.ods'
]

with open('auto_headers_result.txt', 'w', encoding='utf-8') as out:
    for fname in files:
        if not os.path.exists(fname): continue
        df = pd.read_excel(fname, engine='odf', header=None)
        
        # Find train number column
        t_col = 2
        for c in range(1, 6):
            nums = [str(df.iloc[r, c]).strip().replace('.0', '') for r in range(3, min(15, len(df))) if pd.notna(df.iloc[r, c])]
            if len(nums) >= 3 and all(n.isdigit() for n in nums):
                t_col = c
                break
                
        # Find station names from rows 0..3
        col_stations = {}
        for c in range(t_col + 1, len(df.columns)):
            chars = []
            for r in [1, 2, 3]:
                if r < len(df) and pd.notna(df.iloc[r, c]):
                    val = str(df.iloc[r, c]).strip().replace('\u3000', '').replace(' ', '')
                    if val and val not in ['站名', '名間', '起訖站', '備註']:
                        chars.append(val)
            st_name = ''.join(chars)
            # clean up
            if st_name:
                col_stations[c] = st_name
                
        out.write(f"=== {fname} (t_col={t_col}) ===\n")
        for c, st in sorted(col_stations.items()):
            out.write(f"  Col {c}: {st}\n")
        out.write("\n")

print("Generated auto_headers_result.txt successfully!")
