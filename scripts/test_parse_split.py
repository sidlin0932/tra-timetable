import pandas as pd
import re
import json

def normalize_station(st):
    st = str(st).replace('臺', '台').strip()
    st = re.sub(r'[\d:\-－\s\u3000]+', '', st)
    station_clean_map = {
        '鳳': '鳳山', '松': '松山', '佳': '山佳', '冬': '冬山', '岡': '岡山',
        '屏': '屏東', '潮': '潮州', '枋': '枋寮', '竹': '新竹', '義': '嘉義',
        '南': '南港', '新城': '新城(太魯閣)', '新城太魯閣': '新城(太魯閣)',
        '高雄ArrivalTime': '高雄', 'TaipeiArrivalTime': '台北', 'Kaohsiung': '高雄', 'Taipei': '台北'
    }
    return station_clean_map.get(st, st)

def clean_time(val):
    if pd.isna(val): return None
    s = str(val).strip()
    if s.endswith('.0'): s = s[:-2]
    match = re.search(r'(\d{1,2}):(\d{2})', s)
    if match:
        h, m = int(match.group(1)), int(match.group(2))
        return f"{h:02d}:{m:02d}"
    return None

def test_file(fname):
    df = pd.read_excel('data/raw_ods/' + fname, engine='odf', header=None)
    stations = []
    for r in range(12, len(df)):
        c0 = normalize_station(df.iloc[r, 0]) if pd.notna(df.iloc[r, 0]) else ''
        c4 = normalize_station(df.iloc[r, 4]) if df.shape[1] > 4 and pd.notna(df.iloc[r, 4]) else ''
        if c4:
            stations.append({'row': r, 'sea': c0, 'mountain': c4, 'is_split': True})
        elif c0 and c0 not in ['nan', '站名', '起訖站', '備註']:
            stations.append({'row': r, 'name': c0, 'is_split': False})

    parsed = []
    for c in range(8, df.shape[1]):
        t_num = str(df.iloc[3, c]).strip().replace('.0', '')
        if not t_num.isdigit(): continue
        t_type = str(df.iloc[2, c]).strip()
        marker = str(df.iloc[4, c]).strip() if pd.notna(df.iloc[4, c]) else ''
        is_mt = ('山' in marker or 's' in marker)
        is_sea = ('海' in marker or 'c' in marker)
        
        stops = []
        for st in stations:
            t_str = clean_time(df.iloc[st['row'], c])
            if t_str:
                if st.get('is_split'):
                    st_name = st['mountain'] if is_mt else st['sea']
                else:
                    st_name = st['name']
                stops.append({'station': st_name, 'time': t_str})
        if len(stops) >= 2:
            parsed.append({'num': t_num, 'type': t_type, 'marker': marker, 'mt': is_mt, 'sea': is_sea, 'stops': stops})

    print(f"=== {fname}: {len(parsed)} trains parsed ===")
    for p in parsed[:6]:
        st_names = [s['station'] for s in p['stops']]
        line_type = '山線' if p['mt'] else ('海線' if p['sea'] else '全線/直通')
        print(f"  Train {p['num']} ({p['type']} / {line_type} / marker={p['marker']}): {st_names[0]} -> {st_names[-1]} ({len(st_names)} stops) | {st_names}")

test_file('KeelungToChaozhou20260701.ods')
test_file('ChaozhouToKeelung20260701.ods')
