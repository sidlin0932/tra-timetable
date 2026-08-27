# -*- coding: utf-8 -*-
import os
import re
import json
import pandas as pd
from datetime import datetime

print("Building Robust Multi-Block Subtable Parser for All Sheets...")

folder = 'data/raw_ods'
ALL_TRAINS = {}

MAJOR_STATIONS = [
    '基隆', '三坑', '八堵', '七堵', '百福', '五堵', '汐止', '汐科', '南港', '松山', '台北', '萬華', '板橋', '浮洲', '樹林',
    '南樹林', '山佳', '鶯歌', '鳳鳴', '桃園', '中路', '內壢', '中壢', '平鎮', '埔心', '楊梅', '富岡', '新豐', '竹北', '北新竹', '新竹', '三姓橋', '香山', '崎頂', '竹南',
    '苗栗', '豐富', '造橋', '銅鑼', '三義', '后里', '豐原', '栗林', '潭子', '頭家厝', '松竹', '太原', '精武', '台中', '五權', '大慶', '烏日',
    '新烏日', '成功', '彰化', '花壇', '大村', '員林', '永靖', '社頭', '田中', '二水', '林內', '石榴', '斗六',
    '斗南', '石龜', '大林', '民雄', '嘉北', '嘉義', '水上', '南靖', '後壁', '新營', '柳營', '林鳳營', '隆田', '拔林', '善化', '南科', '新市', '永康', '大橋', '台南', '保安', '仁德', '中洲', '大湖', '路竹', '岡山', '橋頭', '楠梓', '新左營', '左營', '內惟', '美術館', '鼓山', '三塊厝', '高雄',
    '民族', '科工館', '正義', '鳳山', '後庄', '九曲堂', '六塊厝', '屏東', '歸來', '麟洛', '西勢', '竹田', '潮州', '崁頂', '南州', '鎮安', '林邊', '佳冬', '東海', '枋寮', '加祿', '內獅', '枋山', '大武', '瀧溪', '金崙', '太麻里', '知本', '康樂', '台東', '山里', '鹿野', '瑞源', '瑞和', '關山', '海端', '池上',
    '富里', '東竹', '東里', '玉里', '三民', '瑞穗', '富源', '大富', '光復', '萬榮', '鳳林', '南平', '豐田', '壽豐', '平和', '志學', '吉安', '花蓮', '北埔', '景美', '新城', '新城(太魯閣)', '崇德', '和仁', '和平',
    '漢本', '武塔', '南澳', '東澳', '永樂', '蘇澳新', '蘇澳', '冬山', '羅東', '中里', '二結', '宜蘭', '四城', '礁溪', '頂埔', '頭城', '外澳', '龜山', '大溪', '大里', '石城',
    '福隆', '貢寮', '雙溪', '牡丹', '三貂嶺', '猴硐', '瑞芳', '車埕', '水里', '集集', '龍泉',
    '濁水', '源泉', '菁桐', '平溪', '嶺腳', '望古', '十分', '大華', '三貂嶺', '海科館', '八斗子',
    '內灣', '富貴', '合興', '九讚頭', '橫山', '竹東', '榮華', '上員', '竹中', '六家', '沙崙', '長榮大學', '中洲',
    '追分', '大肚', '龍井', '沙鹿', '清水', '台中港', '大甲', '日南', '苑裡', '通霄', '新埔', '白沙屯', '龍港', '後龍', '大山', '談文'
]

def normalize_station(raw_name):
    if not raw_name or not isinstance(raw_name, str):
        return ''
    s = raw_name.strip().replace('\n', '').replace('\r', '').replace(' ', '').replace('\u3000', '')
    s = s.replace('（', '(').replace('）', ')')
    s = re.sub(r'\(.*?\)', '', s)
    s = s.replace('台', '臺')
    for m in MAJOR_STATIONS:
        m_norm = m.replace('台', '臺')
        if s == m_norm or s == m:
            return m
    s_std = s.replace('臺', '台')
    for m in MAJOR_STATIONS:
        if s_std == m:
            return m
    return s_std

def clean_time(val):
    if pd.isna(val):
        return None
    val_str = str(val).strip()
    if not val_str or val_str in ['-', '—', '...', 'nan', 'NaT', 'None']:
        return None
    m = re.search(r'(\d{1,2}):(\d{2})', val_str)
    if m:
        h = int(m.group(1))
        minute = int(m.group(2))
        return f"{h:02d}:{minute:02d}"
    return None

def extract_type_and_model(raw_type, raw_note=""):
    raw = f"{raw_type} {raw_note}".strip()
    is_trpass = True
    train_model = ""

    if "3000" in raw or "EMU3000" in raw:
        train_type = "新自強(EMU3000)"
        train_model = "EMU3000"
        is_trpass = False
    elif "普悠瑪" in raw:
        train_type = "普悠瑪"
        train_model = "普悠瑪"
        is_trpass = False
    elif "太魯閣" in raw:
        train_type = "太魯閣"
        train_model = "太魯閣"
        is_trpass = False
    elif "自強" in raw:
        train_type = "自強號"
        train_model = "PP自強號/柴聯自強"
        is_trpass = True
    elif "莒光" in raw:
        train_type = "莒光號"
        train_model = "莒光號"
        is_trpass = True
    elif "區間快" in raw:
        train_type = "區間快"
        train_model = "EMU900/EMU800/EMU700"
        is_trpass = True
    elif "區間" in raw:
        train_type = "區間車"
        train_model = "EMU900/EMU800/EMU700"
        is_trpass = True
    else:
        train_type = "區間車"
        train_model = "電車"
        is_trpass = True

    return train_type, train_model, is_trpass

def add_or_merge_train(train_num, train_type, train_model, is_trpass, line_name, stops, route_dir=''):
    if not stops:
        return
    
    seen = set()
    dedup_stops = []
    for s in stops:
        if s['station'] and s['station'] not in seen:
            seen.add(s['station'])
            dedup_stops.append(s)
            
    if len(dedup_stops) < 2:
        return

    if train_num not in ALL_TRAINS:
        ALL_TRAINS[train_num] = {
            'train_number': train_num,
            'train_type': train_type,
            'train_model': train_model,
            'is_trpass': is_trpass,
            'line': line_name,
            'route_dir': route_dir,
            'origin': dedup_stops[0]['station'],
            'dest': dedup_stops[-1]['station'],
            'stops': dedup_stops
        }
    else:
        existing = ALL_TRAINS[train_num]
        ext_stops = {s['station']: s['time'] for s in existing['stops']}
        new_order = [s['station'] for s in existing['stops']]
        for s in dedup_stops:
            st = s['station']
            if st not in ext_stops:
                ext_stops[st] = s['time']
                new_order.append(st)
            else:
                if not ext_stops[st] and s['time']:
                    ext_stops[st] = s['time']
        
        merged_stops = [{'station': st, 'time': ext_stops[st]} for st in new_order if ext_stops.get(st)]
        if len(merged_stops) >= 2:
            existing['stops'] = merged_stops
            existing['origin'] = merged_stops[0]['station']
            existing['dest'] = merged_stops[-1]['station']
            if route_dir and not existing.get('route_dir'):
                existing['route_dir'] = route_dir

def parse_df_blocks(df, default_line_name):
    # Find all header start rows
    block_starts = []
    for r in range(len(df)):
        row_str = ' '.join([str(df.iloc[r, c]) for c in range(min(5, df.shape[1])) if pd.notna(df.iloc[r, c])])
        if '區間' in row_str or '順行' in row_str or '逆行' in row_str or r == 0:
            # Check if within 5 rows there are train numbers
            has_trains = False
            for r_sub in range(r, min(r + 6, len(df))):
                for c_sub in range(min(5, df.shape[1])):
                    val = str(df.iloc[r_sub, c_sub]).strip().replace('.0','')
                    if val.isdigit() and len(val) >= 3:
                        has_trains = True
                        break
                if has_trains: break
            if has_trains and (not block_starts or r - block_starts[-1] > 6):
                block_starts.append(r)

    if not block_starts:
        block_starts = [0]

    for b_idx, start_r in enumerate(block_starts):
        end_r = block_starts[b_idx + 1] if b_idx + 1 < len(block_starts) else len(df)
        
        # Find t_row, t_col within this block
        t_row, t_col = -1, -1
        for r in range(start_r, min(start_r + 6, end_r)):
            for c in range(min(5, df.shape[1])):
                val = str(df.iloc[r, c]).strip().replace('.0','')
                if val.isdigit() and len(val) >= 3:
                    t_row, t_col = r, c
                    break
            if t_row != -1: break
            
        if t_row == -1: continue
        
        # Extract station headers strictly between start_r+1 and t_row-1
        col_to_st = {}
        header_start = max(start_r, t_row - 3)
        for c in range(t_col + 1, df.shape[1]):
            chars = []
            for r in range(header_start, t_row):
                val = str(df.iloc[r, c]).strip().replace('\u3000','').replace(' ','')
                if val and val not in ['nan', 'None', '站名', '起訖站', '備註']:
                    chars.append(val)
            st = normalize_station(''.join(chars))
            if st and len(st) <= 8 and st not in ['起訖', '站名']:
                col_to_st[c] = st
                
        # Parse trains in this block
        for r in range(t_row, end_r):
            t_num = str(df.iloc[r, t_col]).strip().replace('.0','')
            if not t_num.isdigit() and t_col + 1 < df.shape[1]:
                alt_num = str(df.iloc[r, t_col + 1]).strip().replace('.0','')
                if alt_num.isdigit() and len(alt_num) >= 3:
                    t_num = alt_num
                    
            if not t_num.isdigit() or len(t_num) < 3: continue
            
            raw_type = str(df.iloc[r, max(0, t_col - 1)]).strip()
            raw_note = str(df.iloc[r, max(0, t_col - 2)]).strip()
            t_type, t_model, is_tr = extract_type_and_model(raw_type, raw_note)
            
            stops = []
            for c_idx, st_name in sorted(col_to_st.items()):
                t_str = clean_time(df.iloc[r, c_idx])
                if t_str:
                    stops.append({'station': st_name, 'time': t_str})
                    
            r_dir = '山線' if '山線' in default_line_name else ''
            add_or_merge_train(t_num, t_type, t_model, is_tr, default_line_name, stops, r_dir)

# 1. Parse all Branch Lines with Multi-Block Support
branch_files = [
    ('JIJI20260701.ods', '集集線'),
    ('Neiwan20260701.ods', '內灣線'),
    ('PingxiToShenao20260701.ods', '平溪/深澳線'),
    ('Shalun2026070.ods', '沙崙線')
]

for fname, line_name in branch_files:
    p = os.path.join(folder, fname)
    if not os.path.exists(p):
        candidates = [f for f in os.listdir(folder) if fname[:5].lower() in f.lower()]
        if candidates: p = os.path.join(folder, candidates[0])
    if not os.path.exists(p): continue
    
    xl = pd.ExcelFile(p, engine='odf')
    for s_name in xl.sheet_names:
        df = xl.parse(s_name, header=None)
        parse_df_blocks(df, line_name)

# 2. Parse all Commuter files with Multi-Block Support
commuter_files = [
    ('BaduToSuao20260701.ods', 0, '宜蘭線'),
    ('SuaoToBadu20260701.ods', 0, '宜蘭線'),
    ('HsinchuToKeelung20260701.ods', 0, '縱貫線北段'),
    ('基隆→新竹-20260701(0608修).ods', 0, '縱貫線北段'),
    ('HsinchuToChanghua20260701.ods', 0, '台中線(山線)'),
    ('ChanghuaToHsinchu20260701.ods', 0, '台中線(山線)'),
    ('ChanghuaToChiayi20260701.ods', 0, '縱貫線南段'),
    ('ChiayiToChanghua20260701.ods', 0, '縱貫線南段'),
    ('ChiayiToKaohsiung20260701.ods', 0, '縱貫線南段'),
    ('KaohsiungToChiayi20260701.ods', 0, '縱貫線南段'),
    ('XinzuoyingToFangliao20260701.ods', 0, '屏東線'),
    ('FangliaoToXinzuoying20260701.ods', 0, '屏東線'),
    ('NorthLink20260701.ods', 1, '北迴線'),
    ('台東線-20260701.ods', 0, '台東線')
]

for fname, sheet_idx, line_name in commuter_files:
    p = os.path.join(folder, fname)
    if not os.path.exists(p):
        candidates = [f for f in os.listdir(folder) if fname[:6] in f]
        if candidates: p = os.path.join(folder, candidates[0])
    if not os.path.exists(p): continue
    
    xl = pd.ExcelFile(p, engine='odf')
    sheet = xl.sheet_names[sheet_idx] if isinstance(sheet_idx, int) and sheet_idx < len(xl.sheet_names) else xl.sheet_names[0]
    df = xl.parse(sheet, header=None)
    parse_df_blocks(df, line_name)

# 3. Parse Western Trunk Express with accurate mountain/sea splitting
for fname in ['KeelungToChaozhou20260701.ods', 'ChaozhouToKeelung20260701.ods']:
    p = os.path.join(folder, fname)
    if not os.path.exists(p): continue
    df = pd.read_excel(p, engine='odf', header=None)
    
    t_row = 3
    for r in range(1, 6):
        nums = [str(df.iloc[r, c]).strip().replace('.0', '') for c in range(4, min(15, df.shape[1])) if pd.notna(df.iloc[r, c])]
        if len(nums) >= 3 and all(n.isdigit() for n in nums):
            t_row = r
            break
            
    for c in range(4, df.shape[1]):
        t_num = str(df.iloc[t_row, c]).strip().replace('.0', '')
        if not t_num.isdigit(): continue
        
        raw_type = str(df.iloc[t_row - 1, c]).strip() if t_row >= 1 else ''
        raw_note = str(df.iloc[t_row - 2, c]).strip() if t_row >= 2 else ''
        t_type, t_model, is_tr = extract_type_and_model(raw_type, raw_note)
        
        route_dir = ''
        for r_check in range(0, t_row):
            cell_val = str(df.iloc[r_check, c]).strip()
            if '山' in cell_val: route_dir = '山線'
            elif '海' in cell_val: route_dir = '海線'
            elif '成追' in cell_val: route_dir = '成追線'
            
        stops = []
        for r in range(t_row + 1, len(df)):
            st_raw = str(df.iloc[r, 1]).strip() if pd.notna(df.iloc[r, 1]) else (str(df.iloc[r, 0]).strip() if pd.notna(df.iloc[r, 0]) else '')
            st = normalize_station(st_raw)
            if not st: continue
            
            is_mountain_st = st in ['苗栗', '豐富', '銅鑼', '三義', '后里', '豐原', '潭子', '太原', '台中', '新烏日']
            is_sea_st = st in ['竹南', '談文', '大山', '後龍', '龍港', '白沙屯', '新埔', '通霄', '苑裡', '日南', '大甲', '台中港', '清水', '沙鹿', '龍井', '大肚', '追分']
            
            if route_dir == '海線' and is_mountain_st:
                continue
            if route_dir == '山線' and is_sea_st and st != '竹南':
                continue
                
            t_str = clean_time(df.iloc[r, c])
            if t_str:
                stops.append({'station': st, 'time': t_str})
                
        add_or_merge_train(t_num, t_type, t_model, is_tr, '西部幹線', stops, route_dir)

# 4. Parse Eastern Trunk and South-link express
for fname, line_name in [('ShulinToTaitung20260701.ods', '東部幹線'), ('TaitungToShulin20260701.ods', '東部幹線'), ('SouthLink20260701.ods', '南迴線')]:
    p = os.path.join(folder, fname)
    if not os.path.exists(p): continue
    df = pd.read_excel(p, engine='odf', header=None)
    
    t_row = 3
    for r in range(1, 6):
        nums = [str(df.iloc[r, c]).strip().replace('.0', '') for c in range(4, min(15, df.shape[1])) if pd.notna(df.iloc[r, c])]
        if len(nums) >= 3 and all(n.isdigit() for n in nums):
            t_row = r
            break
            
    for c in range(4, df.shape[1]):
        t_num = str(df.iloc[t_row, c]).strip().replace('.0', '')
        if not t_num.isdigit(): continue
        
        raw_type = str(df.iloc[t_row - 1, c]).strip() if t_row >= 1 else ''
        raw_note = str(df.iloc[t_row - 2, c]).strip() if t_row >= 2 else ''
        t_type, t_model, is_tr = extract_type_and_model(raw_type, raw_note)
        
        stops = []
        for r in range(t_row + 1, len(df)):
            st_raw = str(df.iloc[r, 1]).strip() if pd.notna(df.iloc[r, 1]) else (str(df.iloc[r, 0]).strip() if pd.notna(df.iloc[r, 0]) else '')
            st = normalize_station(st_raw)
            if not st: continue
            t_str = clean_time(df.iloc[r, c])
            if t_str:
                stops.append({'station': st, 'time': t_str})
                
        add_or_merge_train(t_num, t_type, t_model, is_tr, line_name, stops)

print(f"Total Trains in Network: {len(ALL_TRAINS)}")

# Verify 2007
t2007 = ALL_TRAINS.get('2007')
if t2007:
    print(f"Train 2007 verified: {t2007['origin']} -> {t2007['dest']}")
    print("Stops of 2007:")
    for s in t2007['stops']:
        print(f"  {s['station']}: {s['time']}")

trains_list = sorted(ALL_TRAINS.values(), key=lambda x: int(x['train_number']) if x['train_number'].isdigit() else 99999)

with open('full_network_timetable.json', 'w', encoding='utf-8') as f:
    json.dump(trains_list, f, ensure_ascii=False, indent=2)

with open('data.js', 'w', encoding='utf-8') as f:
    f.write('window.EMBEDDED_TIMETABLE_DATA = ' + json.dumps(trains_list, ensure_ascii=False, indent=2) + ';')

print("Database successfully synchronized to full_network_timetable.json and data.js!")
