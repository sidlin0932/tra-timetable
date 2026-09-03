import sys, os, glob, re, json
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
folder = os.path.join(BASE_DIR, 'data', 'raw_ods')

def normalize_station(st):
    if not st or pd.isna(st): return ''
    s = str(st).replace('臺', '台').strip()
    s = re.sub(r'[\d:\-－\s\u3000]+', '', s)
    station_clean_map = {
        '鳳': '鳳山', '松': '松山', '佳': '山佳', '冬': '冬山', '岡': '岡山',
        '屏': '屏東', '潮': '潮州', '枋': '枋寮', '竹': '新竹', '義': '嘉義',
        '南': '南港', '新城': '新城(太魯閣)', '新城太魯閣': '新城(太魯閣)'
    }
    s = station_clean_map.get(s, s)
    if re.search(r'[A-Za-z]', s): return ''
    if s in ['nan', '站名', '起訖站', '備註', '註：', '車次']: return ''
    return s

def clean_time(val):
    if pd.isna(val): return None
    s = str(val).strip()
    if s.endswith('.0'): s = s[:-2]
    match = re.search(r'(\d{1,2}):(\d{2})', s)
    if match:
        h, m = int(match.group(1)), int(match.group(2))
        return f"{h:02d}:{m:02d}"
    return None

def timeToMin(tStr):
    if not tStr: return 0
    h, m = map(int, tStr.split(':'))
    return h * 60 + m

def extract_type_and_model(raw_type, raw_note):
    s = f"{raw_type} {raw_note}".strip()
    if "3000" in s or "EMU3000" in s or "自強3000" in s:
        return "新自強(EMU3000)", "EMU3000", False
    elif "普悠瑪" in s:
        return "普悠瑪", "普悠瑪", False
    elif "太魯閣" in s:
        return "太魯閣", "太魯閣", False
    elif "自強" in s or "T.C." in s:
        return "自強號", "PP自強號/柴聯自強", True
    elif "莒光" in s or "C.K." in s:
        return "莒光號", "莒光號客車", True
    elif "區間快" in s or "Fast" in s:
        return "區間快", "EMU900/EMU800", True
    else:
        return "區間車", "EMU系列", True

all_trains_map = {}

def add_or_merge_train(t_num, t_type, t_model, is_tr, line, stops, route_dir=''):
    stops = [s for s in stops if s['station'] and s['time']]
    if len(stops) < 2: return
    
    # deduplicate consecutive identical stations
    dedup = []
    for s in stops:
        if not dedup or dedup[-1]['station'] != s['station']:
            dedup.append(s)
        else:
            dedup[-1] = s
    if len(dedup) < 2: return
    
    if t_num not in all_trains_map:
        all_trains_map[t_num] = {
            'train_number': t_num,
            'train_type': t_type,
            'train_model': t_model,
            'is_trpass': is_tr,
            'origin': dedup[0]['station'],
            'dest': dedup[-1]['station'],
            'line': line,
            'route_dir': route_dir,
            'stops': dedup
        }
    else:
        existing = all_trains_map[t_num]
        if route_dir and not existing.get('route_dir'):
            existing['route_dir'] = route_dir
        if t_type and t_type != '區間車':
            existing['train_type'] = t_type
            existing['train_model'] = t_model
            existing['is_trpass'] = is_tr
        
        # Merge stops if new list has more stops or covers more stations
        if len(dedup) > len(existing['stops']):
            existing['stops'] = dedup
            existing['origin'] = dedup[0]['station']
            existing['dest'] = dedup[-1]['station']

print("1. Parsing Western Mainline Express with Mountain/Sea split...")
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
            
    stations = []
    for r in range(t_row + 2, len(df)):
        c0 = normalize_station(df.iloc[r, 0])
        c4 = normalize_station(df.iloc[r, 4]) if df.shape[1] > 4 else ''
        if c4:
            stations.append({'row': r, 'sea': c0, 'mountain': c4, 'is_split': True})
        elif c0:
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
        is_mt = ('s' in marker or '山' in marker)
        is_sea = ('c' in marker or '海' in marker)
        r_dir = '山線' if is_mt else ('海線' if is_sea else '')
        
        stops = []
        for st in stations:
            t_str = clean_time(df.iloc[st['row'], c])
            if t_str:
                if st.get('is_split'):
                    st_name = st['mountain'] if is_mt else st['sea']
                else:
                    st_name = st['name']
                if st_name:
                    stops.append({'station': st_name, 'time': t_str})
                    
        add_or_merge_train(t_num, t_type, t_model, is_tr, '西部幹線', stops, r_dir)

print("2. Parsing Eastern Trunk & South Link Express...")
other_express = [
    ('ShulinToTaitung20260701.ods', '東部幹線'),
    ('TaitungToShulin20260701.ods', '東部幹線'),
    ('XinzuoyingToFangliaoToTaitung20260701.ods', '南迴線'),
    ('南迴線(台東→枋寮→新左營)-20260701.ods', '南迴線')
]
for fname, line_name in other_express:
    p = os.path.join(folder, fname)
    if not os.path.exists(p): continue
    df = pd.read_excel(p, engine='odf', header=None)
    t_row = 3
    for r in range(1, 6):
        nums = [str(df.iloc[r, c]).strip().replace('.0', '') for c in range(4, min(15, df.shape[1])) if pd.notna(df.iloc[r, c])]
        if len(nums) >= 3 and all(n.isdigit() for n in nums):
            t_row = r
            break
            
    stations = []
    for r in range(t_row + 2, len(df)):
        c0 = normalize_station(df.iloc[r, 0])
        if c0:
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
            if t_str and st['name']:
                stops.append({'station': st['name'], 'time': t_str})
        add_or_merge_train(t_num, t_type, t_model, is_tr, line_name, stops)

print("3. Parsing Tourist Branches (JIJI, Neiwan, Pingxi, Shalun)...")
# JIJI
df_jiji = pd.read_excel(os.path.join(folder, 'JIJI20260701.ods'), engine='odf', header=None)
jiji_down = ['二水', '源泉', '濁水', '龍泉', '集集', '水里', '車埕']
jiji_up = ['車埕', '水里', '集集', '龍泉', '濁水', '源泉', '二水']
for r in range(3, len(df_jiji)):
    t_num = str(df_jiji.iloc[r, 2]).strip().replace('.0', '')
    if t_num.isdigit():
        stops = []
        for idx, st in enumerate(jiji_down):
            c_idx = 4 + idx
            if c_idx < df_jiji.shape[1]:
                t_str = clean_time(df_jiji.iloc[r, c_idx])
                if t_str: stops.append({'station': st, 'time': t_str})
        add_or_merge_train(t_num, '區間車', '柴油客車', True, '集集線', stops)
for r in range(3, len(df_jiji)):
    t_num = str(df_jiji.iloc[r, 14]).strip().replace('.0', '') if df_jiji.shape[1] > 14 else ''
    if t_num.isdigit():
        stops = []
        for idx, st in enumerate(jiji_up):
            c_idx = 16 + idx
            if c_idx < df_jiji.shape[1]:
                t_str = clean_time(df_jiji.iloc[r, c_idx])
                if t_str: stops.append({'station': st, 'time': t_str})
        add_or_merge_train(t_num, '區間車', '柴油客車', True, '集集線', stops)

# Neiwan
df_nw = pd.read_excel(os.path.join(folder, 'Neiwan20260701.ods'), engine='odf', header=None)
nw_down = ['新竹', '北新竹', '千甲', '新莊', '竹中', '六家', '上員', '榮華', '竹東', '橫山', '九讚頭', '合興', '富貴', '內灣']
nw_up = ['內灣', '富貴', '合興', '九讚頭', '橫山', '竹東', '榮華', '上員', '六家', '竹中', '新莊', '千甲', '北新竹', '新竹']
for r in range(4, 66):
    t_num = ''
    for c in [1, 2, 3]:
        v = str(df_nw.iloc[r, c]).strip().replace('.0', '')
        if v.isdigit() and len(v) >= 3: t_num = v; break
    if t_num:
        stops = []
        for idx, st in enumerate(nw_down):
            c_idx = 4 + idx
            if c_idx < df_nw.shape[1]:
                t_str = clean_time(df_nw.iloc[r, c_idx])
                if t_str: stops.append({'station': st, 'time': t_str})
        add_or_merge_train(t_num, '區間車', 'EMU系列', True, '內灣線', stops)
for r in range(71, len(df_nw)):
    t_num = ''
    for c in [1, 2, 3]:
        v = str(df_nw.iloc[r, c]).strip().replace('.0', '')
        if v.isdigit() and len(v) >= 3: t_num = v; break
    if t_num:
        stops = []
        for idx, st in enumerate(nw_up):
            c_idx = 4 + idx
            if c_idx < df_nw.shape[1]:
                t_str = clean_time(df_nw.iloc[r, c_idx])
                if t_str: stops.append({'station': st, 'time': t_str})
        add_or_merge_train(t_num, '區間車', 'EMU系列', True, '內灣線', stops)

# Pingxi
df_px = pd.read_excel(os.path.join(folder, 'PingxiToShenao20260701.ods'), engine='odf', header=None)
px_down = ['八斗子', '海科館', '瑞芳', '猴硐', '三貂嶺', '大華', '十分', '望古', '嶺腳', '平溪', '菁桐']
px_up = ['菁桐', '平溪', '嶺腳', '望古', '十分', '大華', '三貂嶺', '猴硐', '瑞芳', '海科館', '八斗子']
for r in range(4, len(df_px)):
    t_num = ''
    for c in [1, 2, 3]:
        v = str(df_px.iloc[r, c]).strip().replace('.0', '')
        if v.isdigit() and len(v) >= 3: t_num = v; break
    if t_num:
        stops = []
        for idx, st in enumerate(px_down):
            c_idx = 4 + idx
            if c_idx < df_px.shape[1]:
                t_str = clean_time(df_px.iloc[r, c_idx])
                if t_str: stops.append({'station': st, 'time': t_str})
        add_or_merge_train(t_num, '區間車', '柴油客車', True, '平溪/深澳線', stops)
for r in range(4, len(df_px)):
    t_num = str(df_px.iloc[r, 20]).strip().replace('.0', '') if df_px.shape[1] > 20 else ''
    if not t_num.isdigit() and df_px.shape[1] > 21:
        alt = str(df_px.iloc[r, 21]).strip().replace('.0', '')
        if alt.isdigit(): t_num = alt
    if t_num.isdigit():
        stops = []
        for idx, st in enumerate(px_up):
            c_idx = 22 + idx
            if c_idx < df_px.shape[1]:
                t_str = clean_time(df_px.iloc[r, c_idx])
                if t_str: stops.append({'station': st, 'time': t_str})
        add_or_merge_train(t_num, '區間車', '柴油客車', True, '平溪/深澳線', stops)

# Shalun
df_sl = pd.read_excel(os.path.join(folder, 'Shalun2026070.ods'), engine='odf', header=None)
sl_down = ['善化', '南科', '新市', '永康', '大橋', '台南', '保安', '仁德', '中洲', '長榮大學', '沙崙']
sl_up = ['沙崙', '長榮大學', '中洲', '仁德', '保安', '台南', '大橋', '永康', '新市', '南科', '善化']
for r in range(3, len(df_sl)):
    t_num = str(df_sl.iloc[r, 2]).strip().replace('.0', '')
    if t_num.isdigit():
        stops = []
        for idx, st in enumerate(sl_down):
            c_idx = 4 + idx
            if c_idx < df_sl.shape[1]:
                t_str = clean_time(df_sl.iloc[r, c_idx])
                if t_str: stops.append({'station': st, 'time': t_str})
        add_or_merge_train(t_num, '區間車', 'EMU系列', True, '沙崙線', stops)
for r in range(3, len(df_sl)):
    t_num = str(df_sl.iloc[r, 18]).strip().replace('.0', '') if df_sl.shape[1] > 18 else ''
    if t_num.isdigit():
        stops = []
        for idx, st in enumerate(sl_up):
            c_idx = 20 + idx
            if c_idx < df_sl.shape[1]:
                t_str = clean_time(df_sl.iloc[r, c_idx])
                if t_str: stops.append({'station': st, 'time': t_str})
        add_or_merge_train(t_num, '區間車', 'EMU系列', True, '沙崙線', stops)

print("4. Parsing Commuter Trains...")
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
    if not os.path.exists(p): continue
    xl = pd.ExcelFile(p, engine='odf')
    sheet = xl.sheet_names[sheet_idx] if sheet_idx < len(xl.sheet_names) else xl.sheet_names[0]
    df = xl.parse(sheet, header=None)
    for r in range(3, len(df)):
        t_num = ''
        for c in [1, 2, 3]:
            val = str(df.iloc[r, c]).strip().replace('.0', '')
            clean_num = re.sub(r'[^\d]', '', val)
            if clean_num.isdigit() and len(clean_num) >= 3:
                t_num = clean_num
                break
        if not t_num: continue
        t_type = str(df.iloc[r, 0]).strip()
        t_type, t_model, is_tr = extract_type_and_model(t_type, '')
        stops = []
        for idx, st in enumerate(station_list):
            c_idx = st_start_col + idx
            if c_idx < df.shape[1]:
                t_str = clean_time(df.iloc[r, c_idx])
                if t_str: stops.append({'station': st, 'time': t_str})
        add_or_merge_train(t_num, t_type, t_model, is_tr, line_name, stops)

# Determine route_dir for all trains based on actual stops
mountain_unique = set(['造橋', '豐富', '苗栗', '南勢', '銅鑼', '三義', '泰安', '后里', '豐原', '栗林', '潭子', '頭家厝', '松竹', '太原', '精武', '台中', '五權', '大慶', '烏日', '新烏日', '成功'])
sea_unique = set(['談文', '大山', '後龍', '龍港', '白沙屯', '新埔', '通霄', '苑裡', '日南', '大甲', '台中港', '清水', '沙鹿', '龍井', '大肚', '追分'])

final_list = []
for t_num, t_data in all_trains_map.items():
    st_names = [s['station'] for s in t_data['stops']]
    m_count = sum(1 for s in st_names if s in mountain_unique)
    s_count = sum(1 for s in st_names if s in sea_unique)
    
    if m_count > 0 and s_count > 0:
        t_data['route_dir'] = '成追線'
    elif m_count > 0:
        t_data['route_dir'] = '山線'
    elif s_count > 0:
        t_data['route_dir'] = '海線'
    final_list.append(t_data)

final_list.sort(key=lambda x: int(x['train_number']) if x['train_number'].isdigit() else 99999)

out_json = os.path.join(BASE_DIR, 'full_network_timetable.json')
out_js = os.path.join(BASE_DIR, 'data.js')

with open(out_json, 'w', encoding='utf-8') as f:
    json.dump(final_list, f, ensure_ascii=False, indent=2)

with open(out_js, 'w', encoding='utf-8') as f:
    f.write('window.EMBEDDED_TIMETABLE_DATA = ')
    json.dump(final_list, f, ensure_ascii=False)
    f.write(';\n')

print(f"Successfully rebuilt {len(final_list)} trains!")
print(f"Mountain line trains: {sum(1 for t in final_list if t.get('route_dir')=='山線')}")
print(f"Sea line trains: {sum(1 for t in final_list if t.get('route_dir')=='海線')}")
print(f"Updated {out_json} and {out_js}")
