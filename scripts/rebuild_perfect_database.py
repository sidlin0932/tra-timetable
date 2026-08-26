import os
import json
import pandas as pd
import re

folder = '.'

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
    '南': '南港', '新城': '新城(太魯閣)', '新城太魯閣': '新城(太魯閣)'
}

def normalize_station(st):
    st = st.replace('臺', '台').strip()
    st = re.sub(r'[\d:\-－\s]+', '', st)
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
    """
    Given a physically ordered list of stops from an ODS sheet,
    unwraps cross-midnight times so they are monotonically increasing.
    """
    if not stops: return []
    unwrapped = []
    current_day_offset = 0
    prev_min = -1
    
    for s in stops:
        st_name = normalize_station(s['station'])
        raw_m = t_min(s['time'])
        if prev_min != -1 and raw_m < (prev_min % 1440) and (prev_min % 1440) - raw_m > 360:
            # Crossed midnight! Add 1440 mins
            current_day_offset += 1440
        abs_min = current_day_offset + raw_m
        prev_min = abs_min
        unwrapped.append({
            'station': st_name,
            'time': s['time'],
            'abs_min': abs_min
        })
    return unwrapped

def add_or_merge_train(t_num, t_type, t_model, is_tr, line, stops):
    if len(stops) < 2: return
    unwrapped_new = unwrap_stops(stops)
    
    if t_num not in all_trains_map:
        all_trains_map[t_num] = {
            'train_number': t_num,
            'train_type': t_type,
            'train_model': t_model,
            'is_trpass': is_tr,
            'origin': unwrapped_new[0]['station'],
            'dest': unwrapped_new[-1]['station'],
            'line': line,
            'unwrapped_stops': unwrapped_new,
            'stops': [{'station': s['station'], 'time': s['time']} for s in unwrapped_new]
        }
    else:
        existing = all_trains_map[t_num]
        merged_map = {}
        for s in existing['unwrapped_stops']:
            merged_map[s['station']] = s
            
        for s in unwrapped_new:
            st = s['station']
            if st not in merged_map:
                merged_map[st] = s
            else:
                # keep more precise if needed
                merged_map[st] = s
                
        all_merged = sorted(list(merged_map.values()), key=lambda x: x['abs_min'])
        existing['unwrapped_stops'] = all_merged
        existing['stops'] = [{'station': s['station'], 'time': s['time']} for s in all_merged]
        existing['origin'] = all_merged[0]['station']
        existing['dest'] = all_merged[-1]['station']
        if line and '線' in line and existing['line'] == '特快列車':
            existing['line'] = line

# 1. Parse Branch Lines
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

# Pingxi & Shenao
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

# 2. Commuter Lines
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
                    
            add_or_merge_train(t_num, t_type, t_model, is_tr, line_name, stops)
    except Exception as e:
        print(f'Error parsing commuter {fname}: {e}')

# 3. Mainline Express Trains
ENG_TO_ZH = {
    'Keelung': '基隆', 'Sankeng': '三坑', 'Badu': '八堵', 'Qidu': '七堵', 'Baifu': '百福',
    'Wudu': '五堵', 'Xizhi': '汐止', 'Xike': '汐科', 'Nangang': '南港', 'Songshan': '松山',
    'Taipei': '台北', 'Wanhua': '萬華', 'Banqiao': '板橋', 'Fuzhou': '浮洲', 'Shulin': '樹林',
    'South Shulin': '南樹林', 'Shanjia': '山佳', 'Yingge': '鶯歌', 'Fengming': '鳳鳴', 'Taoyuan': '桃園',
    'Neili': '內壢', 'Zhongli': '中壢', 'Puxin': '埔心', 'Yangmei': '楊梅', 'Fugang': '富岡',
    'Xinfu': '新富', 'Beihu': '北湖', 'Hukou': '湖口', 'Xinfeng': '新豐', 'Zhubei': '竹北',
    'North Hsinchu': '北新竹', 'Hsinchu': '新竹', 'Sanxingqiao': '三姓橋', 'Xiangshan': '香山',
    'Qiding': '崎頂', 'Zhunan': '竹南', 'Zaoqiao': '造橋', 'Fengfu': '豐富', 'Miaoli': '苗栗',
    'Nanshi': '南勢', 'Tongluo': '銅鑼', 'Sanyi': '三義', 'Tai\'an': '泰安', 'Houli': '后里',
    'Fengyuan': '豐原', 'Lilin': '栗林', 'Tanzi': '潭子', 'Toujiacuo': '頭家厝', 'Songzhu': '松竹',
    'Taiyuan': '太原', 'Jingwu': '精武', 'Taichung': '台中', 'Wuquan': '五權', 'Daqing': '大慶',
    'Wuri': '烏日', 'Xinwuri': '新烏日', 'Chenggong': '成功', 'Changhua': '彰化',
    'Tanwen': '談文', 'Dashan': '大山', 'Houlong': '後龍', 'Longgang': '龍港', 'Baishatun': '白沙屯',
    'Xinpu': '新埔', 'Tongxiao': '通霄', 'Yuanli': '苑裡', 'Rinan': '日南', 'Dajia': '大甲',
    'Taichung Port': '台中港', 'Qingshui': '清水', 'Shalu': '沙鹿', 'Longjing': '龍井', 'Dadu': '大肚', 'Zhuifen': '追分',
    'Huatan': '花壇', 'Dacun': '大村', 'Yuanlin': '員林', 'Yongjing': '永靖', 'Shetou': '社頭', 'Tianzhong': '田中',
    'Ershui': '二水', 'Linnei': '林內', 'Shiliu': '石榴', 'Douliu': '斗六', 'Dounan': '斗南', 'Shigui': '石龜',
    'Dalin': '大林', 'Minxiong': '民雄', 'Jiabei': '嘉北', 'Chiayi': '嘉義', 'Shuishang': '水上', 'Nanjing': '南靖',
    'Houbi': '後壁', 'Xinying': '新營', 'Liuying': '柳營', 'Linfengying': '林鳳營', 'Longtian': '隆田', 'Balin': '拔林',
    'Shanhua': '善化', 'Nanke': '南科', 'Xinshi': '新市', 'Yongkang': '永康', 'Daqiao': '大橋', 'Tainan': '台南',
    'Bao\'an': '保安', 'Rende': '仁德', 'Zhongzhou': '中洲', 'Dahu': '大湖', 'Luzhu': '路竹', 'Gangshan': '岡山',
    'Qiaotou': '橋頭', 'Nanzi': '楠梓', 'Xinzuoying': '新左營', 'Zuoying': '左營', 'Neiwei': '內惟',
    'Museum of Fine Arts': '美術館', 'Gushan': '鼓山', 'Sankuaiquo': '三塊厝', 'Kaohsiung': '高雄',
    'Minzu': '民族', 'Science and Technology Museum': '科工館', 'Zhengyi': '正義', 'Fengshan': '鳳山',
    'Houzhuang': '後庄', 'Jiuqutang': '九曲堂', 'Liukuaicuo': '六塊厝', 'Pingtung': '屏東', 'Guilai': '歸來',
    'Linluo': '麟洛', 'Xishi': '西勢', 'Zhutian': '竹田', 'Chaozhou': '潮州', 'Kanding': '崁頂', 'Nanzhou': '南州',
    'Zhen\'an': '鎮安', 'Linbian': '林邊', 'Jiadong': '佳冬', 'Donghai': '東海', 'Fangliao': '枋寮',
    'Jialu': '加祿', 'Neishi': '內獅', 'Fangshan': '枋山', 'Dawu': '大武', 'Longxi': '瀧溪', 'Jinlun': '金崙',
    'Taimali': '太麻里', 'Zhiben': '知本', 'Kangle': '康樂', 'Taitung': '台東',
    'Suao': '蘇澳', 'Suaoxin': '蘇澳新', 'Xinma': '新馬', 'Dongshan': '冬山', 'Luodong': '羅東',
    'Zhongli_Yilan': '中里', 'Erjie': '二結', 'Yilan': '宜蘭', 'Sicheng': '四城', 'Jiaoxi': '礁溪',
    'Dingpu': '頂埔', 'Toucheng': '頭城', 'Wai\'ao': '外澳', 'Guishan': '龜山', 'Daxi': '大溪',
    'Dali': '大里', 'Shicheng': '石城', 'Fulong': '福隆', 'Gongliao': '貢寮', 'Shuangxi': '雙溪',
    'Mudan': '牡丹', 'Sandiaoling': '三貂嶺', 'Houtong': '猴硐', 'Ruifang': '瑞芳', 'Sijiaoting': '四腳亭',
    'Nuannuan': '暖暖', 'Yongle': '永樂', 'Dong\'ao': '東澳', 'Nan\'ao': '南澳', 'Wuta': '武塔',
    'Hanben': '漢本', 'Heping': '和平', 'Heren': '和仁', 'Chongde': '崇德', 'Xincheng': '新城(太魯閣)',
    'Jingmei': '景美', 'Beipu': '北埔', 'Hualien': '花蓮', 'Ji\'an': '吉安', 'Zhixue': '志學',
    'Pinghe': '平和', 'Shoufeng': '壽豐', 'Fengtian': '豐田', 'Linrong Shin Kong': '林榮新光',
    'Nanping': '南平', 'Fenglin': '鳳林', 'Wanrong': '萬榮', 'Guangfu': '光復', 'Dafu': '大富',
    'Fuyuan': '富源', 'Ruisui': '瑞穗', 'Sanmin': '三民', 'Yuli': '玉里', 'Dongli': '東里',
    'Dongzhu': '東竹', 'Fuli': '富里', 'Chishang': '池上', 'Haiduan': '海端', 'Guanshan': '關山',
    'Yuemei': '月美', 'Ruihe': '瑞和', 'Ruiyuan': '瑞源', 'Luye': '鹿野', 'Shanli': '山里'
}

express_files = [
    'KeelungToChaozhou20260701.ods',
    'ChaozhouToKeelung20260701.ods',
    'ShulinToTaitung20260701.ods',
    'TaitungToShulin20260701.ods',
    'XinzuoyingToFangliaoToTaitung20260701.ods',
    '南迴線(台東→枋寮→新左營)-20260701.ods'
]

for fname in express_files:
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
        is_parallel = 'Keelung' in fname or 'Chaozhou' in fname
        
        for r in range(t_row + 2, len(df)):
            eng_name_1 = str(df.iloc[r, 1]).strip() if df.shape[1] > 1 else ''
            eng_name_0 = str(df.iloc[r, 0]).strip()
            
            zh_name = ENG_TO_ZH.get(eng_name_1, ENG_TO_ZH.get(eng_name_0, ''))
            
            zh_name_mt = zh_name
            if is_parallel and df.shape[1] > 3:
                eng_name_mt = str(df.iloc[r, 3]).strip() if df.shape[1] > 3 else ''
                if eng_name_mt in ENG_TO_ZH:
                    zh_name_mt = ENG_TO_ZH[eng_name_mt]
                    
            if zh_name or zh_name_mt:
                if not zh_name: zh_name = zh_name_mt
                stations.append({'row': r, 'name': normalize_station(zh_name), 'name_mt': normalize_station(zh_name_mt)})
                
        type_row = max(0, t_row - 1)
        model_row = max(0, t_row - 2)
        
        for c in range(4, df.shape[1]):
            t_num = str(df.iloc[t_row, c]).strip().replace('.0', '')
            if not t_num.isdigit(): continue
            
            raw_type = str(df.iloc[type_row, c]).strip()
            raw_model = str(df.iloc[model_row, c]).strip()
            t_type, t_model, is_tr = extract_type_and_model(raw_type, raw_model)
            
            is_mountain = False
            if is_parallel and t_row + 1 < len(df):
                marker = str(df.iloc[t_row + 1, c]).strip()
                is_mountain = ('s' in marker or '山' in marker)
                
            stops = []
            for st_info in stations:
                r = st_info['row']
                st_name = st_info['name_mt'] if is_mountain and st_info['name_mt'] else st_info['name']
                t_str = clean_time(df.iloc[r, c])
                if t_str:
                    stops.append({'station': st_name, 'time': t_str})
                    
            add_or_merge_train(t_num, t_type, t_model, is_tr, '特快列車', stops)
    except Exception as e:
        print(f'Error parsing express {fname}: {e}')

final_trains = []
for t in all_trains_map.values():
    clean_stops = []
    seen_st = set()
    for s in t['stops']:
        st_clean = normalize_station(s['station'])
        if st_clean not in seen_st:
            seen_st.add(st_clean)
            clean_stops.append({'station': st_clean, 'time': s['time']})
            
    final_trains.append({
        'train_number': t['train_number'],
        'train_type': t['train_type'],
        'train_model': t['train_model'],
        'is_trpass': t['is_trpass'],
        'origin': clean_stops[0]['station'],
        'dest': clean_stops[-1]['station'],
        'line': t['line'],
        'stops': clean_stops
    })

final_trains.sort(key=lambda x: x['train_number'])

print(f"Master Database Rebuilt with Cross-Midnight support & Perfect Normalization! Total: {len(final_trains)} trains.")

with open('full_network_timetable.json', 'w', encoding='utf-8') as f:
    json.dump(final_trains, f, ensure_ascii=False, indent=2)

with open('data.js', 'w', encoding='utf-8') as f:
    f.write('window.EMBEDDED_TIMETABLE_DATA = ' + json.dumps(final_trains, ensure_ascii=False) + ';')

print("Written perfect data.js and full_network_timetable.json!")
