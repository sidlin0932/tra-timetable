# -*- coding: utf-8 -*-
import os
import re
import glob
import pandas as pd
import json

folder = 'data/raw_ods'

def clean_time(val):
    if pd.isna(val): return ''
    s = str(val).strip()
    if s.endswith('.0'): s = s[:-2]
    match = re.search(r'(\d{1,2}):(\d{2})', s)
    if match:
        h = int(match.group(1))
        m = int(match.group(2))
        return f"{h:02d}:{m:02d}"
    if s.isdigit() and len(s) in [3, 4]:
        if len(s) == 3: s = '0' + s
        h, m = int(s[:2]), int(s[2:])
        if h < 24 and m < 60:
            return f"{h:02d}:{m:02d}"
    return ''

def time_to_min(time_str):
    if not time_str or ':' not in time_str: return -1
    try:
        h, m = map(int, time_str.split(':'))
        return h * 60 + m
    except:
        return -1

STATION_CLEAN_MAP = {
    '鳳': '鳳山', '松': '松山', '佳': '山佳', '冬': '冬山', '岡': '岡山',
    '屏': '屏東', '潮': '潮州', '枋': '枋寮', '竹': '新竹', '義': '嘉義',
    '南': '南港', '新城': '新城(太魯閣)', '新城太魯閣': '新城(太魯閣)',
    '高雄ArrivalTime': '高雄', 'TaipeiArrivalTime': '台北', 'Kaohsiung': '高雄', 'Taipei': '台北'
}

def normalize_station(st):
    st = str(st).replace('臺', '台').strip()
    st = re.sub(r'[\d:\-－\s\u3000]+', '', st)
    if st in STATION_CLEAN_MAP:
        st = STATION_CLEAN_MAP[st]
    return st

def extract_type_and_model(raw_str, fallback_str=''):
    raw = str(raw_str).strip()
    fallback = str(fallback_str).strip()
    combined = raw + ' ' + fallback
    
    t_type = '區間車'
    t_model = 'EMU系列'
    is_trpass = True
    
    if '3000' in combined or 'EMU3000' in combined:
        t_type = '新自強(EMU3000)'
        t_model = 'EMU3000'
        is_trpass = False
    elif '普悠瑪' in combined or 'TEMU2000' in combined:
        t_type = '普悠瑪'
        t_model = '普悠瑪號'
        is_trpass = False
    elif '太魯閣' in combined or 'TEMU1000' in combined:
        t_type = '太魯閣'
        t_model = '太魯閣號'
        is_trpass = False
    elif '自強' in combined or 'T.C.' in combined:
        t_type = '自強號'
        t_model = 'PP自強號'
        is_trpass = True
    elif '莒光' in combined or 'C.K.' in combined:
        t_type = '莒光號'
        t_model = '莒光號客車'
        is_trpass = True
    elif '區間快' in combined or '快' in combined or 'Fast' in combined:
        t_type = '區間快'
        t_model = 'EMU900/EMU800'
        is_trpass = True
    elif '區間' in combined or 'Local' in combined:
        t_type = '區間車'
        t_model = 'EMU系列'
        is_trpass = True
        
    return t_type, t_model, is_trpass

all_trains = []

# 1. Parse Branch Lines
# Neiwan
path = os.path.join(folder, 'Neiwan20260701.ods')
if os.path.exists(path):
    df = pd.read_excel(path, engine='odf', header=None)
    down_cols = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    down_stations = ['新竹', '北新竹', '千甲', '新莊', '竹中', '六家', '上員', '榮華', '竹東', '橫山', '九讚頭', '合興', '富貴', '內灣']
    for r in range(4, 67):
        t_num = str(df.iloc[r, 2]).strip().replace('.0', '')
        if not t_num.isdigit(): continue
        stops = []
        for c_idx, st_name in zip(down_cols, down_stations):
            if c_idx < df.shape[1]:
                t_str = clean_time(df.iloc[r, c_idx])
                if t_str: stops.append({'station': st_name, 'time': t_str})
        if len(stops) >= 2:
            all_trains.append({
                'train_number': t_num,
                'train_type': '區間車',
                'train_model': 'DR1000/EMU',
                'is_trpass': True,
                'origin': stops[0]['station'],
                'dest': stops[-1]['station'],
                'line': '內灣/六家線',
                'route_dir': '',
                'stops': stops
            })
        
    up_cols = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    up_stations = ['內灣', '富貴', '合興', '九讚頭', '橫山', '竹東', '榮華', '上員', '六家', '竹中', '新莊', '千甲', '北新竹', '新竹']
    for r in range(71, len(df)):
        t_num = str(df.iloc[r, 2]).strip().replace('.0', '')
        if not t_num.isdigit(): continue
        stops = []
        for c_idx, st_name in zip(up_cols, up_stations):
            if c_idx < df.shape[1]:
                t_str = clean_time(df.iloc[r, c_idx])
                if t_str: stops.append({'station': st_name, 'time': t_str})
        if len(stops) >= 2:
            all_trains.append({
                'train_number': t_num,
                'train_type': '區間車',
                'train_model': 'DR1000/EMU',
                'is_trpass': True,
                'origin': stops[0]['station'],
                'dest': stops[-1]['station'],
                'line': '內灣/六家線',
                'route_dir': '',
                'stops': stops
            })

# Pingxi
path = os.path.join(folder, 'PingxiToShenao20260701.ods')
if os.path.exists(path):
    df = pd.read_excel(path, engine='odf', header=None)
    down_cols = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    down_stations = ['八堵', '暖暖', '四腳亭', '八斗子', '海科館', '瑞芳', '猴硐', '三貂嶺', '大華', '十分', '望古', '嶺腳', '平溪', '菁桐']
    for r in range(4, len(df)):
        t_num = ''
        for c in [1, 2, 3]:
            val = str(df.iloc[r, c]).strip().replace('.0', '')
            if val.isdigit():
                t_num = val
                break
        if not t_num: continue
        stops = []
        for c_idx, st_name in zip(down_cols, down_stations):
            if c_idx < df.shape[1]:
                t_str = clean_time(df.iloc[r, c_idx])
                if t_str: stops.append({'station': st_name, 'time': t_str})
        if len(stops) >= 2:
            all_trains.append({
                'train_number': t_num,
                'train_type': '區間車',
                'train_model': 'DR1000柴油客車',
                'is_trpass': True,
                'origin': stops[0]['station'],
                'dest': stops[-1]['station'],
                'line': '平溪/深澳線',
                'route_dir': '',
                'stops': stops
            })
        
    up_cols = [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
    up_stations = ['菁桐', '平溪', '嶺腳', '望古', '十分', '大華', '三貂嶺', '猴硐', '瑞芳', '海科館', '八斗子', '四腳亭', '暖暖', '八堵']
    for r in range(4, len(df)):
        t_num = ''
        for c in [19, 20, 21, 22]:
            if c < df.shape[1]:
                val = str(df.iloc[r, c]).strip().replace('.0', '')
                if val.isdigit():
                    t_num = val
                    break
        if not t_num: continue
        stops = []
        for c_idx, st_name in zip(up_cols, up_stations):
            if c_idx < df.shape[1]:
                t_str = clean_time(df.iloc[r, c_idx])
                if t_str: stops.append({'station': st_name, 'time': t_str})
        if len(stops) >= 2:
            all_trains.append({
                'train_number': t_num,
                'train_type': '區間車',
                'train_model': 'DR1000柴油客車',
                'is_trpass': True,
                'origin': stops[0]['station'],
                'dest': stops[-1]['station'],
                'line': '平溪/深澳線',
                'route_dir': '',
                'stops': stops
            })

# Jiji
path = os.path.join(folder, 'JIJI20260701.ods')
if os.path.exists(path):
    df = pd.read_excel(path, engine='odf', header=None)
    jiji_down_cols = [4, 5, 6, 7, 8, 9, 10]
    jiji_down_sts = ['二水', '源泉', '濁水', '龍泉', '集集', '水里', '車埕']
    for r in range(4, len(df)):
        t_num = str(df.iloc[r, 2]).strip().replace('.0', '') if df.shape[1] > 2 else ''
        if not t_num.isdigit(): continue
        stops = []
        for c_idx, st_name in zip(jiji_down_cols, jiji_down_sts):
            if c_idx < df.shape[1]:
                t_str = clean_time(df.iloc[r, c_idx])
                if t_str: stops.append({'station': st_name, 'time': t_str})
        if len(stops) >= 2:
            all_trains.append({
                'train_number': t_num,
                'train_type': '區間車',
                'train_model': 'DR1000柴油客車',
                'is_trpass': True,
                'origin': stops[0]['station'],
                'dest': stops[-1]['station'],
                'line': '集集線',
                'route_dir': '',
                'stops': stops
            })
        
    jiji_up_cols = [16, 17, 18, 19, 20, 21, 22]
    jiji_up_sts = ['車埕', '水里', '集集', '龍泉', '濁水', '源泉', '二水']
    for r in range(4, len(df)):
        t_num = str(df.iloc[r, 14]).strip().replace('.0', '') if df.shape[1] > 14 else ''
        if not t_num.isdigit(): continue
        stops = []
        for c_idx, st_name in zip(jiji_up_cols, jiji_up_sts):
            if c_idx < df.shape[1]:
                t_str = clean_time(df.iloc[r, c_idx])
                if t_str: stops.append({'station': st_name, 'time': t_str})
        if len(stops) >= 2:
            all_trains.append({
                'train_number': t_num,
                'train_type': '區間車',
                'train_model': 'DR1000柴油客車',
                'is_trpass': True,
                'origin': stops[0]['station'],
                'dest': stops[-1]['station'],
                'line': '集集線',
                'route_dir': '',
                'stops': stops
            })

# Shalun
path = os.path.join(folder, 'Shalun2026070.ods')
if os.path.exists(path):
    df = pd.read_excel(path, engine='odf', header=None)
    shalun_down_sts = ['善化', '南科', '新市', '永康', '大橋', '台南', '保安', '仁德', '中洲', '長榮大學', '沙崙']
    for r in range(3, len(df)):
        t_num = str(df.iloc[r, 2]).strip().replace('.0', '')
        if not t_num.isdigit(): continue
        stops = []
        for c_idx, st_name in enumerate(shalun_down_sts, start=4):
            if c_idx < df.shape[1]:
                t_str = clean_time(df.iloc[r, c_idx])
                if t_str: stops.append({'station': st_name, 'time': t_str})
        if len(stops) >= 2:
            all_trains.append({
                'train_number': t_num,
                'train_type': '區間車',
                'train_model': 'EMU系列',
                'is_trpass': True,
                'origin': stops[0]['station'],
                'dest': stops[-1]['station'],
                'line': '沙崙線',
                'route_dir': '',
                'stops': stops
            })
        
    shalun_up_sts = ['沙崙', '長榮大學', '中洲', '仁德', '保安', '台南', '大橋', '永康', '新市', '南科', '善化']
    for r in range(3, len(df)):
        t_num = str(df.iloc[r, 18]).strip().replace('.0', '') if df.shape[1] > 18 else ''
        if not t_num.isdigit(): continue
        stops = []
        for c_idx, st_name in enumerate(shalun_up_sts, start=20):
            if c_idx < df.shape[1]:
                t_str = clean_time(df.iloc[r, c_idx])
                if t_str: stops.append({'station': st_name, 'time': t_str})
        if len(stops) >= 2:
            all_trains.append({
                'train_number': t_num,
                'train_type': '區間車',
                'train_model': 'EMU系列',
                'is_trpass': True,
                'origin': stops[0]['station'],
                'dest': stops[-1]['station'],
                'line': '沙崙線',
                'route_dir': '',
                'stops': stops
            })

# 2. Commuter Lines (Format B)
commuter_specs = [
    ('BaduToSuao20260701.ods', 0, ['八堵', '暖暖', '四腳亭', '瑞芳', '猴硐', '三貂嶺', '牡丹', '雙溪', '貢寮', '福隆', '石城', '大里', '大溪', '龜山', '外澳', '頭城', '頂埔', '礁溪', '四城', '宜蘭', '二結', '中里', '羅東', '冬山', '新馬', '蘇澳新', '蘇澳'], '宜蘭線'),
    ('SuaoToBadu20260701.ods', 0, ['蘇澳', '蘇澳新', '新馬', '冬山', '羅東', '中里', '二結', '宜蘭', '四城', '礁溪', '頂埔', '頭城', '外澳', '龜山', '大溪', '大里', '石城', '福隆', '貢寮', '雙溪', '牡丹', '三貂嶺', '猴硐', '瑞芳', '四腳亭', '暖暖', '八堵'], '宜蘭線'),
    ('HsinchuToKeelung20260701.ods', 0, ['新竹', '北新竹', '竹北', '新豐', '湖口', '北湖', '新富', '富岡', '楊梅', '埔心', '中壢', '內壢', '桃園', '鶯歌', '山佳', '南樹林', '樹林', '浮洲', '板橋', '萬華', '台北', '松山', '南港', '汐科', '汐止', '五堵', '百福', '七堵', '八堵', '三坑', '基隆'], '縱貫線北段'),
    ('基隆→新竹-20260701(0608修).ods', 0, ['基隆', '三坑', '八堵', '七堵', '百福', '五堵', '汐止', '汐科', '南港', '松山', '台北', '萬華', '板橋', '浮洲', '樹林', '南樹林', '山佳', '鶯歌', '桃園', '內壢', '中壢', '埔心', '楊梅', '富岡', '新富', '北湖', '湖口', '新豐', '竹北', '北新竹', '新竹'], '縱貫線北段'),
    ('HsinchuToChanghua20260701.ods', 0, ['新竹', '三姓橋', '香山', '崎頂', '竹南', '造橋', '豐富', '苗栗', '南勢', '銅鑼', '三義', '泰安', '后里', '豐原', '栗林', '潭子', '頭家厝', '松竹', '太原', '精武', '台中', '五權', '大慶', '烏日', '新烏日', '成功', '彰化'], '台中線(山線)'),
    ('ChanghuaToHsinchu20260701.ods', 0, ['彰化', '成功', '新烏日', '烏日', '大慶', '五權', '台中', '精武', '太原', '松竹', '頭家厝', '潭子', '栗林', '豐原', '后里', '泰安', '三義', '銅鑼', '南勢', '苗栗', '豐富', '造橋', '竹南', '崎頂', '香山', '三姓橋', '新竹'], '台中線(山線)'),
    ('ChanghuaToChiayi20260701.ods', 0, ['彰化', '花壇', '大村', '員林', '永靖', '社頭', '田中', '二水', '林內', '石榴', '斗六', '斗南', '石龜', '大林', '民雄', '嘉北', '嘉義'], '縱貫線南段'),
    ('ChiayiToChanghua20260701.ods', 0, ['嘉義', '嘉北', '民雄', '大林', '石龜', '斗南', '斗六', '石榴', '林內', '二水', '田中', '社頭', '永靖', '員林', '大村', '花壇', '彰化'], '縱貫線南段'),
    ('ChiayiToKaohsiung20260701.ods', 0, ['嘉義', '水上', '南靖', '後壁', '新營', '柳營', '林鳳營', '隆田', '拔林', '善化', '南科', '新市', '永康', '大橋', '台南', '保安', '仁德', '中洲', '大湖', '路竹', '岡山', '橋頭', '楠梓', '新左營', '左營', '內惟', '美術館', '鼓山', '三塊厝', '高雄'], '縱貫線南段'),
    ('KaohsiungToChiayi20260701.ods', 0, ['高雄', '三塊厝', '鼓山', '美術館', '內惟', '左營', '新左營', '楠梓', '橋頭', '岡山', '路竹', '大湖', '中洲', '仁德', '保安', '台南', '大橋', '永康', '新市', '南科', '善化', '拔林', '隆田', '林鳳營', '柳營', '新營', '後壁', '南靖', '水上', '嘉義'], '縱貫線南段'),
    ('XinzuoyingToFangliao20260701.ods', 0, ['新左營', '左營', '內惟', '美術館', '鼓山', '三塊厝', '高雄', '民族', '科工館', '正義', '鳳山', '後庄', '九曲堂', '六塊厝', '屏東', '歸來', '麟洛', '西勢', '竹田', '潮州', '崁頂', '南州', '鎮安', '林邊', '佳冬', '東海', '枋寮'], '屏東線'),
    ('FangliaoToXinzuoying20260701.ods', 0, ['枋寮', '東海', '佳冬', '林邊', '鎮安', '南州', '崁頂', '潮州', '竹田', '西勢', '麟洛', '歸來', '屏東', '六塊厝', '九曲堂', '後庄', '鳳山', '正義', '科工館', '民族', '高雄', '三塊厝', '鼓山', '美術館', '內惟', '左營', '新左營'], '屏東線'),
    ('NorthLink20260701.ods', 1, ['蘇澳新', '永樂', '東澳', '南澳', '武塔', '漢本', '和平', '和仁', '崇德', '新城(太魯閣)', '景美', '北埔', '花蓮'], '北迴線'),
    ('台東線-20260701.ods', 0, ['花蓮', '吉安', '志學', '平和', '壽豐', '豐田', '林榮新光', '南平', '鳳林', '萬榮', '光復', '大富', '富源', '瑞穗', '三民', '玉里', '東里', '東竹', '富里', '池上', '海端', '關山', '月美', '瑞和', '瑞源', '鹿野', '山里', '台東'], '台東線'),
]

for fname, sheet_idx, station_list, line_name in commuter_specs:
    path = os.path.join(folder, fname)
    if not os.path.exists(path):
        candidates = [f for f in os.listdir(folder) if fname[:6] in f]
        if candidates: path = os.path.join(folder, candidates[0])
    if not os.path.exists(path): continue
    try:
        xl = pd.ExcelFile(path, engine='odf')
        sheet = xl.sheet_names[sheet_idx] if isinstance(sheet_idx, int) and sheet_idx < len(xl.sheet_names) else xl.sheet_names[0]
        df = xl.parse(sheet, header=None)
        
        t_col = 2
        for c in range(1, 5):
            nums = [str(df.iloc[r, c]).strip().replace('.0', '') for r in range(3, min(15, len(df))) if pd.notna(df.iloc[r, c])]
            if len(nums) >= 3 and all(n.isdigit() for n in nums):
                t_col = c
                break
                
        st_start_col = t_col + 2
        for r in range(3, len(df)):
            t_num = str(df.iloc[r, t_col]).strip().replace('.0', '')
            if not t_num.isdigit(): continue
            
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
                all_trains.append({
                    'train_number': t_num,
                    'train_type': t_type,
                    'train_model': t_model,
                    'is_trpass': is_tr,
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': line_name,
                    'route_dir': r_dir,
                    'stops': stops
                })
    except Exception as e:
        print(f'Error parsing commuter {fname}: {e}')

# 3. Mainline Express Trains with Split Mountain/Sea stations
for fname in ['KeelungToChaozhou20260701.ods', 'ChaozhouToKeelung20260701.ods']:
    path = os.path.join(folder, fname)
    if not os.path.exists(path):
        candidates = [f for f in os.listdir(folder) if fname[:6] in f]
        if candidates: path = os.path.join(folder, candidates[0])
    if not os.path.exists(path): continue
    
    try:
        df = pd.read_excel(path, engine='odf', header=None)
        t_row = 3
        for r in range(1, 6):
            nums = [str(df.iloc[r, c]).strip().replace('.0', '') for c in range(4, min(15, df.shape[1])) if pd.notna(df.iloc[r, c])]
            if len(nums) >= 3 and all(n.isdigit() for n in nums):
                t_row = r
                break
                
        stations = []
        for r in range(t_row + 2, len(df)):
            c0 = normalize_station(df.iloc[r, 0]) if pd.notna(df.iloc[r, 0]) else ''
            c4 = normalize_station(df.iloc[r, 4]) if df.shape[1] > 4 and pd.notna(df.iloc[r, 4]) else ''
            if c4:
                stations.append({'row': r, 'sea': c0, 'mountain': c4, 'is_split': True})
            elif c0 and c0 not in ['nan', '站名', '起訖站', '備註']:
                stations.append({'row': r, 'name': c0, 'is_split': False})
                
        type_row = max(0, t_row - 1)
        model_row = max(0, t_row - 2)
        marker_row = t_row + 1
        
        for c in range(4, df.shape[1]):
            t_num = str(df.iloc[t_row, c]).strip().replace('.0', '')
            if not t_num.isdigit(): continue
            
            raw_type = str(df.iloc[type_row, c]).strip()
            raw_model = str(df.iloc[model_row, c]).strip()
            t_type, t_model, is_tr = extract_type_and_model(raw_type, raw_model)
            
            marker = str(df.iloc[marker_row, c]).strip() if marker_row < len(df) and pd.notna(df.iloc[marker_row, c]) else ''
            is_mountain = ('s' in marker or '山' in marker)
            is_sea = ('c' in marker or '海' in marker)
            r_dir = '山線' if is_mountain else ('海線' if is_sea else '')
            
            stops = []
            for st in stations:
                t_str = clean_time(df.iloc[st['row'], c])
                if t_str:
                    if st.get('is_split'):
                        st_name = st['mountain'] if is_mountain else st['sea']
                    else:
                        st_name = st['name']
                    stops.append({'station': st_name, 'time': t_str})
                    
            if len(stops) >= 2:
                line_desc = f"西部幹線 ({r_dir})" if r_dir else "西部幹線"
                all_trains.append({
                    'train_number': t_num,
                    'train_type': t_type,
                    'train_model': t_model,
                    'is_trpass': is_tr,
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': line_desc,
                    'route_dir': r_dir,
                    'stops': stops
                })
    except Exception as e:
        print(f'Error parsing express {fname}: {e}')

# 4. Other Express Lines
other_express = [
    ('ShulinToTaitung20260701.ods', '東部幹線'),
    ('TaitungToShulin20260701.ods', '東部幹線'),
    ('XinzuoyingToFangliaoToTaitung20260701.ods', '南迴線'),
    ('南迴線(台東→枋寮→新左營)-20260701.ods', '南迴線')
]

for fname, line_name in other_express:
    path = os.path.join(folder, fname)
    if not os.path.exists(path):
        candidates = [f for f in os.listdir(folder) if fname[:6] in f]
        if candidates: path = os.path.join(folder, candidates[0])
    if not os.path.exists(path): continue
    
    try:
        df = pd.read_excel(path, engine='odf', header=None)
        t_row = 3
        for r in range(1, 6):
            nums = [str(df.iloc[r, c]).strip().replace('.0', '') for c in range(4, min(15, df.shape[1])) if pd.notna(df.iloc[r, c])]
            if len(nums) >= 3 and all(n.isdigit() for n in nums):
                t_row = r
                break
                
        stations = []
        for r in range(t_row + 2, len(df)):
            c0 = normalize_station(df.iloc[r, 0]) if pd.notna(df.iloc[r, 0]) else ''
            if c0 and c0 not in ['nan', '站名', '起訖站', '備註']:
                stations.append({'row': r, 'name': c0})
                
        type_row = max(0, t_row - 1)
        model_row = max(0, t_row - 2)
        
        for c in range(4, df.shape[1]):
            t_num = str(df.iloc[t_row, c]).strip().replace('.0', '')
            if not t_num.isdigit(): continue
            
            raw_type = str(df.iloc[type_row, c]).strip()
            raw_model = str(df.iloc[model_row, c]).strip()
            t_type, t_model, is_tr = extract_type_and_model(raw_type, raw_model)
            
            stops = []
            for st in stations:
                t_str = clean_time(df.iloc[st['row'], c])
                if t_str:
                    stops.append({'station': st['name'], 'time': t_str})
                    
            if len(stops) >= 2:
                all_trains.append({
                    'train_number': t_num,
                    'train_type': t_type,
                    'train_model': t_model,
                    'is_trpass': is_tr,
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': line_name,
                    'route_dir': '',
                    'stops': stops
                })
    except Exception as e:
        print(f'Error parsing {fname}: {e}')

# Deduplicate and Merge trains by train number using chronological / monotonic unwrap
mountain_unique = set(['造橋', '豐富', '苗栗', '南勢', '銅鑼', '三義', '泰安', '后里', '豐原', '栗林', '潭子', '頭家厝', '松竹', '太原', '精武', '台中', '五權', '大慶', '烏日', '新烏日', '成功'])
sea_unique = set(['談文', '大山', '後龍', '龍港', '白沙屯', '新埔', '通霄', '苑裡', '日南', '大甲', '台中港', '清水', '沙鹿', '龍井', '大肚', '追分'])

merged = {}
for t in all_trains:
    num = t['train_number']
    if num not in merged:
        merged[num] = t
    else:
        existing = merged[num]
        existing_times = {s['station']: s['time'] for s in existing['stops']}
        for s in t['stops']:
            if s['station'] not in existing_times:
                existing['stops'].append(s)
            else:
                existing_times[s['station']] = s['time']
                
        # Preserve express train types over commuter train types
        if ('自強' in t['train_type'] or '普悠瑪' in t['train_type'] or '太魯閣' in t['train_type'] or '莒光' in t['train_type']) and existing['train_type'] == '區間車':
            existing['train_type'] = t['train_type']
            existing['train_model'] = t['train_model']
            existing['is_trpass'] = t['is_trpass']
            existing['line'] = t['line']

        if t.get('route_dir'):
            existing['route_dir'] = t['route_dir']

# Sort stops for each train
for num, t in merged.items():
    # Unwrap midnight crossings
    unwrapped = []
    curr_offset = 0
    prev_m = -1
    for s in t['stops']:
        m = time_to_min(s['time'])
        if prev_m != -1 and m < (prev_m % 1440) and (prev_m % 1440) - m > 360:
            curr_offset += 1440
        abs_m = curr_offset + m
        prev_m = abs_m
        unwrapped.append({'station': s['station'], 'time': s['time'], 'abs_m': abs_m})
    unwrapped.sort(key=lambda x: x['abs_m'])
    
    # Remove consecutive identical stations
    dedup = []
    for s in unwrapped:
        if not dedup or dedup[-1]['station'] != s['station']:
            dedup.append({'station': s['station'], 'time': s['time']})
        else:
            dedup[-1] = {'station': s['station'], 'time': s['time']}
            
    t['stops'] = dedup
    t['origin'] = dedup[0]['station']
    t['dest'] = dedup[-1]['station']

    # Classify route_dir if empty
    st_names = [s['station'] for s in dedup]
    m_count = sum(1 for s in st_names if s in mountain_unique)
    s_count = sum(1 for s in st_names if s in sea_unique)
    if m_count > 0 and s_count > 0:
        t['route_dir'] = '成追線'
    elif m_count > 0:
        t['route_dir'] = '山線'
    elif s_count > 0:
        t['route_dir'] = '海線'
    elif not t.get('route_dir'):
        t['route_dir'] = ''

final_train_list = list(merged.values())
final_train_list.sort(key=lambda x: int(x['train_number']) if x['train_number'].isdigit() else 99999)

print(f"Total Unique Trains: {len(final_train_list)}")
mt_trains = [t for t in final_train_list if t.get('route_dir') == '山線']
sea_trains = [t for t in final_train_list if t.get('route_dir') == '海線']
cz_trains = [t for t in final_train_list if t.get('route_dir') == '成追線']
print(f"Mountain line trains: {len(mt_trains)}, Sea line trains: {len(sea_trains)}, Cheng-Zhui: {len(cz_trains)}")

# Write to full_network_timetable.json and data.js
with open('full_network_timetable.json', 'w', encoding='utf-8') as f:
    json.dump(final_train_list, f, ensure_ascii=False, indent=2)

with open('data.js', 'w', encoding='utf-8') as f:
    f.write('window.EMBEDDED_TIMETABLE_DATA = ' + json.dumps(final_train_list, ensure_ascii=False) + ';')

print("Successfully exported to full_network_timetable.json and data.js!")
