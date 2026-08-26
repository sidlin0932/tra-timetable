import re
import pandas as pd
import json
import os

def time_to_min(time_str):
    if not time_str or ':' not in time_str: return -1
    try:
        h, m = map(int, time_str.split(':'))
        return h * 60 + m
    except:
        return -1

folder = 'f:/Antigravity/台鐵時刻表0701'
files = [f for f in os.listdir(folder) if f.endswith('.ods') and '0701' in f]

all_trains = []

def extract_type_and_model(raw_str, fallback_str=''):
    raw = str(raw_str).strip()
    fallback = str(fallback_str).strip()
    combined = raw + ' ' + fallback
    
    t_type = 'Unknown'
    t_model = 'Unknown'
    
    if '3000' in combined:
        t_type = '自強'
        t_model = 'EMU3000'
    elif '普悠瑪' in combined:
        t_type = '自強'
        t_model = '普悠瑪 (TEMU2000)'
    elif '太魯閣' in combined:
        t_type = '自強'
        t_model = '太魯閣 (TEMU1000)'
    elif '自強' in combined or 'j' in combined:
        t_type = '自強'
        t_model = 'PP自強號'
    elif '莒光' in combined or '莒' in combined or '653' in combined:
        t_type = '莒光'
        t_model = '莒光號客車'
    elif '區間快' in combined or '快' in combined:
        t_type = '區間快'
        t_model = 'EMU系列'
    elif '區間' in combined or '車' in combined or 'c' in combined or '϶' in combined or 'sW' in combined:
        t_type = '區間車'
        t_model = 'EMU系列'
    else:
        if '1802' in combined or '170' in combined or '47' in combined or '27' in combined or '31' in combined or '32' in combined:
            t_type = '區間車'
            t_model = 'EMU/DRC系列'
        else:
            t_type = raw
            t_model = raw
            
    return t_type, t_model

def get_direction(filename):
    lower_f = filename.lower()
    if 'tochaozhou' in lower_f or 'tochiayi' in lower_f or 'tokaohsiung' in lower_f or 'tochanghua' in lower_f or 'tohsinchu' in lower_f or 'tofangliao' in lower_f or 'totaitung' in lower_f or '基隆→新竹' in filename:
        return '南下/順行 (Southbound/Clockwise)'
    if 'tokeelung' in lower_f or 'tobadu' in lower_f or 'toshulin' in lower_f:
        return '北上/逆行 (Northbound/Counter-clockwise)'
    return '未知 (Unknown)'

def get_clean_station_name(raw_name):
    name = str(raw_name).strip()
    name = name.replace('nan', '').replace(' ', '').replace('\n', '')
    
    # Strip common header noise
    noise_words = [
        'ArrivalTime', 'DepartureTime', 'Arr.', 'Dep.', 
        '到', '開', 'TrainNumber', 'TrainType', 'TrainModel'
    ]
    for w in noise_words:
        name = name.replace(w, '')
        
    if 'Nei' in name: return '內灣線車站'
    if not name: return "Unknown"
    return name

for filename in files:
    branch_lines = ['JIJI', 'Neiwan', 'Pingxi', 'Shalun']
    if any(b in filename for b in branch_lines):
        continue
        
    path = os.path.join(folder, filename)
    try:
        df = pd.read_excel(path, engine='odf', header=None)
    except Exception as e:
        continue
        
    if df.shape[0] == 0 or df.shape[1] == 0:
        continue

    is_format_a = False
    is_format_b = False
    train_num_row = -1
    train_num_col = -1
    
    if len(df) > 3:
        for r_check in range(1, 6):
            vals = [str(x).strip().replace('.0', '') for x in df.iloc[r_check, 4:min(15, len(df.columns))] if pd.notna(x)]
            if len(vals) >= 3 and all(v.isdigit() or (len(v)>=2 and v[0].isdigit()) for v in vals) and not any(':' in v for v in vals):
                is_format_a = True
                train_num_row = r_check
                break

    if len(df.columns) > 2 and not is_format_a:
        for c_check in range(1, 5):
            vals = [str(x).strip().replace('.0', '') for x in df.iloc[3:min(15, len(df)), c_check] if pd.notna(x)]
            if len(vals) >= 3 and all(v.isdigit() or (len(v)>=2 and v[0].isdigit()) for v in vals) and not any(':' in v for v in vals):
                is_format_b = True
                train_num_col = c_check
                break
            
    direction = get_direction(filename)
            
    if is_format_a:
        stations = []
        for r in range(train_num_row + 2, len(df)):
            raw_st = "".join(str(df.iloc[r, c]).strip() for c in range(min(4, len(df.columns))))
            name = get_clean_station_name(raw_st)
            
            is_parallel_file = 'KeelungToChaozhou' in filename or 'ChaozhouToKeelung' in filename
            name_mt = name
            if is_parallel_file and len(df.columns) > 8:
                raw_st_mt = "".join(str(df.iloc[r, c]).strip() for c in range(4, min(8, len(df.columns))))
                parsed_mt = get_clean_station_name(raw_st_mt)
                if parsed_mt != "Unknown":
                    name_mt = parsed_mt
                    
            if name != "Unknown" or (is_parallel_file and name_mt != "Unknown"):
                if name == "Unknown": name = name_mt
                stations.append({'row': r, 'name': name, 'name_mt': name_mt})
                
        type_row = train_num_row - 1 if train_num_row > 0 else 0
        for c in range(4, len(df.columns)):
            train_num = str(df.iloc[train_num_row, c]).strip().replace('.0', '')
            if not train_num or train_num == 'nan' or ':' in train_num: continue
            
            raw_type = str(df.iloc[type_row, c]).strip()
            raw_fallback = str(df.iloc[max(0, type_row-1), c]).strip()
            t_type, t_model = extract_type_and_model(raw_type, raw_fallback)
            
            is_mountain = False
            is_parallel_file = 'KeelungToChaozhou' in filename or 'ChaozhouToKeelung' in filename
            if is_parallel_file:
                marker = str(df.iloc[train_num_row + 1, c]).strip()
                # 's' is the CP950 representation of '山' which gets corrupted in XML, '山' is utf-8
                is_mountain = ('s' in marker or '山' in marker)
            
            stops = []
            for st in stations:
                time = str(df.iloc[st['row'], c]).strip()
                if len(time) >= 4 and ':' in time:
                    final_name = st.get('name_mt', st['name']) if is_mountain else st['name']
                    stops.append({'station': final_name, 'arrival_time': time})
            if stops:
                all_trains.append({
                    'train_number': train_num,
                    'train_type': t_type,
                    'train_model': t_model,
                    'direction': direction,
                    'source_file': filename,
                    'stops': stops
                })
                
    elif is_format_b:
        stations = []
        for c in range(train_num_col + 1, len(df.columns)):
            raw_st = "".join(str(df.iloc[r, c]).strip() for r in range(1, min(3, len(df))))
            name = get_clean_station_name(raw_st)
            if name != "Unknown":
                stations.append({'col': c, 'name': name})
                
        # HARDCODE MOUNTAIN LINE OVERRIDE
        if 'HsinchuToChanghua' in filename or 'ChanghuaToHsinchu' in filename:
            mountain_sb = ['新竹', '三姓橋', '香山', '崎頂', '竹南', '造橋', '豐富', '苗栗', '南勢', '銅鑼', '三義', '泰安', '后里', '豐原', '栗林', '潭子', '頭家厝', '松竹', '太原', '精武', '台中', '五權', '大慶', '烏日', '新烏日', '成功', '彰化']
            st_names = mountain_sb if 'HsinchuToChanghua' in filename else mountain_sb[::-1]
            stations = []
            for i, c in enumerate(range(train_num_col + 2, train_num_col + 2 + len(st_names))):
                stations.append({'col': c, 'name': st_names[i]})
                
        type_col = train_num_col - 1 if train_num_col > 0 else 0
        fallback_col = train_num_col - 2 if train_num_col > 1 else 0
        for r in range(3, len(df)):
            train_num = str(df.iloc[r, train_num_col]).strip().replace('.0', '')
            if not train_num or train_num == 'nan' or ':' in train_num: continue
            
            raw_type = str(df.iloc[r, type_col]).strip()
            raw_fallback = str(df.iloc[r, fallback_col]).strip()
            t_type, t_model = extract_type_and_model(raw_type, raw_fallback)
            
            stops = []
            for st in stations:
                time = str(df.iloc[r, st['col']]).strip()
                if len(time) >= 4 and ':' in time:
                    stops.append({'station': st['name'], 'arrival_time': time})
                    
            if stops:
                all_trains.append({
                    'train_number': train_num,
                    'train_type': t_type,
                    'train_model': t_model,
                    'direction': direction,
                    'source_file': filename,
                    'stops': stops
                })

eng_to_zh = {
    'Keelung': '基隆', 'Qidu': '七堵', 'Songshan': '松山', 'Taipei': '台北', 'Taipei(MainStation)': '台北',
    'Banqiao': '板橋', 'Shulin': '樹林', 'Taoyuan': '桃園', 'Zhongli': '中壢',
    'Hsinchu': '新竹', 'Taichung': '台中', 'Changhua': '彰化', 'Chiayi': '嘉義',
    'Tainan': '台南', 'Kaohsiung': '高雄', 'Xinzuoying': '新左營', 'Pingtung': '屏東',
    'Chaozhou': '潮州', 'Taitung': '台東', 'Hualien': '花蓮', 'Yilan': '宜蘭', 'Ruifang': '瑞芳'
}

merged_trains = {}
for t in all_trains:
    num = t['train_number']
    if num not in merged_trains:
        merged_trains[num] = t
    else:
        # Deduplicate by TIME instead of NAME to prevent same-time duplicates across files
        existing_times = {s['arrival_time'] for s in merged_trains[num]['stops']}
        for s in t['stops']:
            if s['arrival_time'] not in existing_times:
                merged_trains[num]['stops'].append(s)
                existing_times.add(s['arrival_time'])
                
        # Sort stops circularly to handle overnight trains properly
        if len(merged_trains[num]['stops']) > 1:
            stops = merged_trains[num]['stops']
            # Remove stops with invalid times
            stops = [s for s in stops if time_to_min(s['arrival_time']) != -1]
            
            # Sort numerically first (0 to 1439)
            stops.sort(key=lambda x: time_to_min(x['arrival_time']))
            
            # Find the largest gap in the 24-hour cycle
            max_gap = -1
            split_idx = 0
            n = len(stops)
            for i in range(n):
                t1 = time_to_min(stops[i]['arrival_time'])
                t2 = time_to_min(stops[(i + 1) % n]['arrival_time'])
                
                gap = t2 - t1
                if gap < 0:
                    gap += 24 * 60
                    
                if gap > max_gap:
                    max_gap = gap
                    split_idx = (i + 1) % n
            
            # The start of the train is the stop immediately following the largest gap
            merged_trains[num]['stops'] = stops[split_idx:] + stops[:split_idx]
            
        if t['source_file'] not in merged_trains[num]['source_file']:
            merged_trains[num]['source_file'] += f" & {t['source_file']}"

# Post-processing: Normalize English names and merge consecutive identical stations (Arrival/Departure)
for t in merged_trains.values():
    new_stops = []
    for s in t['stops']:
        # Normalize name
        st_name = s['station']
        if st_name in eng_to_zh:
            st_name = eng_to_zh[st_name]
        s['station'] = st_name
        
        # Merge if it's the same station as the last one
        if new_stops:
            last_stop = new_stops[-1]
            last_name = last_stop['station']
            # If names are exactly the same, or one is a substring of another (e.g. "高雄" and "高雄Kaohsiung")
            if st_name == last_name or (len(st_name) >= 2 and st_name in last_name) or (len(last_name) >= 2 and last_name in st_name):
                # It's the same station! Set departure time
                last_stop['departure_time'] = s['arrival_time']
                # Pick the longer/better name
                if len(st_name) > len(last_name) and not bool(re.search(r'[a-zA-Z]', st_name)):
                    last_stop['station'] = st_name
                continue
        
        # Ensure single-time stops also have a departure_time key for schema consistency (optional)
        s['departure_time'] = s['arrival_time']
        new_stops.append(s)
        
    t['stops'] = new_stops

final_trains = list(merged_trains.values())
final_trains.sort(key=lambda x: x['train_number'])

output_path = 'f:/Antigravity/台鐵時刻表0701/full_timetable.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump({'trains': final_trains}, f, ensure_ascii=False, indent=2)

print(f"Successfully exported {len(final_trains)} unique trains.")
