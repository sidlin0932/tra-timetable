import os
import re
import glob
import pandas as pd
import json

folder = 'f:/Antigravity/台鐵時刻表0701'

def time_to_min(time_str):
    if not time_str or ':' not in time_str: return -1
    try:
        parts = time_str.split(':')
        h, m = int(parts[0]), int(parts[1])
        return h * 60 + m
    except:
        return -1

def clean_time(val):
    if pd.isna(val): return ''
    s = str(val).strip()
    # Check if time format HH:MM
    match = re.search(r'(\d{1,2}):(\d{2})', s)
    if match:
        h = int(match.group(1))
        m = int(match.group(2))
        return f"{h:02d}:{m:02d}"
    return ''

def extract_type_and_model(raw_str, fallback_str=''):
    raw = str(raw_str).strip()
    fallback = str(fallback_str).strip()
    combined = raw + ' ' + fallback
    
    t_type = '區間車'
    t_model = 'EMU系列'
    
    if '3000' in combined:
        t_type = '自強(3000)'
        t_model = 'EMU3000'
    elif '普悠瑪' in combined or 'TEMU2000' in combined:
        t_type = '普悠瑪'
        t_model = '普悠瑪 (TEMU2000)'
    elif '太魯閣' in combined or 'TEMU1000' in combined:
        t_type = '太魯閣'
        t_model = '太魯閣 (TEMU1000)'
    elif '自強' in combined or 'T.C.' in combined:
        t_type = '自強'
        t_model = 'PP自強號'
    elif '莒光' in combined or 'C.K.' in combined:
        t_type = '莒光'
        t_model = '莒光號'
    elif '區間快' in combined or '快' in combined or 'Fast' in combined:
        t_type = '區間快'
        t_model = 'EMU900/EMU800'
    elif '區間' in combined or 'Local' in combined:
        t_type = '區間車'
        t_model = 'EMU系列'
        
    return t_type, t_model

# Known Station Lists for Branch Lines & Specific Line Sections
STATION_MAPS = {
    'Neiwan_down': ['新竹', '北新竹', '千甲', '新莊', '竹中', '六家', '上員', '榮華', '竹東', '橫山', '九讚頭', '合興', '富貴', '內灣'],
    'Neiwan_up': ['內灣', '富貴', '合興', '九讚頭', '橫山', '竹東', '榮華', '上員', '六家', '竹中', '新莊', '千甲', '北新竹', '新竹'],
    
    'Pingxi_down': ['八堵', '暖暖', '四腳亭', '海科館', '八斗子', '瑞芳', '猴硐', '三貂嶺', '大華', '十分', '望古', '嶺腳', '平溪', '菁桐'],
    'Pingxi_up': ['菁桐', '平溪', '嶺腳', '望古', '十分', '大華', '三貂嶺', '猴硐', '瑞芳', '八斗子', '海科館', '四腳亭', '暖暖', '八堵'],
    
    'Jiji_down': ['二水', '源泉', '濁水', '龍泉', '集集', '水里', '車埕'],
    'Jiji_up': ['車埕', '水里', '集集', '龍泉', '濁水', '源泉', '二水'],
    
    'Shalun_down': ['善化', '南科', '新市', '永康', '大橋', '台南', '保安', '仁德', '中洲', '長榮大學', '沙崙'],
    'Shalun_up': ['沙崙', '長榮大學', '中洲', '仁德', '保安', '台南', '大橋', '永康', '新市', '南科', '善化'],
    
    'NorthLink_down': ['蘇澳新', '永樂', '東澳', '南澳', '武塔', '漢本', '和平', '和仁', '崇德', '新城', '景美', '北埔', '花蓮'],
    'NorthLink_up': ['花蓮', '北埔', '景美', '新城', '崇德', '和仁', '和平', '漢本', '武塔', '南澳', '東澳', '永樂', '蘇澳新'],
    
    'TaitungLine_down': ['花蓮', '吉安', '志學', '平和', '壽豐', '豐田', '林榮新光', '南平', '鳳林', '萬榮', '光復', '大富', '富源', '瑞穗', '三民', '玉里', '東里', '東竹', '富里', '池上', '海端', '關山', '月美', '瑞和', '瑞源', '鹿野', '山里', '台東'],
    'TaitungLine_up': ['台東', '山里', '鹿野', '瑞源', '瑞和', '月美', '關山', '海端', '池上', '富里', '東竹', '東里', '玉里', '三民', '瑞穗', '富源', '大富', '光復', '萬榮', '鳳林', '南平', '林榮新光', '豐田', '壽豐', '平和', '志學', '吉安', '花蓮'],
    
    'HsinchuToKeelung': ['新竹', '北新竹', '竹北', '新豐', '湖口', '北湖', '新富', '富岡', '楊梅', '埔心', '中壢', '內壢', '桃園', '鶯歌', '山佳', '南樹林', '樹林', '浮洲', '板橋', '萬華', '台北', '松山', '南港', '汐科', '汐止', '五堵', '百福', '七堵', '八堵', '三坑', '基隆'],
    'KeelungToHsinchu': ['基隆', '三坑', '八堵', '七堵', '百福', '五堵', '汐止', '汐科', '南港', '松山', '台北', '萬華', '板橋', '浮洲', '樹林', '南樹林', '山佳', '鶯歌', '桃園', '內壢', '中壢', '埔心', '楊梅', '富岡', '新富', '北湖', '湖口', '新豐', '竹北', '北新竹', '新竹'],
    
    'HsinchuToChanghua_Mountain': ['新竹', '三姓橋', '香山', '崎頂', '竹南', '造橋', '豐富', '苗栗', '南勢', '銅鑼', '三義', '泰安', '后里', '豐原', '栗林', '潭子', '頭家厝', '松竹', '太原', '精武', '台中', '五權', '大慶', '烏日', '新烏日', '成功', '彰化'],
    'ChanghuaToHsinchu_Mountain': ['彰化', '成功', '新烏日', '烏日', '大慶', '五權', '台中', '精武', '太原', '松竹', '頭家厝', '潭子', '栗林', '豐原', '后里', '泰安', '三義', '銅鑼', '南勢', '苗栗', '豐富', '造橋', '竹南', '崎頂', '香山', '三姓橋', '新竹'],
    
    'ChanghuaToChiayi': ['彰化', '花壇', '大村', '員林', '永靖', '社頭', '田中', '二水', '林內', '石榴', '斗六', '斗南', '石龜', '大林', '民雄', '嘉北', '嘉義'],
    'ChiayiToChanghua': ['嘉義', '嘉北', '民雄', '大林', '石龜', '斗南', '斗六', '石榴', '林內', '二水', '田中', '社頭', '永靖', '員林', '大村', '花壇', '彰化'],
    
    'ChiayiToKaohsiung': ['嘉義', '水上', '南靖', '後壁', '新營', '柳營', '林鳳營', '隆田', '拔林', '善化', '南科', '新市', '永康', '大橋', '台南', '保安', '仁德', '中洲', '大湖', '路竹', '岡山', '橋頭', '楠梓', '新左營', '左營', '內惟', '美術館', '鼓山', '三塊厝', '高雄'],
    'KaohsiungToChiayi': ['高雄', '三塊厝', '鼓山', '美術館', '內惟', '左營', '新左營', '楠梓', '橋頭', '岡山', '路竹', '大湖', '中洲', '仁德', '保安', '台南', '大橋', '永康', '新市', '南科', '善化', '拔林', '隆田', '林鳳營', '柳營', '新營', '後壁', '南靖', '水上', '嘉義'],
    
    'XinzuoyingToFangliao': ['新左營', '左營', '內惟', '美術館', '鼓山', '三塊厝', '高雄', '民族', '科工館', '正義', '鳳山', '後庄', '九曲堂', '六塊厝', '屏東', '歸來', '麟洛', '西勢', '竹田', '潮州', '崁頂', '南州', '鎮安', '林邊', '佳冬', '東海', '枋寮'],
    'FangliaoToXinzuoying': ['枋寮', '東海', '佳冬', '林邊', '鎮安', '南州', '崁頂', '潮州', '竹田', '西勢', '麟洛', '歸來', '屏東', '六塊厝', '九曲堂', '後庄', '鳳山', '正義', '科工館', '民族', '高雄', '三塊厝', '鼓山', '美術館', '內惟', '左營', '新左營'],
    
    'BaduToSuao': ['八堵', '暖暖', '四腳亭', '瑞芳', '猴硐', '三貂嶺', '牡丹', '雙溪', '貢寮', '福隆', '石城', '大里', '大溪', '龜山', '外澳', '頭城', '頂埔', '礁溪', '四城', '宜蘭', '二結', '中里', '羅東', '冬山', '新馬', '蘇澳新', '蘇澳'],
    'SuaoToBadu': ['蘇澳', '蘇澳新', '新馬', '冬山', '羅東', '中里', '二結', '宜蘭', '四城', '礁溪', '頂埔', '頭城', '外澳', '龜山', '大溪', '大里', '石城', '福隆', '貢寮', '雙溪', '牡丹', '三貂嶺', '猴硐', '瑞芳', '四腳亭', '暖暖', '八堵']
}

all_trains = []

def parse_branch_lines():
    # 1. Neiwan Line
    path = os.path.join(folder, 'Neiwan20260701.ods')
    if os.path.exists(path):
        df = pd.read_excel(path, engine='odf', header=None)
        # Down trains (新竹/竹中 -> 內灣/六家)
        # Col 4..17: 新竹, 北新竹, 千甲, 新莊, 竹中, 六家, 上員, 榮華, 竹東, 橫山, 九讚頭, 合興, 富貴, 內灣
        down_cols = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        down_stations = ['新竹', '北新竹', '千甲', '新莊', '竹中', '六家', '上員', '榮華', '竹東', '橫山', '九讚頭', '合興', '富貴', '內灣']
        for r in range(4, 68):
            t_num = str(df.iloc[r, 2]).strip().replace('.0', '')
            if not t_num.isdigit(): continue
            t_type = '區間車'
            stops = []
            for c_idx, st_name in zip(down_cols, down_stations):
                if c_idx < df.shape[1]:
                    t_str = clean_time(df.iloc[r, c_idx])
                    if t_str:
                        stops.append({'station': st_name, 'time': t_str})
            if len(stops) >= 2:
                all_trains.append({
                    'train_number': t_num,
                    'train_type': t_type,
                    'train_model': 'EMU/DRC',
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '內灣六家線',
                    'direction': '順行 (南下/東行)',
                    'stops': stops
                })
        # Up trains (內灣/六家 -> 新竹)
        # In rows 71..133
        up_cols = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        up_stations = ['內灣', '富貴', '合興', '九讚頭', '橫山', '竹東', '榮華', '上員', '六家', '竹中', '新莊', '千甲', '北新竹', '新竹']
        for r in range(70, len(df)):
            t_num = str(df.iloc[r, 2]).strip().replace('.0', '')
            if not t_num.isdigit(): continue
            t_type = '區間車'
            stops = []
            for c_idx, st_name in zip(up_cols, up_stations):
                if c_idx < df.shape[1]:
                    t_str = clean_time(df.iloc[r, c_idx])
                    if t_str:
                        stops.append({'station': st_name, 'time': t_str})
            if len(stops) >= 2:
                all_trains.append({
                    'train_number': t_num,
                    'train_type': t_type,
                    'train_model': 'EMU/DRC',
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '內灣六家線',
                    'direction': '逆行 (北上/西行)',
                    'stops': stops
                })
                
    # 2. Pingxi Line
    path = os.path.join(folder, 'PingxiToShenao20260701.ods')
    if os.path.exists(path):
        df = pd.read_excel(path, engine='odf', header=None)
        # Down: Cols 4..17
        down_cols = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        down_sts = ['八堵', '暖暖', '四腳亭', '海科館', '八斗子', '瑞芳', '猴硐', '三貂嶺', '大華', '十分', '望古', '嶺腳', '平溪', '菁桐']
        for r in range(4, len(df)):
            t_num = str(df.iloc[r, 2]).strip().replace('.0', '')
            if not t_num.isdigit(): continue
            stops = []
            for c_idx, st_name in zip(down_cols, down_sts):
                if c_idx < df.shape[1]:
                    t_str = clean_time(df.iloc[r, c_idx])
                    if t_str:
                        stops.append({'station': st_name, 'time': t_str})
            if len(stops) >= 2:
                all_trains.append({
                    'train_number': t_num,
                    'train_type': '區間車',
                    'train_model': 'DRC冷氣柴客',
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '平溪深澳線',
                    'direction': '順行 (往菁桐)',
                    'stops': stops
                })
        # Up: Cols 23..36
        up_cols = [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        up_sts = ['菁桐', '平溪', '嶺腳', '望古', '十分', '大華', '三貂嶺', '猴硐', '瑞芳', '八斗子', '海科館', '四腳亭', '暖暖', '八堵']
        for r in range(4, len(df)):
            t_num = str(df.iloc[r, 21]).strip().replace('.0', '') if df.shape[1] > 21 else ''
            if not t_num.isdigit():
                # check col 18, 19, 20
                for c_try in [18, 19, 20, 21, 22]:
                    if c_try < df.shape[1] and str(df.iloc[r, c_try]).strip().replace('.0', '').isdigit():
                        t_num = str(df.iloc[r, c_try]).strip().replace('.0', '')
                        break
            if not t_num.isdigit(): continue
            stops = []
            for c_idx, st_name in zip(up_cols, up_sts):
                if c_idx < df.shape[1]:
                    t_str = clean_time(df.iloc[r, c_idx])
                    if t_str:
                        stops.append({'station': st_name, 'time': t_str})
            if len(stops) >= 2:
                all_trains.append({
                    'train_number': t_num,
                    'train_type': '區間車',
                    'train_model': 'DRC冷氣柴客',
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '平溪深澳線',
                    'direction': '逆行 (往瑞芳/八堵/八斗子)',
                    'stops': stops
                })

    # 3. Jiji Line
    path = os.path.join(folder, 'JIJI20260701.ods')
    if os.path.exists(path):
        df = pd.read_excel(path, engine='odf', header=None)
        # Down: Cols 4..10
        jiji_down_sts = ['二水', '源泉', '濁水', '龍泉', '集集', '水里', '車埕']
        for r in range(3, len(df)):
            t_num = str(df.iloc[r, 2]).strip().replace('.0', '')
            if not t_num.isdigit(): continue
            stops = []
            for c_idx, st_name in enumerate(jiji_down_sts, start=4):
                if c_idx < df.shape[1]:
                    t_str = clean_time(df.iloc[r, c_idx])
                    if t_str:
                        stops.append({'station': st_name, 'time': t_str})
            if len(stops) >= 2:
                all_trains.append({
                    'train_number': t_num,
                    'train_type': '區間車',
                    'train_model': 'DRC冷氣柴客',
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '集集線',
                    'direction': '順行 (往車埕)',
                    'stops': stops
                })
        # Up: Cols 16..22
        jiji_up_sts = ['車埕', '水里', '集集', '龍泉', '濁水', '源泉', '二水']
        for r in range(3, len(df)):
            t_num = str(df.iloc[r, 14]).strip().replace('.0', '') if df.shape[1] > 14 else ''
            if not t_num.isdigit(): continue
            stops = []
            for c_idx, st_name in enumerate(jiji_up_sts, start=16):
                if c_idx < df.shape[1]:
                    t_str = clean_time(df.iloc[r, c_idx])
                    if t_str:
                        stops.append({'station': st_name, 'time': t_str})
            if len(stops) >= 2:
                all_trains.append({
                    'train_number': t_num,
                    'train_type': '區間車',
                    'train_model': 'DRC冷氣柴客',
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '集集線',
                    'direction': '逆行 (往二水/彰化)',
                    'stops': stops
                })

    # 4. Shalun Line
    path = os.path.join(folder, 'Shalun2026070.ods')
    if os.path.exists(path):
        df = pd.read_excel(path, engine='odf', header=None)
        # Down: Cols 4..14 (善化..沙崙)
        shalun_down_sts = ['善化', '南科', '新市', '永康', '大橋', '台南', '保安', '仁德', '中洲', '長榮大學', '沙崙']
        for r in range(3, len(df)):
            t_num = str(df.iloc[r, 2]).strip().replace('.0', '')
            if not t_num.isdigit(): continue
            stops = []
            for c_idx, st_name in enumerate(shalun_down_sts, start=4):
                if c_idx < df.shape[1]:
                    t_str = clean_time(df.iloc[r, c_idx])
                    if t_str:
                        stops.append({'station': st_name, 'time': t_str})
            if len(stops) >= 2:
                all_trains.append({
                    'train_number': t_num,
                    'train_type': '區間車',
                    'train_model': 'EMU系列',
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '沙崙線',
                    'direction': '順行 (往沙崙)',
                    'stops': stops
                })
        # Up: Cols 20..30 (沙崙..善化)
        shalun_up_sts = ['沙崙', '長榮大學', '中洲', '仁德', '保安', '台南', '大橋', '永康', '新市', '南科', '善化']
        for r in range(3, len(df)):
            t_num = str(df.iloc[r, 18]).strip().replace('.0', '') if df.shape[1] > 18 else ''
            if not t_num.isdigit(): continue
            stops = []
            for c_idx, st_name in enumerate(shalun_up_sts, start=20):
                if c_idx < df.shape[1]:
                    t_str = clean_time(df.iloc[r, c_idx])
                    if t_str:
                        stops.append({'station': st_name, 'time': t_str})
            if len(stops) >= 2:
                all_trains.append({
                    'train_number': t_num,
                    'train_type': '區間車',
                    'train_model': 'EMU系列',
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '沙崙線',
                    'direction': '逆行 (往台南/善化/嘉義)',
                    'stops': stops
                })

parse_branch_lines()
print(f'Branch lines loaded: {len(all_trains)} trains')
