import pandas as pd
import json
import re

df_expr = pd.read_excel('f:/Antigravity/台鐵時刻表0701/KeelungToChaozhou20260701.ods', engine='odf', header=None)
df_loc1 = pd.read_excel('f:/Antigravity/台鐵時刻表0701/基隆→新竹-20260701(0608修).ods', engine='odf', header=None)
df_loc2 = pd.read_excel('f:/Antigravity/台鐵時刻表0701/HsinchuToChanghua20260701.ods', engine='odf', header=None)

valid_trains = []

def fix_garbled_type(garbled_str):
    if '3000' in garbled_str or '普悠瑪' in garbled_str or '太魯閣' in garbled_str:
        return None
    if 'j' in garbled_str or '自強' in garbled_str:
        return '自強'
    if '' in garbled_str or '區間' in garbled_str:
        return '區間快' if '2005' in garbled_str or '2011' in garbled_str or '2017' in garbled_str else '區間車'
    if '莒' in garbled_str or '653' in garbled_str or '513' in garbled_str:
        return '莒光'
    return garbled_str

for c in range(4, len(df_expr.columns)):
    train_num = str(df_expr.iloc[3, c]).strip()
    train_type_cn = str(df_expr.iloc[2, c]).strip()
    if pd.isna(df_expr.iloc[2, c]) or not df_expr.iloc[2, c]: continue
    
    # Filter TR-PASS valid
    if '3000' in train_type_cn or '普悠瑪' in train_type_cn or '太魯閣' in train_type_cn: continue
    
    clean_type = fix_garbled_type(train_type_cn)
    if clean_type is None: continue

    bq_time = str(df_expr.iloc[21, c]).strip()
    tc_time = str(df_expr.iloc[38, c]).strip()
    
    if len(bq_time) >= 4 and ':' in bq_time and len(tc_time) >= 4 and ':' in tc_time:
        valid_trains.append({
            'departure': bq_time,
            'arrival': tc_time,
            'train_type': clean_type,
            'train_number': train_num,
            'note': '直達'
        })

bq_col = 17
tc_col = 28

mountain_trains = {}
for r in range(3, len(df_loc2)):
    train_num = str(df_loc2.iloc[r, 2]).strip().replace('.0', '')
    train_type_cn = str(df_loc2.iloc[r, 0]).strip()
    tc_time = str(df_loc2.iloc[r, tc_col]).strip()
    if len(tc_time) >= 4 and ':' in tc_time:
        mountain_trains[train_num] = (tc_time, train_type_cn)

for r in range(3, len(df_loc1)):
    train_num = str(df_loc1.iloc[r, 2]).strip().replace('.0', '')
    train_type_cn = str(df_loc1.iloc[r, 0]).strip()
    bq_time = str(df_loc1.iloc[r, bq_col]).strip()
    
    if len(bq_time) >= 4 and ':' in bq_time:
        if train_num in mountain_trains:
            tc_time, _ = mountain_trains[train_num]
            clean_type = fix_garbled_type(train_type_cn + ' ' + train_num)
            valid_trains.append({
                'departure': bq_time,
                'arrival': tc_time,
                'train_type': clean_type,
                'train_number': train_num,
                'note': '直達'
            })

# Remove duplicates if any
seen = set()
unique_trains = []
for v in valid_trains:
    key = v['train_number']
    if key not in seen:
        seen.add(key)
        unique_trains.append(v)

unique_trains.sort(key=lambda x: x['departure'])

# Output JSON
with open('f:/Antigravity/台鐵時刻表0701/banqiao_taichung_timetable.json', 'w', encoding='utf-8') as f:
    json.dump({'trains': unique_trains}, f, ensure_ascii=False, indent=4)

# Output MD for top 10 earliest and latest
earliest_10 = unique_trains[:10]
latest_10 = unique_trains[-10:]

md_content = "# 板橋至台中 TR-PASS 學生版【最早與最晚10班直達車】\n\n"
md_content += "## 🌅 最早 10 班組合\n"
md_content += "| 發車時間 | 抵達時間 | 車種 | 車次 | 備註 |\n|---|---|---|---|---|\n"
for t in earliest_10:
    md_content += f"| {t['departure']} | {t['arrival']} | {t['train_type']} | {t['train_number']} | {t['note']} |\n"

md_content += "\n## 🌙 最晚 10 班組合\n"
md_content += "| 發車時間 | 抵達時間 | 車種 | 車次 | 備註 |\n|---|---|---|---|---|\n"
for t in latest_10:
    md_content += f"| {t['departure']} | {t['arrival']} | {t['train_type']} | {t['train_number']} | {t['note']} |\n"

with open('f:/Antigravity/台鐵時刻表0701/banqiao_taichung_timetable.md', 'w', encoding='utf-8') as f:
    f.write(md_content)

print('Files generated successfully.')
