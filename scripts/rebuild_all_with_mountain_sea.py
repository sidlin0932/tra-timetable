import os
import json
import pandas as pd
import re

folder = 'data/raw_ods'

def clean_time(val):
    if pd.isna(val): return None
    s = str(val).strip()
    if s.endswith('.0'): s = s[:-2]
    match = re.search(r'(\d{1,2}):(\d{2})', s)
    if match:
        h, m = int(match.group(1)), int(match.group(2))
        return f"{h:02d}:{m:02d}"
    if s.isdigit() and len(s) in [3, 4]:
        if len(s) == 3: s = '0' + s
        h, m = int(s[:2]), int(s[2:])
        if h < 24 and m < 60:
            return f"{h:02d}:{m:02d}"
    return None

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

all_trains_map = {}

def t_min(t_str):
    h, m = map(int, t_str.split(':'))
    return h * 60 + m

def unwrap_stops(stops):
    if not stops: return []
    unwrapped = []
    current_day_offset = 0
    prev_min = -1
    
    for s in stops:
        st_name = normalize_station(s['station'])
        raw_m = t_min(s['time'])
        if prev_min != -1 and raw_m < (prev_min % 1440) and (prev_min % 1440) - raw_m > 360:
            current_day_offset += 1440
        abs_min = current_day_offset + raw_m
        prev_min = abs_min
        unwrapped.append({
            'station': st_name,
            'time': s['time'],
            'abs_min': abs_min
        })
    return unwrapped

def add_or_merge_train(t_num, t_type, t_model, is_tr, line, stops, route_dir=''):
    if len(stops) < 2: return
    unwrapped_new = unwrap_stops(stops)
    
    # Deduplicate consecutive identical stations
    dedup_stops = []
    for s in unwrapped_new:
        if not dedup_stops or dedup_stops[-1]['station'] != s['station']:
            dedup_stops.append(s)
        else:
            dedup_stops[-1] = s # keep latest time (dep time)
            
    unwrapped_new = dedup_stops
    if len(unwrapped_new) < 2: return

    if t_num not in all_trains_map:
        all_trains_map[t_num] = {
            'train_number': t_num,
            'train_type': t_type,
            'train_model': t_model,
            'is_trpass': is_tr,
            'origin': unwrapped_new[0]['station'],
            'dest': unwrapped_new[-1]['station'],
            'line': line,
            'route_dir': route_dir,
            'unwrapped_stops': unwrapped_new,
            'stops': [{'station': s['station'], 'time': s['time']} for s in unwrapped_new]
        }
    else:
        existing = all_trains_map[t_num]
        if route_dir and not existing.get('route_dir'):
            existing['route_dir'] = route_dir
        if t_type and t_type != '區間車':
            existing['train_type'] = t_type
            existing['train_model'] = t_model
            existing['is_trpass'] = is_tr

        merged_map = {}
        for s in existing['unwrapped_stops']:
            merged_map[s['station']] = s
            
        for s in unwrapped_new:
            st = s['station']
            if st not in merged_map:
                merged_map[st] = s
            else:
                merged_map[st] = s
                
        all_merged = sorted(list(merged_map.values()), key=lambda x: x['abs_min'])
        
        # Deduplicate consecutive identical stations in merged list
        dedup_merged = []
        for s in all_merged:
            if not dedup_merged or dedup_merged[-1]['station'] != s['station']:
                dedup_merged.append(s)
            else:
                dedup_merged[-1] = s
                
        existing['unwrapped_stops'] = dedup_merged
        existing['stops'] = [{'station': s['station'], 'time': s['time']} for s in dedup_merged]
        existing['origin'] = dedup_merged[0]['station']
        existing['dest'] = dedup_merged[-1]['station']
        if line and '線' in line and (existing['line'] == '特快列車' or not existing['line']):
            existing['line'] = line

print("Building test full database...")
# (1) Branch lines
# Neiwan
path = os.path.join(folder, 'Neiwan20260701.ods')
if os.path.exists(path):
    df = pd.read_excel(path, engine='odf', header=None)
    down_cols = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    down_stations = ['新竹', '北新竹', '千甲', '新莊', '竹中', '六家', '上員', '榮華', '竹東', '橫山', '九讚頭', '合興', '富貴', '內灣']
    for r in range(4, min(68, len(df))):
        t_num = str(df.iloc[r, 2]).strip().replace('.0', '')
        if not t_num.isdigit(): continue
        stops = []
        for c_idx, st_name in zip(down_cols, down_stations):
            if c_idx < df.shape[1]:
                t_str = clean_time(df.iloc[r, c_idx])
                if t_str: stops.append({'station': st_name, 'time': t_str})
        add_or_merge_train(t_num, '區間車', 'DR1000/EMU', True, '內灣/六家線', stops)
        
    up_cols = [24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]
    up_stations = ['內灣', '富貴', '合興', '九讚頭', '橫山', '竹東', '榮華', '上員', '六家', '竹中', '新莊', '千甲', '北新竹', '新竹']
    for r in range(4, min(68, len(df))):
        t_num = str(df.iloc[r, 22]).strip().replace('.0', '') if df.shape[1] > 22 else ''
        if not t_num.isdigit(): continue
        stops = []
        for c_idx, st_name in zip(up_cols, up_stations):
            if c_idx < df.shape[1]:
                t_str = clean_time(df.iloc[r, c_idx])
                if t_str: stops.append({'station': st_name, 'time': t_str})
        add_or_merge_train(t_num, '區間車', 'DR1000/EMU', True, '內灣/六家線', stops)

# Pingxi
path = os.path.join(folder, 'PingxiToShenao20260701.ods')
if os.path.exists(path):
    df = pd.read_excel(path, engine='odf', header=None)
    down_cols = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    down_stations = ['八堵', '暖暖', '四腳亭', '八斗子', '海科館', '瑞芳', '猴硐', '三貂嶺', '大華', '十分', '望古', '嶺腳', '平溪', '菁桐']
    for r in range(4, min(45, len(df))):
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
        add_or_merge_train(t_num, '區間車', 'DR1000柴油客車', True, '平溪/深澳線', stops)
        
    up_cols = [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
    up_stations = ['菁桐', '平溪', '嶺腳', '望古', '十分', '大華', '三貂嶺', '猴硐', '瑞芳', '海科館', '八斗子', '四腳亭', '暖暖', '八堵']
    for r in range(4, min(45, len(df))):
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
        add_or_merge_train(t_num, '區間車', 'DR1000柴油客車', True, '平溪/深澳線', stops)

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
        add_or_merge_train(t_num, '區間車', 'DR1000柴油客車', True, '集集線', stops)
        
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
        add_or_merge_train(t_num, '區間車', 'DR1000柴油客車', True, '集集線', stops)

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
        add_or_merge_train(t_num, '區間車', 'EMU系列', True, '沙崙線', stops)
        
    shalun_up_sts = ['沙崙', '長榮大學', '中洲', '仁德', '保安', '台南', '大橋', '永康', '新市', '南科', '善化']
    for r in range(3, len(df)):
        t_num = str(df.iloc[r, 18]).strip().replace('.0', '') if df.shape[1] > 18 else ''
        if not t_num.isdigit(): continue
        stops = []
        for c_idx, st_name in enumerate(shalun_up_sts, start=20):
            if c_idx < df.shape[1]:
                t_str = clean_time(df.iloc[r, c_idx])
                if t_str: stops.append({'station': st_name, 'time': t_str})
        add_or_merge_train(t_num, '區間車', 'EMU系列', True, '沙崙線', stops)

# (2) Commuter files
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
        for c in range(1, 6):
            nums = [str(df.iloc[r, c]).strip().replace('.0', '') for r in range(3, min(15, len(df))) if pd.notna(df.iloc[r, c])]
            if len(nums) >= 3 and all(n.isdigit() for n in nums):
                t_col = c
                break
                
        col_to_station = {}
        for c in range(t_col + 1, len(df.columns)):
            chars = []
            for r in [1, 2, 3]:
                if r < len(df) and pd.notna(df.iloc[r, c]):
                    val = str(df.iloc[r, c]).strip().replace('\u3000', '').replace(' ', '')
                    if val and val not in ['站名', '名間', '起訖站', '備註']:
                        chars.append(val)
            raw_st = ''.join(chars)
            st = normalize_station(raw_st)
            
            if st and len(st) <= 8 and not st.startswith('名間') and not st.startswith('起訖') and st != '山':
                col_to_station[c] = st
                
        for r in range(3, len(df)):
            t_num = str(df.iloc[r, t_col]).strip().replace('.0', '')
            if not t_num.isdigit(): continue
            
            raw_type = str(df.iloc[r, max(0, t_col - 1)]).strip()
            raw_note = str(df.iloc[r, max(0, t_col - 2)]).strip()
            t_type, t_model, is_tr = extract_type_and_model(raw_type, raw_note)
            
            stops = []
            for c_idx, st_name in sorted(col_to_station.items()):
                t_str = clean_time(df.iloc[r, c_idx])
                if t_str:
                    stops.append({'station': st_name, 'time': t_str})
                    
            r_dir = '山線' if '山線' in line_name else ''
            add_or_merge_train(t_num, t_type, t_model, is_tr, line_name, stops, r_dir)
    except Exception as e:
        print(f'Error parsing commuter {fname}: {e}')

# (3) Western Trunk Express with Split Mountain/Sea stations
for fname in ['KeelungToChaozhou20260701.ods', 'ChaozhouToKeelung20260701.ods']:
    path = os.path.join(folder, fname)
    if not os.path.exists(path): continue
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
                
        line_desc = f"西部幹線 ({r_dir})" if r_dir else "西部幹線"
        add_or_merge_train(t_num, t_type, t_model, is_tr, line_desc, stops, r_dir)

# (4) Eastern Trunk and South Link Express
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
                    
            add_or_merge_train(t_num, t_type, t_model, is_tr, line_name, stops)
    except Exception as e:
        print(f'Error parsing {fname}: {e}')

# Determine route_dir for all trains based on stations if not explicitly tagged
mountain_unique = set(['造橋', '豐富', '苗栗', '南勢', '銅鑼', '三義', '泰安', '后里', '豐原', '栗林', '潭子', '頭家厝', '松竹', '太原', '精武', '台中', '五權', '大慶', '烏日', '新烏日', '成功'])
sea_unique = set(['談文', '大山', '後龍', '龍港', '白沙屯', '新埔', '通霄', '苑裡', '日南', '大甲', '台中港', '清水', '沙鹿', '龍井', '大肚', '追分'])

final_list = []
for t_num, t_data in all_trains_map.items():
    stops = t_data['stops']
    st_names = [s['station'] for s in stops]
    m_count = sum(1 for s in st_names if s in mountain_unique)
    s_count = sum(1 for s in st_names if s in sea_unique)
    
    if m_count > 0 and s_count > 0:
        t_data['route_dir'] = '成追線'
    elif m_count > 0:
        t_data['route_dir'] = '山線'
    elif s_count > 0:
        t_data['route_dir'] = '海線'
    elif not t_data.get('route_dir'):
        # Check if train runs across Zhunan and Changhua without stopping
        t_data['route_dir'] = ''

    del t_data['unwrapped_stops']
    final_list.append(t_data)

final_list.sort(key=lambda x: int(x['train_number']) if x['train_number'].isdigit() else 99999)

print(f"Total Trains Rebuilt: {len(final_list)}")
mt_trains = [t for t in final_list if t.get('route_dir') == '山線']
sea_trains = [t for t in final_list if t.get('route_dir') == '海線']
cz_trains = [t for t in final_list if t.get('route_dir') == '成追線']
print(f"Mountain line trains: {len(mt_trains)}, Sea line trains: {len(sea_trains)}, Cheng-Zhui: {len(cz_trains)}")

# Sample check
for num in ['101', '102', '103', '105', '112', '116', '130', '152', '278', '280', '501', '511', '2114', '2601']:
    t = next((x for x in final_list if x['train_number'] == num), None)
    if t:
        sts = [s['station'] for s in t['stops']]
        print(f"Train {num} ({t['train_type']} / [{t['route_dir']}]): {t['origin']} -> {t['dest']} ({len(sts)} stops) -> {sts}")
