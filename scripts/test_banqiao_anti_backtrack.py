import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

# Load CORRIDOR_MAPS
WEST_NORTH = ['基隆', '三坑', '八堵', '七堵', '百福', '五堵', '汐止', '汐科', '南港', '松山', '台北', '萬華', '板橋', '浮洲', '樹林', '南樹林', '山佳', '鶯歌', '桃園', '內壢', '中壢', '埔心', '楊梅', '富岡', '新富', '北湖', '湖口', '新豐', '竹北', '北新竹', '新竹', '三姓橋', '香山', '崎頂', '竹南']
MOUNTAIN = ['竹南', '造橋', '豐富', '苗栗', '南勢', '銅鑼', '三義', '泰安', '后里', '豐原', '栗林', '潭子', '頭家厝', '松竹', '太原', '精武', '台中', '五權', '大慶', '烏日', '新烏日', '成功', '彰化']
SEA = ['竹南', '談文', '大山', '後龍', '龍港', '白沙屯', '新埔', '通霄', '苑裡', '日南', '大甲', '台中港', '清水', '沙鹿', '龍井', '大肚', '追分', '彰化']
SOUTH = ['彰化', '花壇', '大村', '員林', '永靖', '社頭', '田中', '二水', '林內', '石榴', '斗六', '斗南', '石龜', '大林', '民雄', '嘉北', '嘉義', '水上', '南靖', '後壁', '新營', '柳營', '林鳳營', '隆田', '拔林', '善化', '南科', '新市', '永康', '大橋', '台南', '保安', '仁德', '中洲', '大湖', '路竹', '岡山', '橋頭', '楠梓', '新左營', '左營', '內惟', '美術館', '鼓山', '三塊厝', '高雄', '民族', '科工館', '正義', '鳳山', '後庄', '九曲堂', '六塊厝', '屏東', '歸來', '麟洛', '西勢', '竹田', '潮州', '崁頂', '南州', '鎮安', '林邊', '佳冬', '東海', '枋寮']
SOUTH_LINK = ['枋寮', '加祿', '內獅', '枋山', '枋野', '大武', '瀧溪', '金崙', '太麻里', '知本', '康樂', '台東']
EAST = ['台東', '山里', '鹿野', '瑞源', '瑞和', '月美', '關山', '海端', '池上', '富里', '東竹', '東里', '玉里', '三民', '瑞穗', '富源', '大富', '光復', '萬榮', '鳳林', '南平', '林榮新光', '豐田', '壽豐', '平和', '志學', '吉安', '花蓮']
YILAN_NORTH_LINK = ['八堵', '暖暖', '四腳亭', '瑞芳', '猴硐', '三貂嶺', '牡丹', '雙溪', '貢寮', '福隆', '石城', '大里', '大溪', '龜山', '外澳', '頭城', '頂埔', '礁溪', '四城', '宜蘭', '二結', '中里', '羅東', '冬山', '新馬', '蘇澳新', '蘇澳', '永樂', '東澳', '南澳', '武塔', '漢本', '和平', '和仁', '崇德', '新城(太魯閣)', '景美', '北埔', '花蓮']

WEST_TO_EAST_MOUNTAIN = ['新竹', '北新竹', '竹北', '新豐', '湖口', '北湖', '新富', '富岡', '楊梅', '埔心', '中壢', '內壢', '桃園', '鶯歌', '山佳', '南樹林', '樹林', '浮洲', '板橋', '萬華', '台北', '松山', '南港', '汐科', '汐止', '五堵', '百福', '七堵', '八堵'] + YILAN_NORTH_LINK[1:] + EAST[1:] + SOUTH_LINK[1:]

CORRIDORS = [
    WEST_TO_EAST_MOUNTAIN,
    WEST_NORTH + MOUNTAIN[1:] + SOUTH[1:] + SOUTH_LINK[1:] + EAST[1:] + YILAN_NORTH_LINK[::-1][1:],
    WEST_NORTH + SEA[1:] + SOUTH[1:] + SOUTH_LINK[1:] + EAST[1:] + YILAN_NORTH_LINK[::-1][1:],
    ['八堵', '暖暖', '四腳亭', '瑞芳', '猴硐', '三貂嶺', '大華', '十分', '望古', '嶺腳', '平溪', '菁桐'],
    ['新竹', '北新竹', '千甲', '新莊', '竹中', '上員', '榮華', '竹東', '橫山', '九讚頭', '合興', '富貴', '內灣'],
    ['新竹', '北新竹', '千甲', '新莊', '竹中', '六家'],
    ['二水', '源泉', '濁水', '龍泉', '集集', '水里', '車埕'],
    ['善化', '南科', '新市', '永康', '大橋', '台南', '保安', '仁德', '中洲', '長榮大學', '沙崙']
]

TERMINAL_HUBS = {'七堵', '八堵', '基隆', '新左營', '高雄', '二水', '竹中', '瑞芳'}

def is_overshooting(orig, dest, mid):
    if not orig or not dest or not mid or mid == orig or mid == dest:
        return False
    for corridor in CORRIDORS:
        if orig in corridor and dest in corridor and mid in corridor:
            iOrig = corridor.index(orig)
            iDest = corridor.index(dest)
            iMid = corridor.index(mid)
            minP = min(iOrig, iDest)
            maxP = max(iOrig, iDest)
            if iMid < minP or iMid > maxP:
                if mid in TERMINAL_HUBS and abs(iMid - iDest) <= 2:
                    continue
                return True
    return False

# Test Banqiao -> Yilan at 16:55
def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

# Check first hop departures from 板橋 after 16:55
bq_deps = []
for t in trains:
    stops = t['stops']
    st_names = [s['station'] for s in stops]
    if '板橋' in st_names:
        idx = st_names.index('板橋')
        dep_time = stops[idx]['time']
        dep_min = time_to_min(dep_time)
        if 1015 <= dep_min <= 1040: # 16:55 to 17:20
            bq_deps.append((t['train_number'], t['train_type'], dep_time, stops[idx+1:]))

print(f"Departures from 板橋 (16:55 ~ 17:20): {len(bq_deps)}")
for no, ttype, dep, next_stops in bq_deps:
    dest_stops = [s['station'] for s in next_stops]
    print(f"  Train {no} ({ttype}) at {dep} -> next stops: {dest_stops[:5]}")
    for s in next_stops:
        st = s['station']
        overshoot = is_overshooting('板橋', '宜蘭', st)
        if st in ['桃園', '中壢', '樹林', '台北', '松山', '南港', '八堵', '瑞芳']:
            print(f"     to {st}: is_overshooting = {overshoot}")
