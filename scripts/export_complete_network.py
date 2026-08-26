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
    match = re.search(r'(\d{1,2}):(\d{2})', s)
    if match:
        h = int(match.group(1))
        m = int(match.group(2))
        return f"{h:02d}:{m:02d}"
    return ''

ENG_TO_ZH = {
    'Keelung': '基隆', 'Badu': '八堵', 'Qidu': '七堵', 'Xizhi': '汐止', 'Nangang': '南港',
    'Songshan': '松山', 'Taipei': '台北', 'Wanhua': '萬華', 'Banqiao': '板橋', 'Shulin': '樹林',
    'Yingge': '鶯歌', 'Taoyuan': '桃園', 'Neili': '內壢', 'Zhongli': '中壢', 'Puxin': '埔心',
    'Yangmei': '楊梅', 'Fugang': '富岡', 'Xinfu': '新富', 'Beihu': '北湖', 'Hukou': '湖口',
    'Xinfeng': '新豐', 'Zhubei': '竹北', 'NorthHsinchu': '北新竹', 'Hsinchu': '新竹',
    'Sanxingqiao': '三姓橋', 'Xiangshan': '香山', 'Qiding': '崎頂', 'Zhunan': '竹南',
    'Zaociao': '造橋', 'Fengfu': '豐富', 'Miaoli': '苗栗', 'Nanshi': '南勢', 'Tongluo': '銅鑼',
    'Sanyi': '三義', 'Tai\'an': '泰安', 'Houli': '后里', 'Fengyuan': '豐原', 'Lilin': '栗林',
    'Tanzi': '潭子', 'Toujiacuo': '頭家厝', 'Songzhu': '松竹', 'Taiyuan': '太原', 'Jingwu': '精武',
    'Taichung': '台中', 'Wuquan': '五權', 'Daqing': '大慶', 'Wuri': '烏日', 'Xinwuri': '新烏日',
    'Chenggong': '成功', 'Changhua': '彰化',
    'Tanwen': '談文', 'Dashan': '大山', 'Houlong': '後龍', 'Longgang': '龍港', 'Baishatun': '白沙屯',
    'Xinpu': '新埔', 'Tongxiao': '通霄', 'Yuanli': '苑裡', 'Rinan': '日南', 'Dajia': '大甲',
    'TaichungPort': '台中港', 'Qingshui': '清水', 'Shalu': '沙鹿', 'Longjing': '龍井', 'Dadu': '大肚',
    'Zhuifen': '追分',
    'Huatan': '花壇', 'Dacun': '大村', 'Yuanlin': '員林', 'Yongjing': '永靖', 'Shetou': '社頭',
    'Tianzhong': '田中', 'Ershui': '二水', 'Linnei': '林內', 'Shiliu': '石榴', 'Douliu': '斗六',
    'Dounan': '斗南', 'Shigui': '石龜', 'Dalin': '大林', 'Minxiong': '民雄', 'Jiabei': '嘉北',
    'Chiayi': '嘉義', 'Shuishang': '水上', 'Nanjing': '南靖', 'Houbi': '後壁', 'Xinying': '新營',
    'Liuying': '柳營', 'Linfengying': '林鳳營', 'Longtian': '隆田', 'Balin': '拔林', 'Shanhua': '善化',
    'Nanke': '南科', 'Xinshi': '新市', 'Yongkang': '永康', 'Daqiao': '大橋', 'Tainan': '台南',
    'Bao\'an': '保安', 'Baoan': '保安', 'Rende': '仁德', 'Zhongzhou': '中洲', 'Dahu': '大湖',
    'Luzhu': '路竹', 'Gangshan': '岡山', 'Qiaotou': '橋頭', 'Nanzi': '楠梓', 'Xinzuoying': '新左營',
    'Zuoying': '左營', 'Neiwei': '內惟', 'FineArtsMuseum': '美術館', 'Gushan': '鼓山',
    'Sankuaihuo': '三塊厝', 'Sankuaicuo': '三塊厝', 'Kaohsiung': '高雄', 'Minzu': '民族',
    'ScienceMuseum': '科工館', 'Zhengyi': '正義', 'Fengshan': '鳳山', 'Houzhuang': '後庄',
    'Jiuqutang': '九曲堂', 'Liukuaicuo': '六塊厝', 'Pingtung': '屏東', 'Guilai': '歸來',
    'Linluo': '麟洛', 'Xishi': '西勢', 'Zhutian': '竹田', 'Chaozhou': '潮州', 'Kanding': '崁頂',
    'Nanzhou': '南州', 'Zhen\'an': '鎮安', 'Zhenan': '鎮安', 'Linbian': '林邊', 'Jiadong': '佳冬',
    'Donghai': '東海', 'Fangliao': '枋寮',
    'Jialu': '加祿', 'Neishi': '內獅', 'Fangshan': '枋山', 'Dawu': '大武', 'Longxi': '瀧溪',
    'Jinlun': '金崙', 'Taimali': '太麻里', 'Zhiben': '知本', 'Kangle': '康樂', 'Taitung': '台東',
    'Shanli': '山里', 'Luye': '鹿野', 'Ruiyuan': '瑞源', 'Ruihe': '瑞和', 'Guanshan': '關山',
    'Haiduan': '海端', 'Chishang': '池上', 'Fuli': '富里', 'Dongzhu': '東竹', 'Dongli': '東里',
    'Yuli': '玉里', 'Sanmin': '三民', 'Ruisui': '瑞穗', 'Fuyuan': '富源', 'Dafu': '大富',
    'Guangfu': '光復', 'Wanrong': '萬榮', 'Fenglin': '鳳林', 'Nanping': '南平',
    'LinrongShinKong': '林榮新光', 'Linrong Shin Kong': '林榮新光', 'Fengtian': '豐田',
    'Shoufeng': '壽豐', 'Pinghe': '平和', 'Zhixue': '志學', 'Ji\'an': '吉安', 'Jian': '吉安',
    'Hualien': '花蓮', 'Beipu': '北埔', 'Jingmei': '景美', 'Xincheng': '新城(太魯閣)',
    'Chongde': '崇德', 'Heren': '和仁', 'Heping': '和平', 'Hanben': '漢本', 'Wuta': '武塔',
    'Nan\'ao': '南澳', 'Nanao': '南澳', 'Dong\'ao': '東澳', 'Dongao': '東澳', 'Yongle': '永樂',
    'Su\'aoxin': '蘇澳新', 'Suaoxin': '蘇澳新', 'Su\'ao': '蘇澳', 'Suao': '蘇澳',
    'Dongshan': '冬山', 'Luodong': '羅東', 'Zhongli(Yilan)': '中里', 'Zhongli2': '中里', 'Erjie': '二結',
    'Yilan': '宜蘭', 'Sicheng': '四城', 'Jiaoxi': '礁溪', 'Dingpu': '頂埔', 'Toucheng': '頭城',
    'Wai\'ao': '外澳', 'Waiao': '外澳', 'Guishan': '龜山', 'Daxi': '大溪', 'Dali': '大里',
    'Shicheng': '石城', 'Fulong': '福隆', 'Gongliao': '貢寮', 'Shuangxi': '雙溪', 'Mudan': '牡丹',
    'Sandiaoling': '三貂嶺', 'Houtong': '猴硐', 'Ruifang': '瑞芳', 'Sijiaoting': '四腳亭', 'Nuannuan': '暖暖',
    'Dahua': '大華', 'Shifen': '十分', 'Wanggu': '望古', 'Lingjiao': '嶺腳', 'Pingxi': '平溪',
    'Jingtong': '菁桐', 'Haiguan': '海科館', 'Badouzi': '八斗子',
    'Qianjia': '千甲', 'Xinzhuang': '新莊', 'Zhuzhong': '竹中', 'Liujia': '六家', 'Shangyuan': '上員',
    'Ronghua': '榮華', 'Zhudong': '竹東', 'Hengshan': '橫山', 'Jiuzantou': '九讚頭', 'Hexing': '合興',
    'Fugui': '富貴', 'Neiwan': '內灣',
    'Yuanquan': '源泉', 'Zhuoshui': '濁水', 'Longquan': '龍泉', 'Jiji': '集集', 'Shuili': '水里', 'Checheng': '車埕',
    'ChangrongUniversity': '長榮大學', 'Chang Jung Christian University': '長榮大學', 'Shalun': '沙崙'
}

def extract_type_and_model(raw_str, fallback_str=''):
    raw = str(raw_str).strip()
    fallback = str(fallback_str).strip()
    combined = raw + ' ' + fallback
    
    t_type = '區間車'
    t_model = 'EMU系列'
    is_trpass = True
    
    if '3000' in combined or 'EMU3000' in combined:
        t_type = '自強(3000)'
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

# 1. Parse Branch lines
def parse_branches():
    # Neiwan
    path = os.path.join(folder, 'Neiwan20260701.ods')
    if os.path.exists(path):
        df = pd.read_excel(path, engine='odf', header=None)
        down_cols = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        down_stations = ['新竹', '北新竹', '千甲', '新莊', '竹中', '六家', '上員', '榮華', '竹東', '橫山', '九讚頭', '合興', '富貴', '內灣']
        for r in range(4, 68):
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
                    'train_model': 'EMU/DRC',
                    'is_trpass': True,
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '內灣六家線',
                    'stops': stops
                })
        up_cols = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        up_stations = ['內灣', '富貴', '合興', '九讚頭', '橫山', '竹東', '榮華', '上員', '六家', '竹中', '新莊', '千甲', '北新竹', '新竹']
        for r in range(70, len(df)):
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
                    'train_model': 'EMU/DRC',
                    'is_trpass': True,
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '內灣六家線',
                    'stops': stops
                })

    # Pingxi
    path = os.path.join(folder, 'PingxiToShenao20260701.ods')
    if os.path.exists(path):
        df = pd.read_excel(path, engine='odf', header=None)
        down_cols = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        down_sts = ['八堵', '暖暖', '四腳亭', '海科館', '八斗子', '瑞芳', '猴硐', '三貂嶺', '大華', '十分', '望古', '嶺腳', '平溪', '菁桐']
        for r in range(4, len(df)):
            t_num = str(df.iloc[r, 2]).strip().replace('.0', '')
            if not t_num.isdigit(): continue
            stops = []
            for c_idx, st_name in zip(down_cols, down_sts):
                if c_idx < df.shape[1]:
                    t_str = clean_time(df.iloc[r, c_idx])
                    if t_str: stops.append({'station': st_name, 'time': t_str})
            if len(stops) >= 2:
                all_trains.append({
                    'train_number': t_num,
                    'train_type': '區間車',
                    'train_model': 'DRC冷氣柴客',
                    'is_trpass': True,
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '平溪深澳線',
                    'stops': stops
                })
        up_cols = [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        up_sts = ['菁桐', '平溪', '嶺腳', '望古', '十分', '大華', '三貂嶺', '猴硐', '瑞芳', '八斗子', '海科館', '四腳亭', '暖暖', '八堵']
        for r in range(4, len(df)):
            t_num = ''
            for c_try in [18, 19, 20, 21, 22]:
                if c_try < df.shape[1] and str(df.iloc[r, c_try]).strip().replace('.0', '').isdigit():
                    t_num = str(df.iloc[r, c_try]).strip().replace('.0', '')
                    break
            if not t_num: continue
            stops = []
            for c_idx, st_name in zip(up_cols, up_sts):
                if c_idx < df.shape[1]:
                    t_str = clean_time(df.iloc[r, c_idx])
                    if t_str: stops.append({'station': st_name, 'time': t_str})
            if len(stops) >= 2:
                all_trains.append({
                    'train_number': t_num,
                    'train_type': '區間車',
                    'train_model': 'DRC冷氣柴客',
                    'is_trpass': True,
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '平溪深澳線',
                    'stops': stops
                })

    # Jiji
    path = os.path.join(folder, 'JIJI20260701.ods')
    if os.path.exists(path):
        df = pd.read_excel(path, engine='odf', header=None)
        jiji_down_sts = ['二水', '源泉', '濁水', '龍泉', '集集', '水里', '車埕']
        for r in range(3, len(df)):
            t_num = str(df.iloc[r, 2]).strip().replace('.0', '')
            if not t_num.isdigit(): continue
            stops = []
            for c_idx, st_name in enumerate(jiji_down_sts, start=4):
                if c_idx < df.shape[1]:
                    t_str = clean_time(df.iloc[r, c_idx])
                    if t_str: stops.append({'station': st_name, 'time': t_str})
            if len(stops) >= 2:
                all_trains.append({
                    'train_number': t_num,
                    'train_type': '區間車',
                    'train_model': 'DRC冷氣柴客',
                    'is_trpass': True,
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '集集線',
                    'stops': stops
                })
        jiji_up_sts = ['車埕', '水里', '集集', '龍泉', '濁水', '源泉', '二水']
        for r in range(3, len(df)):
            t_num = str(df.iloc[r, 14]).strip().replace('.0', '') if df.shape[1] > 14 else ''
            if not t_num.isdigit(): continue
            stops = []
            for c_idx, st_name in enumerate(jiji_up_sts, start=16):
                if c_idx < df.shape[1]:
                    t_str = clean_time(df.iloc[r, c_idx])
                    if t_str: stops.append({'station': st_name, 'time': t_str})
            if len(stops) >= 2:
                all_trains.append({
                    'train_number': t_num,
                    'train_type': '區間車',
                    'train_model': 'DRC冷氣柴客',
                    'is_trpass': True,
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '集集線',
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
                    'stops': stops
                })

parse_branches()

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
                all_trains.append({
                    'train_number': t_num,
                    'train_type': t_type,
                    'train_model': t_model,
                    'is_trpass': is_tr,
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': line_name,
                    'stops': stops
                })
    except Exception as e:
        print(f'Error parsing commuter {fname}: {e}')

# 3. Mainline Express Trains (Format A)
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
                
        # Parse station list from English names in cols 1 and 3
        stations = []
        is_parallel = 'Keelung' in fname or 'Chaozhou' in fname
        
        for r in range(t_row + 2, len(df)):
            eng_name_1 = str(df.iloc[r, 1]).strip() if df.shape[1] > 1 else ''
            eng_name_0 = str(df.iloc[r, 0]).strip()
            
            zh_name = ENG_TO_ZH.get(eng_name_1, ENG_TO_ZH.get(eng_name_0, ''))
            
            # Mountain line station name
            zh_name_mt = zh_name
            if is_parallel and df.shape[1] > 3:
                eng_name_mt = str(df.iloc[r, 3]).strip() if df.shape[1] > 3 else ''
                if eng_name_mt in ENG_TO_ZH:
                    zh_name_mt = ENG_TO_ZH[eng_name_mt]
                    
            if zh_name or zh_name_mt:
                if not zh_name: zh_name = zh_name_mt
                stations.append({'row': r, 'name': zh_name, 'name_mt': zh_name_mt})
                
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
            for st in stations:
                t_str = clean_time(df.iloc[st['row'], c])
                if t_str:
                    st_name = st['name_mt'] if is_mountain else st['name']
                    stops.append({'station': st_name, 'time': t_str})
                    
            if len(stops) >= 2:
                all_trains.append({
                    'train_number': t_num,
                    'train_type': t_type,
                    'train_model': t_model,
                    'is_trpass': is_tr,
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '對號特快',
                    'stops': stops
                })
    except Exception as e:
        print(f'Error parsing express {fname}: {e}')

# Deduplicate and Merge trains by train number
merged = {}
for t in all_trains:
    num = t['train_number']
    if num not in merged:
        merged[num] = t
    else:
        existing_times = {s['time'] for s in merged[num]['stops']}
        for s in t['stops']:
            if s['time'] not in existing_times:
                merged[num]['stops'].append(s)
                existing_times.add(s['time'])
                
        stops = merged[num]['stops']
        stops.sort(key=lambda x: time_to_min(x['time']))
        merged[num]['stops'] = stops
        merged[num]['origin'] = stops[0]['station']
        merged[num]['dest'] = stops[-1]['station']
        # Prioritize express type info if available
        if '自強' in t['train_type'] or '普悠瑪' in t['train_type'] or '莒光' in t['train_type']:
            merged[num]['train_type'] = t['train_type']
            merged[num]['train_model'] = t['train_model']
            merged[num]['is_trpass'] = t['is_trpass']

final_train_list = list(merged.values())

# Clean all stations list
all_st_set = set()
for t in final_train_list:
    for s in t['stops']:
        all_st_set.add(s['station'])

print(f'Total final unique trains: {len(final_train_list)}')
print(f'Total stations: {len(all_st_set)}')
print('All clean station names:', sorted(list(all_st_set)))

output_path = os.path.join(folder, 'full_network_timetable.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(final_train_list, f, ensure_ascii=False, indent=2)

print(f'Saved to {output_path}')
