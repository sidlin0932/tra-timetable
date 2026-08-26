import pandas as pd
import json

df_expr = pd.read_excel('f:/Antigravity/台鐵時刻表0701/KeelungToChaozhou20260701.ods', engine='odf', header=None)
df_loc1 = pd.read_excel('f:/Antigravity/台鐵時刻表0701/基隆→新竹-20260701(0608修).ods', engine='odf', header=None)
df_loc2 = pd.read_excel('f:/Antigravity/台鐵時刻表0701/HsinchuToChanghua20260701.ods', engine='odf', header=None)

valid_trains = []

for c in range(4, len(df_expr.columns)):
    train_num = str(df_expr.iloc[3, c]).strip()
    train_type_cn = str(df_expr.iloc[2, c]).strip()
    if pd.isna(df_expr.iloc[2, c]) or not df_expr.iloc[2, c]: continue
    
    if '3000' in train_type_cn or '普悠瑪' in train_type_cn or '太魯閣' in train_type_cn: continue
    if '自強' not in train_type_cn and '莒光' not in train_type_cn and '區間' not in train_type_cn: continue

    bq_time = str(df_expr.iloc[21, c]).strip()
    tc_time = str(df_expr.iloc[38, c]).strip()
    
    if len(bq_time) >= 4 and ':' in bq_time and len(tc_time) >= 4 and ':' in tc_time:
        valid_trains.append({
            'dep': bq_time,
            'arr': tc_time,
            'train': f'{train_type_cn} {train_num}',
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
            valid_trains.append({
                'dep': bq_time,
                'arr': tc_time,
                'train': f'{train_type_cn} {train_num}',
                'note': '直達'
            })

valid_trains.sort(key=lambda x: x['dep'])
print('--- Earliest 10 ---')
for v in valid_trains[:10]:
    print(f"{v['dep']} -> {v['arr']} ({v['train']})")
print('--- Latest 10 ---')
for v in valid_trains[-10:]:
    print(f"{v['dep']} -> {v['arr']} ({v['train']})")
