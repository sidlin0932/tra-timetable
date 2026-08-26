# -*- coding: utf-8 -*-
import os
import re
import glob
import pandas as pd
import json

folder = 'f:/Antigravity/台鐵時刻表0701'

def clean_time(val):
    if pd.isna(val): return ''
    s = str(val).strip()
    match = re.search(r'(\d{1,2}):(\d{2})', s)
    if match:
        h = int(match.group(1))
        m = int(match.group(2))
        return f"{h:02d}:{m:02d}"
    return ''

def time_to_min(time_str):
    if not time_str or ':' not in time_str: return -1
    try:
        h, m = map(int, time_str.split(':'))
        return h * 60 + m
    except:
        return -1

# Station Translations
ENG_TO_ZH = {
    'Keelung': '\u57fa\u9686', 'Badu': '\u516b\u5835', 'Qidu': '\u4e03\u5835', 'Xizhi': '\u6c50\u6b62', 'Nangang': '\u5357\u6e2f',
    'Songshan': '\u677e\u5c71', 'Taipei': '\u53f0\u5317', 'Wanhua': '\u842c\u83ef', 'Banqiao': '\u677f\u6a4b', 'Shulin': '\u6a39\u6797',
    'Yingge': '\u9daf\u6b4c', 'Taoyuan': '\u6843\u5712', 'Neili': '\u5167\u58e2', 'Zhongli': '\u4e2d\u58e2', 'Puxin': '\u57d4\u5fc3',
    'Yangmei': '\u694a\u6885', 'Fugang': '\u5bcc\u5ca1', 'Xinfu': '\u65b0\u5bcc', 'Beihu': '\u5317\u6e56', 'Hukou': '\u6e56\u53e3',
    'Xinfeng': '\u65b0\u8c50', 'Zhubei': '\u7af9\u5317', 'NorthHsinchu': '\u5317\u65b0\u7af9', 'Hsinchu': '\u65b0\u7af9',
    'Sanxingqiao': '\u4e09\u59d3\u6a4b', 'Xiangshan': '\u9999\u5c71', 'Qiding': '\u5d04\u9802', 'Zhunan': '\u7af9\u5357',
    'Zaociao': '\u9020\u6a4b', 'Fengfu': '\u8c50\u5bcc', 'Miaoli': '\u82d7\u6817', 'Nanshi': '\u5357\u52e2',
    'Tongluo': '\u9285\u947c', 'Sanyi': '\u4e09\u7fa9', 'Tai\'an': '\u6cf0\u5b89', 'Houli': '\u540e\u91cc', 'Fengyuan': '\u8c50\u539f',
    'Lilin': '\u6817\u6797', 'Tanzi': '\u6f6d\u5b50', 'Toujiacuo': '\u982d\u5bb6\u539d', 'Songzhu': '\u677e\u7af9', 'Taiyuan': '\u592a\u539f',
    'Jingwu': '\u7cbe\u6b66', 'Taichung': '\u53f0\u4e2d', 'Wuquan': '\u4e94\u6b0a', 'Daqing': '\u5927\u6176', 'Wuri': '\u70cf\u65e5',
    'Xinwuri': '\u65b0\u70cf\u65e5', 'Chenggong': '\u6210\u529f', 'Changhua': '\u5f70\u5316',
    'Tanwen': '\u8ac7\u6587', 'Dashan': '\u5927\u5c71', 'Houlong': '\u5f8c\u9f8d', 'Longgang': '\u9f8d\u6e2f', 'Baishatun': '\u767d\u6c99\u5c6f',
    'Xinpu': '\u65b0\u57d4', 'Tongxiao': '\u901a\u9704', 'Yuanli': '\u82d1\u88e1', 'Rinan': '\u65e5\u5357', 'Dajia': '\u5927\u7532',
    'TaichungPort': '\u53f0\u4e2d\u6e2f', 'Qingshui': '\u6e05\u6c34', 'Shalu': '\u6c99\u9e7f', 'Longjing': '\u9f8d\u4e95', 'Dadu': '\u5927\u809a',
    'Zhuifen': '\u8ffd\u5206', 'Huatan': '\u82b1\u5887', 'Dacun': '\u5927\u6751', 'Yuanlin': '\u54e1\u6797',
    'Yongjing': '\u6c38\u9756', 'Shetou': '\u793e\u982d', 'Tianzhong': '\u7530\u4e2d', 'Ershui': '\u4e8c\u6c34', 'Linnei': '\u6797\u5167',
    'Shiliu': '\u77f3\u69b4', 'Douliu': '\u6597\u516d', 'Dounan': '\u6597\u5357', 'Shigui': '\u77f3\u9f9c', 'Dalin': '\u5927\u6797',
    'Minxiong': '\u6c11\u96c4', 'Jiabei': '\u5609\u5317', 'Chiayi': '\u5609\u7fa9', 'Shuishang': '\u6c34\u4e0a', 'Nanjing': '\u5357\u9756',
    'Houbi': '\u5f8c\u58c1', 'Xinying': '\u65b0\u71df', 'Liuying': '\u67f3\u71df', 'Linfengying': '\u6797\u9cf3\u71df', 'Longtian': '\u9686\u7530',
    'Balin': '\u62d4\u6797', 'Shanhua': '\u5584\u5316', 'Nanke': '\u5357\u79d1', 'Xinshi': '\u65b0\u5e02', 'Yongkang': '\u6c38\u5eb7',
    'Daqiao': '\u5927\u6a4b', 'Tainan': '\u53f0\u5357', 'Bao\'an': '\u4fdd\u5b89', 'Baoan': '\u4fdd\u5b89', 'Rende': '\u4ec1\u5fb7',
    'Zhongzhou': '\u4e2d\u6d32', 'Dahu': '\u5927\u6e56', 'Luzhu': '\u8def\u7af9', 'Gangshan': '\u5ca1\u5c71', 'Qiaotou': '\u6a4b\u982d',
    'Nanzi': '\u6960\u6893', 'Xinzuoying': '\u65b0\u5de6\u71df', 'Zuoying': '\u5de6\u71df', 'Neiwei': '\u5167\u60df',
    'FineArtsMuseum': '\u7f8e\u8853\u9928', 'Gushan': '\u9f13\u5c71', 'Sankuaihuo': '\u4e09\u584a\u539d', 'Sankuaicuo': '\u4e09\u584a\u539d',
    'Kaohsiung': '\u9ad8\u96c4', 'Minzu': '\u6c11\u65cf', 'ScienceMuseum': '\u79d1\u5de5\u9928', 'Zhengyi': '\u6b63\u7fa9',
    'Fengshan': '\u9cf3\u5c71', 'Houzhuang': '\u5f8c\u5e84', 'Jiuqutang': '\u4e5d\u66f2\u5802', 'Liukuaicuo': '\u516d\u584a\u539d',
    'Pingtung': '\u5c4f\u6771', 'Guilai': '\u6b78\u4f86', 'Linluo': '\u9e9f\u6d1b', 'Xishi': '\u897f\u52e2', 'Zhutian': '\u7af9\u7530',
    'Chaozhou': '\u6f6e\u5dde', 'Kanding': '\u5d01\u9802', 'Nanzhou': '\u5357\u5dde', 'Zhen\'an': '\u93ae\u5b89', 'Zhenan': '\u93ae\u5b89',
    'Linbian': '\u6797\u908a', 'Jiadong': '\u4f73\u51ac', 'Donghai': '\u6771\u6d77', 'Fangliao': '\u678b\u5bee',
    'Jialu': '\u52a0\u797f', 'Neishi': '\u5167\u7345', 'Fangshan': '\u678b\u5c71', 'Dawu': '\u5927\u6b66', 'Longxi': '\u7027\u6eaa',
    'Jinlun': '\u91d1\u5d19', 'Taimali': '\u592a\u9ebb\u91cc', 'Zhiben': '\u77e5\u672c', 'Kangle': '\u5eb7\u6a02', 'Taitung': '\u53f0\u6771',
    'Shanli': '\u5c71\u91cc', 'Luye': '\u9e7f\u91ce', 'Ruiyuan': '\u745e\u6e90', 'Ruihe': '\u745e\u548c', 'Guanshan': '\u95dc\u5c71',
    'Haiduan': '\u6d77\u7aef', 'Chishang': '\u6c60\u4e0a', 'Fuli': '\u5bcc\u91cc', 'Dongzhu': '\u6771\u7af9', 'Dongli': '\u6771\u91cc',
    'Yuli': '\u7389\u91cc', 'Sanmin': '\u4e09\u6c11', 'Ruisui': '\u745e\u7a57', 'Fuyuan': '\u5bcc\u6e90', 'Dafu': '\u5927\u5bcc',
    'Guangfu': '\u5149\u5fa9', 'Wanrong': '\u842c\u69ae', 'Fenglin': '\u9cf3\u6797', 'Nanping': '\u5357\u5e73',
    'LinrongShinKong': '\u6797\u69ae\u65b0\u5149', 'Linrong Shin Kong': '\u6797\u69ae\u65b0\u5149', 'Fengtian': '\u8c50\u7530',
    'Shoufeng': '\u58fd\u8c50', 'Pinghe': '\u5e73\u548c', 'Zhixue': '\u5fd7\u5b78', 'Ji\'an': '\u5409\u5b89', 'Jian': '\u5409\u5b89',
    'Hualien': '\u82b1\u84ee', 'Beipu': '\u5317\u57d4', 'Jingmei': '\u666f\u7f8e', 'Xincheng': '\u65b0\u57ce(\u592a\u9b6f\u95a3)',
    'Chongde': '\u5d07\u5fb7', 'Heren': '\u548c\u4ec1', 'Heping': '\u548c\u5e73', 'Hanben': '\u6f22\u672c', 'Wuta': '\u6b66\u5854',
    'Nan\'ao': '\u5357\u6fb3', 'Nanao': '\u5357\u6fb3', 'Dong\'ao': '\u6771\u6fb3', 'Dongao': '\u6771\u6fb3', 'Yongle': '\u6c38\u6a02',
    'Su\'aoxin': '\u8607\u6fb3\u65b0', 'Suaoxin': '\u8607\u6fb3\u65b0', 'Su\'ao': '\u8607\u6fb3', 'Suao': '\u8607\u6fb3',
    'Dongshan': '\u51ac\u5c71', 'Luodong': '\u7f85\u6771', 'Zhongli(Yilan)': '\u4e2d\u91cc', 'Zhongli2': '\u4e2d\u91cc', 'Erjie': '\u4e8c\u7d50',
    'Yilan': '\u5b9c\u862d', 'Sicheng': '\u56db\u57ce', 'Jiaoxi': '\u7901\u6eaa', 'Dingpu': '\u9802\u57d4', 'Toucheng': '\u982d\u57ce',
    'Wai\'ao': '\u5916\u6fb3', 'Waiao': '\u5916\u6fb3', 'Guishan': '\u9f9c\u5c71', 'Daxi': '\u5927\u6eaa', 'Dali': '\u5927\u91cc',
    'Shicheng': '\u77f3\u57ce', 'Fulong': '\u798f\u9686', 'Gongliao': '\u8ca2\u5bee', 'Shuangxi': '\u96d9\u6eaa', 'Mudan': '\u7261\u4e39',
    'Sandiaoling': '\u4e09\u8c82\u5dba', 'Houtong': '\u7334\u7850', 'Ruifang': '\u745e\u82b3', 'Sijiaoting': '\u56db\u8173\u4ead', 'Nuannuan': '\u6696\u6696',
    'Dahua': '\u5927\u83ef', 'Shifen': '\u5341\u5206', 'Wanggu': '\u671b\u53e4', 'Lingjiao': '\u5dba\u8173', 'Pingxi': '\u5e73\u6eaa',
    'Jingtong': '\u83c1\u6850', 'Haiguan': '\u6d77\u79d1\u9928', 'Badouzi': '\u516b\u6597\u5b50',
    'Qianjia': '\u5343\u7532', 'Xinzhuang': '\u65b0\u838a', 'Zhuzhong': '\u7af9\u4e2d', 'Liujia': '\u516d\u5bb6', 'Shangyuan': '\u4e0a\u54e1',
    'Ronghua': '\u69ae\u83ef', 'Zhudong': '\u7af9\u6771', 'Hengshan': '\u6a6b\u5c71', 'Jiuzantou': '\u4e5d\u8b9a\u982d', 'Hexing': '\u5408\u8208',
    'Fugui': '\u5bcc\u8cb4', 'Neiwan': '\u5167\u7063',
    'Yuanquan': '\u6e90\u6cc9', 'Zhuoshui': '\u6fc1\u6c34', 'Longquan': '\u9f8d\u6cc9', 'Jiji': '\u96c6\u96c6', 'Shuili': '\u6c34\u91cc', 'Checheng': '\u8eca\u5760',
    'ChangrongUniversity': '\u9577\u69ae\u5927\u5b78', 'Chang Jung Christian University': '\u9577\u69ae\u5927\u5b78', 'Shalun': '\u6c99\u5d19'
}

def extract_type_and_model(raw_str, fallback_str=''):
    raw = str(raw_str).strip()
    fallback = str(fallback_str).strip()
    combined = raw + ' ' + fallback
    
    t_type = '\u5340\u9593\u8eca'
    t_model = 'EMU\u7cfb\u5217'
    is_trpass = True
    
    if '3000' in combined or 'EMU3000' in combined:
        t_type = '\u65b0\u81ea\u5f37(EMU3000)'
        t_model = 'EMU3000'
        is_trpass = False
    elif '普悠瑪' in combined or 'TEMU2000' in combined or '\u666e\u60a0\u746a' in combined:
        t_type = '\u666e\u60a0\u746a'
        t_model = '\u666e\u60a0\u746a\u865f'
        is_trpass = False
    elif '太魯閣' in combined or 'TEMU1000' in combined or '\u592a\u9b6f\u95a3' in combined:
        t_type = '\u592a\u9b6f\u95a3'
        t_model = '\u592a\u9b6f\u95a3\u865f'
        is_trpass = False
    elif '自強' in combined or 'T.C.' in combined or '\u81ea\u5f37' in combined:
        t_type = '\u81ea\u5f37\u865f'
        t_model = 'PP\u81ea\u5f37\u865f'
        is_trpass = True
    elif '莒光' in combined or 'C.K.' in combined or '\u8392\u5149' in combined:
        t_type = '\u8392\u5149\u865f'
        t_model = '\u8392\u5149\u865f\u5ba2\u8eca'
        is_trpass = True
    elif '區間快' in combined or '快' in combined or 'Fast' in combined or '\u5340\u9593\u5feb' in combined:
        t_type = '\u5340\u9593\u5feb'
        t_model = 'EMU900/EMU800'
        is_trpass = True
    elif '區間' in combined or 'Local' in combined or '\u5340\u9593' in combined:
        t_type = '\u5340\u9593\u8eca'
        t_model = 'EMU\u7cfb\u5217'
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
        down_stations = ['\u65b0\u7af9', '\u5317\u65b0\u7af9', '\u5343\u7532', '\u65b0\u838a', '\u7af9\u4e2d', '\u516d\u5bb6', '\u4e0a\u54e1', '\u69ae\u83ef', '\u7af9\u6771', '\u6a6b\u5c71', '\u4e5d\u8b9a\u982d', '\u5408\u8208', '\u5bcc\u8cb4', '\u5167\u7063']
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
                    'train_type': '\u5340\u9593\u8eca',
                    'train_model': 'EMU/DRC',
                    'is_trpass': True,
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '\u5167\u7063\u516d\u5bb6\u7dda',
                    'stops': stops
                })
        up_cols = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        up_stations = ['\u5167\u7063', '\u5bcc\u8cb4', '\u5408\u8208', '\u4e5d\u8b9a\u982d', '\u6a6b\u5c71', '\u7af9\u6771', '\u69ae\u83ef', '\u4e0a\u54e1', '\u516d\u5bb6', '\u7af9\u4e2d', '\u65b0\u838a', '\u5343\u7532', '\u5317\u65b0\u7af9', '\u65b0\u7af9']
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
                    'train_type': '\u5340\u9593\u8eca',
                    'train_model': 'EMU/DRC',
                    'is_trpass': True,
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '\u5167\u7063\u516d\u5bb6\u7dda',
                    'stops': stops
                })

    # Pingxi
    path = os.path.join(folder, 'PingxiToShenao20260701.ods')
    if os.path.exists(path):
        df = pd.read_excel(path, engine='odf', header=None)
        down_cols = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        down_sts = ['\u516b\u5835', '\u6696\u6696', '\u56db\u8173\u4ead', '\u6d77\u79d1\u9928', '\u516b\u6597\u5b50', '\u745e\u82b3', '\u7334\u7850', '\u4e09\u8c82\u5dba', '\u5927\u83ef', '\u5341\u5206', '\u671b\u53e4', '\u5dba\u8173', '\u5e73\u6eaa', '\u83c1\u6850']
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
                    'train_type': '\u5340\u9593\u8eca',
                    'train_model': 'DRC\u51b7\u6c23\u67f4\u5ba2',
                    'is_trpass': True,
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '\u5e73\u6eaa\u6df1\u6fb3\u7dda',
                    'stops': stops
                })
        up_cols = [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        up_sts = ['\u83c1\u6850', '\u5e73\u6eaa', '\u5dba\u8173', '\u671b\u53e4', '\u5341\u5206', '\u5927\u83ef', '\u4e09\u8c82\u5dba', '\u7334\u7850', '\u745e\u82b3', '\u516b\u6597\u5b50', '\u6d77\u79d1\u9928', '\u56db\u8173\u4ead', '\u6696\u6696', '\u516b\u5835']
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
                    'train_type': '\u5340\u9593\u8eca',
                    'train_model': 'DRC\u51b7\u6c23\u67f4\u5ba2',
                    'is_trpass': True,
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '\u5e73\u6eaa\u6df1\u6fb3\u7dda',
                    'stops': stops
                })

    # Jiji
    path = os.path.join(folder, 'JIJI20260701.ods')
    if os.path.exists(path):
        df = pd.read_excel(path, engine='odf', header=None)
        jiji_down_sts = ['二水', '源泉', '濁水', '龍泉', '集集', '水里', '車埕']
        jiji_up_sts = ['車埕', '水里', '集集', '龍泉', '濁水', '源泉', '二水']

        for r in range(3, len(df)):
            # Down trains (Col 2 is train number, Cols 4-10 are stops)
            t_num_down = str(df.iloc[r, 2]).strip().replace('.0', '')
            if t_num_down.isdigit():
                stops = []
                for c_idx, st_name in enumerate(jiji_down_sts, start=4):
                    if c_idx < df.shape[1]:
                        t_str = clean_time(df.iloc[r, c_idx])
                        if t_str: stops.append({'station': st_name, 'time': t_str})
                if len(stops) >= 2:
                    all_trains.append({
                        'train_number': t_num_down,
                        'train_type': '區間車' if '車' in str(df.iloc[r, 0]) else '區間快',
                        'train_model': 'DRC冷氣柴客',
                        'is_trpass': True,
                        'origin': stops[0]['station'],
                        'dest': stops[-1]['station'],
                        'line': '集集線',
                        'stops': stops
                    })

            # Up trains (Col 14 is train number, Cols 16-22 are stops)
            if df.shape[1] >= 15:
                t_num_up = str(df.iloc[r, 14]).strip().replace('.0', '')
                if t_num_up.isdigit():
                    stops = []
                    for c_idx, st_name in enumerate(jiji_up_sts, start=16):
                        if c_idx < df.shape[1]:
                            t_str = clean_time(df.iloc[r, c_idx])
                            if t_str: stops.append({'station': st_name, 'time': t_str})
                    if len(stops) >= 2:
                        all_trains.append({
                            'train_number': t_num_up,
                            'train_type': '區間車' if '車' in str(df.iloc[r, 12]) else '區間快',
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
        shalun_down_sts = ['\u5584\u5316', '\u5357\u79d1', '\u65b0\u5e02', '\u6c38\u5eb7', '\u5927\u6a4b', '\u53f0\u5357', '\u4fdd\u5b89', '\u4ec1\u5fb7', '\u4e2d\u6d32', '\u9577\u69ae\u5927\u5b78', '\u6c99\u5d19']
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
                    'train_type': '\u5340\u9593\u8eca',
                    'train_model': 'EMU\u7cfb\u5217',
                    'is_trpass': True,
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '\u6c99\u5d19\u7dda',
                    'stops': stops
                })
        shalun_up_sts = ['\u6c99\u5d19', '\u9577\u69ae\u5927\u5b78', '\u4e2d\u6d32', '\u4ec1\u5fb7', '\u4fdd\u5b89', '\u53f0\u5357', '\u5927\u6a4b', '\u6c38\u5eb7', '\u65b0\u5e02', '\u5357\u79d1', '\u5584\u5316']
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
                    'train_type': '\u5340\u9593\u8eca',
                    'train_model': 'EMU\u7cfb\u5217',
                    'is_trpass': True,
                    'origin': stops[0]['station'],
                    'dest': stops[-1]['station'],
                    'line': '\u6c99\u5d19\u7dda',
                    'stops': stops
                })

parse_branches()

# 2. Commuter Lines (Format B)
commuter_specs = [
    ('BaduToSuao20260701.ods', 0, ['\u516b\u5835', '\u6696\u6696', '\u56db\u8173\u4ead', '\u745e\u82b3', '\u7334\u7850', '\u4e09\u8c82\u5dba', '\u7261\u4e39', '\u96d9\u6eaa', '\u8ca2\u5bee', '\u798f\u9686', '\u77f3\u57ce', '\u5927\u91cc', '\u5927\u6eaa', '\u9f9c\u5c71', '\u5916\u6fb3', '\u982d\u57ce', '\u9802\u57d4', '\u7901\u6eaa', '\u56db\u57ce', '\u5b9c\u862d', '\u4e8c\u7d50', '\u4e2d\u91cc', '\u7f85\u6771', '\u51ac\u5c71', '\u65b0\u99ac', '\u8607\u6fb3\u65b0', '\u8607\u6fb3'], '\u5b9c\u862d\u7dda'),
    ('SuaoToBadu20260701.ods', 0, ['\u8607\u6fb3', '\u8607\u6fb3\u65b0', '\u65b0\u99ac', '\u51ac\u5c71', '\u7f85\u6771', '\u4e2d\u91cc', '\u4e8c\u7d50', '\u5b9c\u862d', '\u56db\u57ce', '\u7901\u6eaa', '\u9802\u57d4', '\u982d\u57ce', '\u5916\u6fb3', '\u9f9c\u5c71', '\u5927\u6eaa', '\u5927\u91cc', '\u77f3\u57ce', '\u798f\u9686', '\u8ca2\u5bee', '\u96d9\u6eaa', '\u7261\u4e39', '\u4e09\u8c82\u5dba', '\u7334\u7850', '\u745e\u82b3', '\u56db\u8173\u4ead', '\u6696\u6696', '\u516b\u5835'], '\u5b9c\u862d\u7dda'),
    ('HsinchuToKeelung20260701.ods', 0, ['\u65b0\u7af9', '\u5317\u65b0\u7af9', '\u7af9\u5317', '\u65b0\u8c50', '\u6e56\u53e3', '\u5317\u6e56', '\u65b0\u5bcc', '\u5bcc\u5ca1', '\u694a\u6885', '\u57d4\u5fc3', '\u4e2d\u58e2', '\u5167\u58e2', '\u6843\u5712', '\u9daf\u6b4c', '\u5c71\u4f73', '\u5357\u6a39\u6797', '\u6a39\u6797', '\u6d6e\u6d32', '\u677f\u6a4b', '\u842c\u83ef', '\u53f0\u5317', '\u677e\u5c71', '\u5357\u6e2f', '\u6c50\u79d1', '\u6c50\u6b62', '\u4e94\u5835', '\u767e\u798f', '\u4e03\u5835', '\u516b\u5835', '\u4e09\u5751', '\u57fa\u9686'], '\u7e31\u8cab\u7dda\u5317\u6bb5'),
    ('基隆→新竹-20260701(0608修).ods', 0, ['\u57fa\u9686', '\u4e09\u5751', '\u516b\u5835', '\u4e03\u5835', '\u767e\u798f', '\u4e94\u5835', '\u6c50\u6b62', '\u6c50\u79d1', '\u5357\u6e2f', '\u677e\u5c71', '\u53f0\u5317', '\u842c\u83ef', '\u677f\u6a4b', '\u6d6e\u6d32', '\u6a39\u6797', '\u5357\u6a39\u6797', '\u5c71\u4f73', '\u9daf\u6b4c', '\u6843\u5712', '\u5167\u58e2', '\u4e2d\u58e2', '\u57d4\u5fc3', '\u694a\u6885', '\u5bcc\u5ca1', '\u65b0\u5bcc', '\u5317\u6e56', '\u6e56\u53e3', '\u65b0\u8c50', '\u7af9\u5317', '\u5317\u65b0\u7af9', '\u65b0\u7af9'], '\u7e31\u8cab\u7dda\u5317\u6bb5'),
    ('HsinchuToChanghua20260701.ods', 0, ['\u65b0\u7af9', '\u4e09\u59d3\u6a4b', '\u9999\u5c71', '\u5d04\u9802', '\u7af9\u5357', '\u9020\u6a4b', '\u8c50\u5bcc', '\u82d7\u6817', '\u5357\u52e2', '\u9285\u947c', '\u4e09\u7fa9', '\u6cf0\u5b89', '\u540e\u91cc', '\u8c50\u539f', '\u6817\u6797', '\u6f6d\u5b50', '\u982d\u5bb6\u539d', '\u677e\u7af9', '\u592a\u539f', '\u7cbe\u6b66', '\u53f0\u4e2d', '\u4e94\u6b0a', '\u5927\u6176', '\u70cf\u65e5', '\u65b0\u70cf\u65e5', '\u6210\u529f', '\u5f70\u5316'], '\u53f0\u4e2d\u7dda(\u5c71\u7dda)'),
    ('ChanghuaToHsinchu20260701.ods', 0, ['\u5f70\u5316', '\u6210\u529f', '\u65b0\u70cf\u65e5', '\u70cf\u65e5', '\u5927\u6176', '\u4e94\u6b0a', '\u53f0\u4e2d', '\u7cbe\u6b66', '\u592a\u539f', '\u677e\u7af9', '\u982d\u5bb6\u539d', '\u6f6d\u5b50', '\u6817\u6797', '\u8c50\u539f', '\u540e\u91cc', '\u6cf0\u5b89', '\u4e09\u7fa9', '\u9285\u947c', '\u5357\u52e2', '\u82d7\u6817', '\u8c50\u5bcc', '\u9020\u6a4b', '\u7af9\u5357', '\u5d04\u9802', '\u9999\u5c71', '\u4e09\u59d3\u6a4b', '\u65b0\u7af9'], '\u53f0\u4e2d\u7dda(\u5c71\u7dda)'),
    ('ChanghuaToChiayi20260701.ods', 0, ['\u5f70\u5316', '\u82b1\u5887', '\u5927\u6751', '\u54e1\u6797', '\u6c38\u9756', '\u793e\u982d', '\u7530\u4e2d', '\u4e8c\u6c34', '\u6797\u5167', '\u77f3\u69b4', '\u6597\u516d', '\u6597\u5357', '\u77f3\u9f9c', '\u5927\u6797', '\u6c11\u96c4', '\u5609\u5317', '\u5609\u7fa9'], '\u7e31\u8cab\u7dda\u5357\u6bb5'),
    ('ChiayiToChanghua20260701.ods', 0, ['\u5609\u7fa9', '\u5609\u5317', '\u6c11\u96c4', '\u5927\u6797', '\u77f3\u9f9c', '\u6597\u5357', '\u6597\u516d', '\u77f3\u69b4', '\u6797\u5167', '\u4e8c\u6c34', '\u7530\u4e2d', '\u793e\u982d', '\u6c38\u9756', '\u54e1\u6797', '\u5927\u6751', '\u82b1\u5887', '\u5f70\u5316'], '\u7e31\u8cab\u7dda\u5357\u6bb5'),
    ('ChiayiToKaohsiung20260701.ods', 0, ['\u5609\u7fa9', '\u6c34\u4e0a', '\u5357\u9756', '\u5f8c\u58c1', '\u65b0\u71df', '\u67f3\u71df', '\u6797\u9cf3\u71df', '\u9686\u7530', '\u62d4\u6797', '\u5584\u5316', '\u5357\u79d1', '\u65b0\u5e02', '\u6c38\u5eb7', '\u5927\u6a4b', '\u53f0\u5357', '\u4fdd\u5b89', '\u4ec1\u5fb7', '\u4e2d\u6d32', '\u5927\u6e56', '\u8def\u7af9', '\u5ca1\u5c71', '\u6a4b\u982d', '\u6960\u6893', '\u65b0\u5de6\u71df', '\u5de6\u71df', '\u5167\u60df', '\u7f8e\u8853\u9928', '\u9f13\u5c71', '\u4e09\u584a\u539d', '\u9ad8\u96c4'], '\u7e31\u8cab\u7dda\u5357\u6bb5'),
    ('KaohsiungToChiayi20260701.ods', 0, ['\u9ad8\u96c4', '\u4e09\u584a\u539d', '\u9f13\u5c71', '\u7f8e\u8853\u9928', '\u5167\u60df', '\u5de6\u71df', '\u65b0\u5de6\u71df', '\u6960\u6893', '\u6a4b\u982d', '\u5ca1\u5c71', '\u8def\u7af9', '\u5927\u6e56', '\u4e2d\u6d32', '\u4ec1\u5fb7', '\u4fdd\u5b89', '\u53f0\u5357', '\u5927\u6a4b', '\u6c38\u5eb7', '\u65b0\u5e02', '\u5357\u79d1', '\u5584\u5316', '\u62d4\u6797', '\u9686\u7530', '\u6797\u9cf3\u71df', '\u67f3\u71df', '\u65b0\u71df', '\u5f8c\u58c1', '\u5357\u9756', '\u6c34\u4e0a', '\u5609\u7fa9'], '\u7e31\u8cab\u7dda\u5357\u6bb5'),
    ('XinzuoyingToFangliao20260701.ods', 0, ['\u65b0\u5de6\u71df', '\u5de6\u71df', '\u5167\u60df', '\u7f8e\u8853\u9928', '\u9f13\u5c71', '\u4e09\u584a\u539d', '\u9ad8\u96c4', '\u6c11\u65cf', '\u79d1\u5de5\u9928', '\u6b63\u7fa9', '\u9cf3\u5c71', '\u5f8c\u5e84', '\u4e5d\u66f2\u5802', '\u516d\u584a\u539d', '\u5c4f\u6771', '\u6b78\u4f86', '\u9e9f\u6d1b', '\u897f\u52e2', '\u7af9\u7530', '\u6f6e\u5dde', '\u5d01\u9802', '\u5357\u5dde', '\u93ae\u5b89', '\u6797\u908a', '\u4f73\u51ac', '\u6771\u6d77', '\u678b\u5bee'], '\u5c4f\u6771\u7dda'),
    ('FangliaoToXinzuoying20260701.ods', 0, ['\u678b\u5bee', '\u6771\u6d77', '\u4f73\u51ac', '\u6797\u908a', '\u93ae\u5b89', '\u5357\u5dde', '\u5d01\u9802', '\u6f6e\u5dde', '\u7af9\u7530', '\u897f\u52e2', '\u9e9f\u6d1b', '\u6b78\u4f86', '\u5c4f\u6771', '\u516d\u584a\u539d', '\u4e5d\u66f2\u5802', '\u5f8c\u5e84', '\u9cf3\u5c71', '\u6b63\u7fa9', '\u79d1\u5de5\u9928', '\u6c11\u65cf', '\u9ad8\u96c4', '\u4e09\u584a\u539d', '\u9f13\u5c71', '\u7f8e\u8853\u9928', '\u5167\u60df', '\u5de6\u71df', '\u65b0\u5de6\u71df'], '\u5c4f\u6771\u7dda'),
    ('NorthLink20260701.ods', 1, ['\u8607\u6fb3\u65b0', '\u6c38\u6a02', '\u6771\u6fb3', '\u5357\u6fb3', '\u6b66\u5854', '\u6f22\u672c', '\u548c\u5e73', '\u548c\u4ec1', '\u5d07\u5fb7', '\u65b0\u57ce(\u592a\u9b6f\u95a3)', '\u666f\u7f8e', '\u5317\u57d4', '\u82b1\u84ee'], '\u5317\u8ff4\u7dda'),
    ('台東線-20260701.ods', 0, ['\u82b1\u84ee', '\u5409\u5b89', '\u5fd7\u5b78', '\u5e73\u548c', '\u58fd\u8c50', '\u8c50\u7530', '\u6797\u69ae\u65b0\u5149', '\u5357\u5e73', '\u9cf3\u6797', '\u842c\u69ae', '\u5149\u5fa9', '\u5927\u5bcc', '\u5bcc\u6e90', '\u745e\u7a57', '\u4e09\u6c11', '\u7389\u91cc', '\u6771\u91cc', '\u6771\u7af9', '\u5bcc\u91cc', '\u6c60\u4e0a', '\u6d77\u7aef', '\u95dc\u5c71', '\u6708\u7f8e', '\u745e\u548c', '\u745e\u6e90', '\u9e7f\u91ce', '\u5c71\u91cc', '\u53f0\u6771'], '\u53f0\u6771\u7dda'),
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
                    'line': '\u5c0d\u865f\u7279\u5feb',
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
        if '自強' in t['train_type'] or '普悠瑪' in t['train_type'] or '莒光' in t['train_type'] or '\u81ea\u5f37' in t['train_type'] or '\u666e\u60a0\u746a' in t['train_type'] or '\u8392\u5149' in t['train_type']:
            merged[num]['train_type'] = t['train_type']
            merged[num]['train_model'] = t['train_model']
            merged[num]['is_trpass'] = t['is_trpass']

final_train_list = list(merged.values())

# Clean all stations list
all_st_set = set()
for t in final_train_list:
    for s in t['stops']:
        all_st_set.add(s['station'])

output_path = os.path.join(folder, 'full_network_timetable.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(final_train_list, f, ensure_ascii=False, indent=2)

print(f'SUCCESS! Total final unique trains: {len(final_train_list)}')
print(f'Total stations: {len(all_st_set)}')
