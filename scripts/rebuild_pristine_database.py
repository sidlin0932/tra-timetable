# -*- coding: utf-8 -*-
import os
import re
import json
import pandas as pd

print("Rebuilding pristine database with standard chronological stop sorting...")

folder = 'data/raw_ods'

def clean_time(val):
    if pd.isna(val): return None
    val_str = str(val).strip()
    if not val_str or val_str in ['-', '—', '...', 'nan', 'NaT', 'None']:
        return None
    m = re.search(r'(\d{1,2}):(\d{2})', val_str)
    if m:
        h = int(m.group(1))
        minute = int(m.group(2))
        return f"{h:02d}:{minute:02d}"
    return None

def normalize_station(st_raw):
    if not st_raw or pd.isna(st_raw): return ''
    s = str(st_raw).replace('臺', '台').replace('\u3000', '').replace(' ', '').strip()
    if s in ['新城', '新城(太魯閣)', '新城（太魯閣）']:
        return '新城(太魯閣)'
    return s

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

def timeToMin(tStr):
    if not tStr: return 0
    h, m = map(int, tStr.split(':'))
    return h * 60 + m

def sort_stops_chronologically(stops):
    if not stops or len(stops) < 2: return stops
    cleaned = []
    seen = set()
    for s in stops:
        if s['station'] not in seen:
            seen.add(s['station'])
            cleaned.append(s)
            
    has_night = any(timeToMin(s['time']) >= 1200 for s in cleaned)
    has_morning = any(timeToMin(s['time']) < 360 for s in cleaned)
    
    if has_night and has_morning:
        items = []
        for s in cleaned:
            m = timeToMin(s['time'])
            abs_m = (m + 1440) if m < 360 else m
            items.append((abs_m, s))
        items.sort(key=lambda x: x[0])
        return [x[1] for x in items]
    else:
        cleaned.sort(key=lambda s: timeToMin(s['time']))
        return cleaned

EXPRESS_TRAINS = {}
COMMUTER_TRAINS = {}
BRANCH_TRAINS = {}

# 1. Express Western Trunk (Mountain / Sea) - Authoritative
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
        if not t_num.isdigit() or len(t_num) < 3: continue
        
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
            st_raw = df.iloc[r, 1] if pd.notna(df.iloc[r, 1]) else df.iloc[r, 0]
            st = normalize_station(st_raw)
            if not st: continue
            
            is_mountain_st = st in ['苗栗', '豐富', '銅鑼', '三義', '后里', '豐原', '栗林', '潭子', '頭家厝', '松竹', '太原', '精武', '台中', '五權', '大慶', '烏日', '新烏日', '成功']
            is_sea_st = st in ['談文', '大山', '後龍', '龍港', '白沙屯', '新埔', '通霄', '苑裡', '日南', '大甲', '台中港', '清水', '沙鹿', '龍井', '大肚', '追分']
            
            if route_dir == '海線' and is_mountain_st:
                continue
            if route_dir == '山線' and is_sea_st:
                continue
                
            t_str = clean_time(df.iloc[r, c])
            if t_str:
                stops.append({'station': st, 'time': t_str})
                
        if len(stops) >= 2:
            stops = sort_stops_chronologically(stops)
            EXPRESS_TRAINS[t_num] = {
                'train_number': t_num, 'train_type': t_type, 'train_model': t_model,
                'is_trpass': is_tr, 'origin': stops[0]['station'], 'dest': stops[-1]['station'],
                'line': '西部幹線', 'route_dir': route_dir, 'stops': stops
            }

# 2. Eastern Trunk & South-link Express - Authoritative
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
        if not t_num.isdigit() or len(t_num) < 3: continue
        
        raw_type = str(df.iloc[t_row - 1, c]).strip() if t_row >= 1 else ''
        raw_note = str(df.iloc[t_row - 2, c]).strip() if t_row >= 2 else ''
        t_type, t_model, is_tr = extract_type_and_model(raw_type, raw_note)
        
        stops = []
        for r in range(t_row + 1, len(df)):
            st_raw = df.iloc[r, 1] if pd.notna(df.iloc[r, 1]) else df.iloc[r, 0]
            st = normalize_station(st_raw)
            if not st: continue
            t_str = clean_time(df.iloc[r, c])
            if t_str:
                stops.append({'station': st, 'time': t_str})
                
        if len(stops) >= 2:
            stops = sort_stops_chronologically(stops)
            EXPRESS_TRAINS[t_num] = {
                'train_number': t_num, 'train_type': t_type, 'train_model': t_model,
                'is_trpass': is_tr, 'origin': stops[0]['station'], 'dest': stops[-1]['station'],
                'line': line_name, 'route_dir': '', 'stops': stops
            }

# 3. Branch Lines (JIJI, Neiwan, Pingxi, Shalun)
df_jiji = pd.read_excel(os.path.join(folder, 'JIJI20260701.ods'), engine='odf', header=None)
jiji_down_sts = ['二水', '源泉', '濁水', '龍泉', '集集', '水里', '車埕']
jiji_up_sts = ['車埕', '水里', '集集', '龍泉', '濁水', '源泉', '二水']

for r in range(3, len(df_jiji)):
    t_num = str(df_jiji.iloc[r, 2]).strip().replace('.0', '')
    if t_num.isdigit():
        stops = []
        for idx, st in enumerate(jiji_down_sts):
            c_idx = 4 + idx
            if c_idx < df_jiji.shape[1]:
                t_str = clean_time(df_jiji.iloc[r, c_idx])
                if t_str: stops.append({'station': st, 'time': t_str})
        if len(stops) >= 2:
            BRANCH_TRAINS[t_num] = {
                'train_number': t_num, 'train_type': '區間車', 'train_model': '柴油客車',
                'is_trpass': True, 'origin': stops[0]['station'], 'dest': stops[-1]['station'],
                'line': '集集線', 'route_dir': '', 'stops': stops
            }

for r in range(3, len(df_jiji)):
    t_num = str(df_jiji.iloc[r, 14]).strip().replace('.0', '') if df_jiji.shape[1] > 14 else ''
    if t_num.isdigit():
        stops = []
        for idx, st in enumerate(jiji_up_sts):
            c_idx = 16 + idx
            if c_idx < df_jiji.shape[1]:
                t_str = clean_time(df_jiji.iloc[r, c_idx])
                if t_str: stops.append({'station': st, 'time': t_str})
        if len(stops) >= 2:
            BRANCH_TRAINS[t_num] = {
                'train_number': t_num, 'train_type': '區間車', 'train_model': '柴油客車',
                'is_trpass': True, 'origin': stops[0]['station'], 'dest': stops[-1]['station'],
                'line': '集集線', 'route_dir': '', 'stops': stops
            }

# Neiwan
df_neiwan = pd.read_excel(os.path.join(folder, 'Neiwan20260701.ods'), engine='odf', header=None)
neiwan_down_sts = ['新竹', '北新竹', '千甲', '新莊', '竹中', '六家', '上員', '榮華', '竹東', '橫山', '九讚頭', '合興', '富貴', '內灣']
neiwan_up_sts = ['內灣', '富貴', '合興', '九讚頭', '橫山', '竹東', '榮華', '上員', '六家', '竹中', '新莊', '千甲', '北新竹', '新竹']

for r in range(4, 66):
    t_num = ''
    for c in [1, 2, 3]:
        val = str(df_neiwan.iloc[r, c]).strip().replace('.0', '')
        if val.isdigit() and len(val) >= 3: t_num = val; break
    if not t_num: continue
    stops = []
    for idx, st in enumerate(neiwan_down_sts):
        c_idx = 4 + idx
        if c_idx < df_neiwan.shape[1]:
            t_str = clean_time(df_neiwan.iloc[r, c_idx])
            if t_str: stops.append({'station': st, 'time': t_str})
    if len(stops) >= 2:
        BRANCH_TRAINS[t_num] = {
            'train_number': t_num, 'train_type': '區間車', 'train_model': 'EMU系列',
            'is_trpass': True, 'origin': stops[0]['station'], 'dest': stops[-1]['station'],
            'line': '內灣線', 'route_dir': '', 'stops': stops
        }

for r in range(71, len(df_neiwan)):
    t_num = ''
    for c in [1, 2, 3]:
        val = str(df_neiwan.iloc[r, c]).strip().replace('.0', '')
        if val.isdigit() and len(val) >= 3: t_num = val; break
    if not t_num: continue
    stops = []
    for idx, st in enumerate(neiwan_up_sts):
        c_idx = 4 + idx
        if c_idx < df_neiwan.shape[1]:
            t_str = clean_time(df_neiwan.iloc[r, c_idx])
            if t_str: stops.append({'station': st, 'time': t_str})
    if len(stops) >= 2:
        BRANCH_TRAINS[t_num] = {
            'train_number': t_num, 'train_type': '區間車', 'train_model': 'EMU系列',
            'is_trpass': True, 'origin': stops[0]['station'], 'dest': stops[-1]['station'],
            'line': '內灣線', 'route_dir': '', 'stops': stops
        }

# Pingxi
df_px = pd.read_excel(os.path.join(folder, 'PingxiToShenao20260701.ods'), engine='odf', header=None)
px_down_sts = ['八斗子', '海科館', '瑞芳', '猴硐', '三貂嶺', '大華', '十分', '望古', '嶺腳', '平溪', '菁桐']
px_up_sts = ['菁桐', '平溪', '嶺腳', '望古', '十分', '大華', '三貂嶺', '猴硐', '瑞芳', '海科館', '八斗子']

for r in range(4, len(df_px)):
    t_num = ''
    for c in [1, 2, 3]:
        val = str(df_px.iloc[r, c]).strip().replace('.0', '')
        if val.isdigit() and len(val) >= 3: t_num = val; break
    if not t_num: continue
    stops = []
    for idx, st in enumerate(px_down_sts):
        c_idx = 4 + idx
        if c_idx < df_px.shape[1]:
            t_str = clean_time(df_px.iloc[r, c_idx])
            if t_str: stops.append({'station': st, 'time': t_str})
    if len(stops) >= 2:
        BRANCH_TRAINS[t_num] = {
            'train_number': t_num, 'train_type': '區間車', 'train_model': '柴油客車',
            'is_trpass': True, 'origin': stops[0]['station'], 'dest': stops[-1]['station'],
            'line': '平溪/深澳線', 'route_dir': '', 'stops': stops
        }

for r in range(4, len(df_px)):
    t_num = str(df_px.iloc[r, 20]).strip().replace('.0', '') if df_px.shape[1] > 20 else ''
    if not t_num.isdigit() and df_px.shape[1] > 21:
        alt = str(df_px.iloc[r, 21]).strip().replace('.0', '')
        if alt.isdigit(): t_num = alt
    if not t_num.isdigit(): continue
    stops = []
    for idx, st in enumerate(px_up_sts):
        c_idx = 22 + idx
        if c_idx < df_px.shape[1]:
            t_str = clean_time(df_px.iloc[r, c_idx])
            if t_str: stops.append({'station': st, 'time': t_str})
    if len(stops) >= 2:
        BRANCH_TRAINS[t_num] = {
            'train_number': t_num, 'train_type': '區間車', 'train_model': '柴油客車',
            'is_trpass': True, 'origin': stops[0]['station'], 'dest': stops[-1]['station'],
            'line': '平溪/深澳線', 'route_dir': '', 'stops': stops
        }

# Shalun
df_sl = pd.read_excel(os.path.join(folder, 'Shalun2026070.ods'), engine='odf', header=None)
sl_down_sts = ['善化', '南科', '新市', '永康', '大橋', '台南', '保安', '仁德', '中洲', '長榮大學', '沙崙']
sl_up_sts = ['沙崙', '長榮大學', '中洲', '仁德', '保安', '台南', '大橋', '永康', '新市', '南科', '善化']

for r in range(3, len(df_sl)):
    t_num = str(df_sl.iloc[r, 2]).strip().replace('.0', '')
    if t_num.isdigit():
        stops = []
        for idx, st in enumerate(sl_down_sts):
            c_idx = 4 + idx
            if c_idx < df_sl.shape[1]:
                t_str = clean_time(df_sl.iloc[r, c_idx])
                if t_str: stops.append({'station': st, 'time': t_str})
        if len(stops) >= 2:
            BRANCH_TRAINS[t_num] = {
                'train_number': t_num, 'train_type': '區間車', 'train_model': 'EMU系列',
                'is_trpass': True, 'origin': stops[0]['station'], 'dest': stops[-1]['station'],
                'line': '沙崙線', 'route_dir': '', 'stops': stops
            }

for r in range(3, len(df_sl)):
    t_num = str(df_sl.iloc[r, 18]).strip().replace('.0', '') if df_sl.shape[1] > 18 else ''
    if t_num.isdigit():
        stops = []
        for idx, st in enumerate(sl_up_sts):
            c_idx = 20 + idx
            if c_idx < df_sl.shape[1]:
                t_str = clean_time(df_sl.iloc[r, c_idx])
                if t_str: stops.append({'station': st, 'time': t_str})
        if len(stops) >= 2:
            BRANCH_TRAINS[t_num] = {
                'train_number': t_num, 'train_type': '區間車', 'train_model': 'EMU系列',
                'is_trpass': True, 'origin': stops[0]['station'], 'dest': stops[-1]['station'],
                'line': '沙崙線', 'route_dir': '', 'stops': stops
            }

# 4. Commuter files (Dynamic multi-column scan)
commuter_specs = [
    ('BaduToSuao20260701.ods', 0, 7, ['八堵', '暖暖', '四腳亭', '瑞芳', '猴硐', '三貂嶺', '牡丹', '雙溪', '貢寮', '福隆', '石城', '大里', '大溪', '龜山', '外澳', '頭城', '頂埔', '礁溪', '四城', '宜蘭', '二結', '中里', '羅東', '冬山', '新馬', '蘇澳新', '蘇澳'], '宜蘭線'),
    ('SuaoToBadu20260701.ods', 0, 4, ['蘇澳', '蘇澳新', '新馬', '冬山', '羅東', '中里', '二結', '宜蘭', '四城', '礁溪', '頂埔', '頭城', '外澳', '龜山', '大溪', '大里', '石城', '福隆', '貢寮', '雙溪', '牡丹', '三貂嶺', '猴硐', '瑞芳', '四腳亭', '暖暖', '八堵'], '宜蘭線'),
    ('HsinchuToKeelung20260701.ods', 0, 5, ['新竹', '北新竹', '竹北', '新豐', '湖口', '北湖', '新富', '富岡', '楊梅', '埔心', '中壢', '內壢', '桃園', '鶯歌', '山佳', '南樹林', '樹林', '浮洲', '板橋', '萬華', '台北', '松山', '南港', '汐科', '汐止', '五堵', '百福', '七堵', '八堵', '三坑', '基隆'], '縱貫線北段'),
    ('基隆→新竹-20260701(0608修).ods', 0, 5, ['基隆', '三坑', '八堵', '七堵', '百福', '五堵', '汐止', '汐科', '南港', '松山', '台北', '萬華', '板橋', '浮洲', '樹林', '南樹林', '山佳', '鶯歌', '桃園', '內壢', '中壢', '埔心', '楊梅', '富岡', '新富', '北湖', '湖口', '新豐', '竹北', '北新竹', '新竹'], '縱貫線北段'),
    ('HsinchuToChanghua20260701.ods', 0, 4, ['新竹', '三姓橋', '香山', '崎頂', '竹南', '造橋', '豐富', '苗栗', '南勢', '銅鑼', '三義', '泰安', '后里', '豐原', '栗林', '潭子', '頭家厝', '松竹', '太原', '精武', '台中', '五權', '大慶', '烏日', '新烏日', '成功', '彰化'], '台中線(山線)'),
    ('ChanghuaToHsinchu20260701.ods', 0, 4, ['彰化', '成功', '新烏日', '烏日', '大慶', '五權', '台中', '精武', '太原', '松竹', '頭家厝', '潭子', '栗林', '豐原', '后里', '泰安', '三義', '銅鑼', '南勢', '苗栗', '豐富', '造橋', '竹南', '崎頂', '香山', '三姓橋', '新竹'], '台中線(山線)'),
    ('ChanghuaToChiayi20260701.ods', 0, 5, ['彰化', '花壇', '大村', '員林', '永靖', '社頭', '田中', '二水', '林內', '石榴', '斗六', '斗南', '石龜', '大林', '民雄', '嘉北', '嘉義'], '縱貫線南段'),
    ('ChiayiToChanghua20260701.ods', 0, 5, ['嘉義', '嘉北', '民雄', '大林', '石龜', '斗南', '斗六', '石榴', '林內', '二水', '田中', '社頭', '永靖', '員林', '大村', '花壇', '彰化'], '縱貫線南段'),
    ('ChiayiToKaohsiung20260701.ods', 0, 5, ['嘉義', '水上', '南靖', '後壁', '新營', '柳營', '林鳳營', '隆田', '拔林', '善化', '南科', '新市', '永康', '大橋', '台南', '保安', '仁德', '中洲', '大湖', '路竹', '岡山', '橋頭', '楠梓', '新左營', '左營', '內惟', '美術館', '鼓山', '三塊厝', '高雄'], '縱貫線南段'),
    ('KaohsiungToChiayi20260701.ods', 0, 5, ['高雄', '三塊厝', '鼓山', '美術館', '內惟', '左營', '新左營', '楠梓', '橋頭', '岡山', '路竹', '大湖', '中洲', '仁德', '保安', '台南', '大橋', '永康', '新市', '南科', '善化', '拔林', '隆田', '林鳳營', '柳營', '新營', '後壁', '南靖', '水上', '嘉義'], '縱貫線南段'),
    ('XinzuoyingToFangliao20260701.ods', 0, 8, ['新左營', '左營', '內惟', '美術館', '鼓山', '三塊厝', '高雄', '民族', '科工館', '正義', '鳳山', '後庄', '九曲堂', '六塊厝', '屏東', '歸來', '麟洛', '西勢', '竹田', '潮州', '崁頂', '南州', '鎮安', '林邊', '佳冬', '東海', '枋寮'], '屏東線'),
    ('FangliaoToXinzuoying20260701.ods', 0, 8, ['枋寮', '東海', '佳冬', '林邊', '鎮安', '南州', '崁頂', '潮州', '竹田', '西勢', '麟洛', '歸來', '屏東', '六塊厝', '九曲堂', '後庄', '鳳山', '正義', '科工館', '民族', '高雄', '三塊厝', '鼓山', '美術館', '內惟', '左營', '新左營'], '屏東線'),
    ('NorthLink20260701.ods', 1, 4, ['蘇澳新', '永樂', '東澳', '南澳', '武塔', '漢本', '和平', '和仁', '崇德', '新城(太魯閣)', '景美', '北埔', '花蓮'], '北迴線'),
    ('台東線-20260701.ods', 0, 4, ['花蓮', '吉安', '志學', '平和', '壽豐', '豐田', '林榮新光', '南平', '鳳林', '萬榮', '光復', '大富', '富源', '瑞穗', '三民', '玉里', '東里', '東竹', '富里', '池上', '海端', '關山', '月美', '瑞和', '瑞源', '鹿野', '山里', '台東'], '台東線'),
]

for fname, sheet_idx, st_start_col, station_list, line_name in commuter_specs:
    p = os.path.join(folder, fname)
    if not os.path.exists(p):
        cand = [f for f in os.listdir(folder) if fname[:6] in f]
        if cand: p = os.path.join(folder, cand[0])
    if not os.path.exists(p): continue
    
    xl = pd.ExcelFile(p, engine='odf')
    sheet = xl.sheet_names[sheet_idx] if sheet_idx < len(xl.sheet_names) else xl.sheet_names[0]
    df = xl.parse(sheet, header=None)
    
    for r in range(3, len(df)):
        t_num = ''
        t_col = -1
        for c in [1, 2, 3]:
            val = str(df.iloc[r, c]).strip().replace('.0', '')
            if val.isdigit() and len(val) >= 3:
                t_num = val
                t_col = c
                break
        if not t_num: continue
        
        # If train is already in authoritative EXPRESS_TRAINS, do NOT overwrite
        if t_num in EXPRESS_TRAINS:
            continue
            
        raw_type = str(df.iloc[r, max(0, t_col - 1)]).strip()
        raw_note = str(df.iloc[r, max(0, t_col - 2)]).strip()
        t_type, t_model, is_tr = extract_type_and_model(raw_type, raw_note)
        
        stops = []
        for idx, st_name in enumerate(station_list):
            c_idx = st_start_col + idx
            if c_idx < df.shape[1]:
                t_str = clean_time(df.iloc[r, c_idx])
                if t_str: stops.append({'station': st_name, 'time': t_str})
                
        if len(stops) >= 2:
            r_dir = '山線' if '山線' in line_name else ''
            
            if t_num not in COMMUTER_TRAINS:
                COMMUTER_TRAINS[t_num] = {
                    'train_number': t_num, 'train_type': t_type, 'train_model': t_model,
                    'is_trpass': is_tr, 'origin': stops[0]['station'], 'dest': stops[-1]['station'],
                    'line': line_name, 'route_dir': r_dir, 'stops': stops
                }
            else:
                ext = COMMUTER_TRAINS[t_num]
                merged = ext['stops'] + stops
                ext['stops'] = sort_stops_chronologically(merged)
                ext['origin'] = ext['stops'][0]['station']
                ext['dest'] = ext['stops'][-1]['station']

# Final Merge: EXPRESS > BRANCH > COMMUTER
FINAL_MAP = {}
for t_num, t in EXPRESS_TRAINS.items():
    FINAL_MAP[t_num] = t
for t_num, t in BRANCH_TRAINS.items():
    if t_num not in FINAL_MAP:
        FINAL_MAP[t_num] = t
for t_num, t in COMMUTER_TRAINS.items():
    if t_num not in FINAL_MAP:
        FINAL_MAP[t_num] = t

final_list = sorted(FINAL_MAP.values(), key=lambda x: int(x['train_number']) if x['train_number'].isdigit() else 99999)
print(f"Total Complete Pristine Trains: {len(final_list)}")

t2007 = FINAL_MAP.get('2007')
if t2007:
    print(f"Train 2007: {t2007['origin']} -> {t2007['dest']}, last={t2007['stops'][-1]}")

with open('full_network_timetable.json', 'w', encoding='utf-8') as f:
    json.dump(final_list, f, ensure_ascii=False, indent=2)

with open('data.js', 'w', encoding='utf-8') as f:
    f.write('window.EMBEDDED_TIMETABLE_DATA = ' + json.dumps(final_list, ensure_ascii=False, indent=2) + ';')

print("Pristine database successfully saved!")
