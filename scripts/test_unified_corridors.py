import sys
sys.stdout.reconfigure(encoding='utf-8')

WEST_NORTH = ['基隆', '三坑', '八堵', '七堵', '百福', '五堵', '汐止', '汐科', '南港', '松山', '台北', '萬華', '板橋', '浮洲', '樹林', '南樹林', '山佳', '鶯歌', '桃園', '內壢', '中壢', '埔心', '楊梅', '富岡', '新富', '北湖', '湖口', '新豐', '竹北', '北新竹', '新竹', '三姓橋', '香山', '崎頂', '竹南']

MOUNTAIN = ['竹南', '造橋', '豐富', '苗栗', '南勢', '銅鑼', '三義', '泰安', '后里', '豐原', '栗林', '潭子', '頭家厝', '松竹', '太原', '精武', '台中', '五權', '大慶', '烏日', '新烏日', '成功', '彰化']

SEA = ['竹南', '談文', '大山', '後龍', '龍港', '白沙屯', '新埔', '通霄', '苑裡', '日南', '大甲', '台中港', '清水', '沙鹿', '龍井', '大肚', '追分', '彰化']

SOUTH = ['彰化', '花壇', '大村', '員林', '永靖', '社頭', '田中', '二水', '林內', '石榴', '斗六', '斗南', '石龜', '大林', '民雄', '嘉北', '嘉義', '水上', '南靖', '後壁', '新營', '柳營', '林鳳營', '隆田', '拔林', '善化', '南科', '新市', '永康', '大橋', '台南', '保安', '仁德', '中洲', '大湖', '路竹', '岡山', '橋頭', '楠梓', '新左營', '左營', '內惟', '美術館', '鼓山', '三塊厝', '高雄', '民族', '科工館', '正義', '鳳山', '後庄', '九曲堂', '六塊厝', '屏東', '歸來', '麟洛', '西勢', '竹田', '潮州', '崁頂', '南州', '鎮安', '林邊', '佳冬', '東海', '枋寮']

SOUTH_LINK = ['枋寮', '加祿', '內獅', '枋山', '枋野', '大武', '瀧溪', '金崙', '太麻里', '知本', '康樂', '台東']

EAST = ['台東', '山里', '鹿野', '瑞源', '瑞和', '月美', '關山', '海端', '池上', '富里', '東竹', '東里', '玉里', '三民', '瑞穗', '富源', '大富', '光復', '萬榮', '鳳林', '南平', '林榮新光', '豐田', '壽豐', '平和', '志學', '吉安', '花蓮']

NORTH_LINK_YILAN = ['花蓮', '北埔', '景美', '新城(太魯閣)', '崇德', '和仁', '和平', '漢本', '武塔', '南澳', '東澳', '永樂', '蘇澳新', '新馬', '冬山', '羅東', '中里', '二結', '宜蘭', '四城', '礁溪', '頂埔', '頭城', '外澳', '龜山', '大溪', '大里', '石城', '福隆', '貢寮', '雙溪', '牡丹', '三貂嶺', '猴硐', '瑞芳', '四腳亭', '暖暖', '八堵']

# Build unified seamless through-corridors:
# Corridor A: Whole West (via Mountain) + East + Yilan + North (Full continuous Ring)
# Corridor B: Whole West (via Sea) + East + Yilan + North (Full continuous Ring)
# Also West-to-East through Taipei/Badu:
# Corridor West-North-East: [Hsinchu ... Taoyuan ... Banqiao ... Taipei ... Songshan ... Badu ... Yilan ... Hualien ... Taitung]

WEST_TO_EAST = WEST_NORTH[::-1] + NORTH_LINK_YILAN[1:] + EAST[1:] + SOUTH_LINK[1:]
# Note: In WEST_NORTH[::-1], order is: 竹南 ... 桃園 ... 板橋 ... 台北 ... 八堵
# Then NORTH_LINK_YILAN from 八堵 to 宜蘭 to 花蓮!
# Let's verify!
print(f"WEST_TO_EAST length: {len(WEST_TO_EAST)}")
print(f"Sample: {WEST_TO_EAST[WEST_TO_EAST.index('桃園') : WEST_TO_EAST.index('宜蘭')+1]}")

def check_overshoot(corridors, orig, dest, mid):
    TERMINAL_HUBS = {'七堵', '八堵', '基隆', '新左營', '高雄', '二水', '竹中', '瑞芳'}
    for corridor in corridors:
        if orig in corridor and dest in corridor and mid in corridor:
            iOrig = corridor.index(orig)
            iDest = corridor.index(dest)
            iMid = corridor.index(mid)
            minP = min(iOrig, iDest)
            maxP = max(iOrig, iDest)
            if iMid < minP or iMid > maxP:
                if mid in TERMINAL_HUBS and abs(iMid - iDest) <= 2:
                    continue
                return True # Overshoot!
    return False

# Test 1: 板橋 ➔ 宜蘭, mid = 桃園 -> MUST BE OVERSHOOT (True)
corrs = [
    # Full West-North-East corridor
    WEST_NORTH[::-1] + [s for s in NORTH_LINK_YILAN[::-1] if s != '八堵'] + EAST[1:] + SOUTH_LINK[1:]
]
print("Corridor preview around Taipei:")
c = corrs[0]
for st in ['中壢', '桃園', '鶯歌', '板橋', '台北', '松山', '八堵', '瑞芳', '頭城', '礁溪', '宜蘭']:
    print(f"  {st}: index {c.index(st)}")

o1 = check_overshoot(corrs, '板橋', '宜蘭', '桃園')
print(f"\nTest 1 (板橋 ➔ 宜蘭, mid=桃園): isOvershooting = {o1} (Expected: True)")

o2 = check_overshoot(corrs, '板橋', '宜蘭', '中壢')
print(f"Test 2 (板橋 ➔ 宜蘭, mid=中壢): isOvershooting = {o2} (Expected: True)")

o3 = check_overshoot(corrs, '板橋', '宜蘭', '松山')
print(f"Test 3 (板橋 ➔ 宜蘭, mid=松山): isOvershooting = {o3} (Expected: False)")

o4 = check_overshoot(corrs, '板橋', '宜蘭', '瑞芳')
print(f"Test 4 (板橋 ➔ 宜蘭, mid=瑞芳): isOvershooting = {o4} (Expected: False)")

o5 = check_overshoot(corrs, '宜蘭', '板橋', '七堵')
print(f"Test 5 (宜蘭 ➔ 板橋, mid=七堵): isOvershooting = {o5} (Expected: False)")

o6 = check_overshoot(corrs, '宜蘭', '板橋', '花蓮')
print(f"Test 6 (宜蘭 ➔ 板橋, mid=花蓮): isOvershooting = {o6} (Expected: True)")
