# -*- coding: utf-8 -*-
import re

print("Applying Anti-Overshoot & Zero-Backtracking Filter to index.html and lite.html...")

corridor_logic = """
        const CORRIDOR_MAPS = [
            ['基隆', '三坑', '八堵', '七堵', '百福', '五堵', '汐止', '汐科', '南港', '松山', '台北', '萬華', '板橋', '浮洲', '樹林', '南樹林', '山佳', '鶯歌', '桃園', '內壢', '中壢', '埔心', '楊梅', '富岡', '新富', '北湖', '湖口', '新豐', '竹北', '北新竹', '新竹', '三姓橋', '香山', '崎頂', '竹南', '造橋', '豐富', '苗栗', '南勢', '銅鑼', '三義', '泰安', '后里', '豐原', '栗林', '潭子', '頭家厝', '松竹', '太原', '精武', '台中', '五權', '大慶', '烏日', '新烏日', '成功', '彰化', '花壇', '大村', '員林', '永靖', '社頭', '田中', '二水', '林內', '石榴', '斗六', '斗南', '石龜', '大林', '民雄', '嘉北', '嘉義', '水上', '南靖', '後壁', '新營', '柳營', '林鳳營', '隆田', '拔林', '善化', '南科', '新市', '永康', '大橋', '台南', '保安', '仁德', '中洲', '大湖', '路竹', '岡山', '橋頭', '楠梓', '新左營', '左營', '內惟', '美術館', '鼓山', '三塊厝', '高雄', '民族', '科工館', '正義', '鳳山', '後庄', '九曲堂', '六塊厝', '屏東', '歸來', '麟洛', '西勢', '竹田', '潮州', '崁頂', '南州', '鎮安', '林邊', '佳冬', '東海', '枋寮'],
            ['基隆', '三坑', '八堵', '七堵', '百福', '五堵', '汐止', '汐科', '南港', '松山', '台北', '萬華', '板橋', '浮洲', '樹林', '南樹林', '山佳', '鶯歌', '桃園', '內壢', '中壢', '埔心', '楊梅', '富岡', '新富', '北湖', '湖口', '新豐', '竹北', '北新竹', '新竹', '三姓橋', '香山', '崎頂', '竹南', '談文', '大山', '後龍', '龍港', '白沙屯', '新埔', '通霄', '苑裡', '日南', '大甲', '台中港', '清水', '沙鹿', '龍井', '大肚', '追分', '彰化', '花壇', '大村', '員林', '永靖', '社頭', '田中', '二水', '林內', '石榴', '斗六', '斗南', '石龜', '大林', '民雄', '嘉北', '嘉義', '水上', '南靖', '後壁', '新營', '柳營', '林鳳營', '隆田', '拔林', '善化', '南科', '新市', '永康', '大橋', '台南', '保安', '仁德', '中洲', '大湖', '路竹', '岡山', '橋頭', '楠梓', '新左營', '左營', '內惟', '美術館', '鼓山', '三塊厝', '高雄', '民族', '科工館', '正義', '鳳山', '後庄', '九曲堂', '六塊厝', '屏東', '歸來', '麟洛', '西勢', '竹田', '潮州', '崁頂', '南州', '鎮安', '林邊', '佳冬', '東海', '枋寮'],
            ['樹林', '浮洲', '板橋', '萬華', '台北', '松山', '南港', '汐科', '汐止', '五堵', '百福', '七堵', '八堵', '暖暖', '四腳亭', '瑞芳', '猴硐', '三貂嶺', '牡丹', '雙溪', '貢寮', '福隆', '石城', '大里', '大溪', '龜山', '外澳', '頭城', '頂埔', '礁溪', '四城', '宜蘭', '二結', '中里', '羅東', '冬山', '新馬', '蘇澳新', '蘇澳', '永樂', '東澳', '南澳', '武塔', '漢本', '和平', '和仁', '崇德', '新城(太魯閣)', '景美', '北埔', '花蓮', '吉安', '志學', '平和', '壽豐', '豐田', '林榮新光', '南平', '鳳林', '萬榮', '光復', '大富', '富源', '瑞穗', '三民', '玉里', '東里', '東竹', '富里', '池上', '海端', '關山', '月美', '瑞和', '瑞源', '鹿野', '山里', '台東'],
            ['新左營', '左營', '內惟', '美術館', '鼓山', '三塊厝', '高雄', '民族', '科工館', '正義', '鳳山', '後庄', '九曲堂', '六塊厝', '屏東', '歸來', '麟洛', '西勢', '竹田', '潮州', '崁頂', '南州', '鎮安', '林邊', '佳冬', '東海', '枋寮', '加祿', '內獅', '枋山', '枋野', '大武', '瀧溪', '金崙', '太麻里', '知本', '康樂', '台東'],
            ['新竹', '北新竹', '千甲', '新莊', '竹中', '上員', '榮華', '竹東', '橫山', '九讚頭', '合興', '富貴', '內灣'],
            ['新竹', '北新竹', '千甲', '新莊', '竹中', '六家'],
            ['八堵', '暖暖', '四腳亭', '瑞芳', '猴硐', '三貂嶺', '大華', '十分', '望古', '嶺腳', '平溪', '菁桐'],
            ['二水', '源泉', '濁水', '龍泉', '集集', '水里', '車埕'],
            ['善化', '南科', '新市', '永康', '大橋', '台南', '保安', '仁德', '中洲', '長榮大學', '沙崙']
        ];

        function isStationOvershooting(orig, dest, mid) {
            if (!orig || !dest || !mid || mid === orig || mid === dest) return false;
            for (let cIdx = 0; cIdx < CORRIDOR_MAPS.length; cIdx++) {
                const corridor = CORRIDOR_MAPS[cIdx];
                const iOrig = corridor.indexOf(orig);
                const iDest = corridor.indexOf(dest);
                const iMid = corridor.indexOf(mid);
                if (iOrig !== -1 && iDest !== -1 && iMid !== -1) {
                    const minP = Math.min(iOrig, iDest);
                    const maxP = Math.max(iOrig, iDest);
                    if (iMid < minP || iMid > maxP) {
                        return true; // Strictly out of corridor bounds!
                    }
                }
            }
            return false;
        }
"""

# 1. Update index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

if 'isStationOvershooting' not in html:
    html = html.replace('function planRoutes(orig, dest, startTimeMin, viaStation = \'\') {',
                        corridor_logic + '\n        function planRoutes(orig, dest, startTimeMin, viaStation = \'\') {')

# In planRoutes hop 1:
# If isStationOvershooting(orig, dest, nextSt), skip!
old_hop1_check = """                        if (KEY_HUBS.has(nextSt) || nextSt === viaStation || j === train1.stops.length - 1) {"""
new_hop1_check = """                        if ((KEY_HUBS.has(nextSt) || nextSt === viaStation || j === train1.stops.length - 1) && !isStationOvershooting(orig, dest, nextSt)) {"""

html = html.replace(old_hop1_check, new_hop1_check)

# In planRoutes hop 2+:
# If isStationOvershooting(orig, dest, nextSt), skip!
old_hop2_check = """                                    if (nextSt !== dest && !KEY_HUBS.has(nextSt) && nextSt !== viaStation && j !== train.stops.length - 1) continue;"""
new_hop2_check = """                                    if (nextSt !== dest && !KEY_HUBS.has(nextSt) && nextSt !== viaStation && j !== train.stops.length - 1) continue;
                                    if (nextSt !== dest && isStationOvershooting(orig, dest, nextSt)) continue;"""

html = html.replace(old_hop2_check, new_hop2_check)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html patched with anti-overshoot filter!")

# 2. Update lite.html
with open('lite.html', 'r', encoding='utf-8') as f:
    lite = f.read()

if 'isStationOvershooting' not in lite:
    lite = lite.replace('function planLeg(orig, dest, startMin, transferMax, typeF) {',
                        corridor_logic + '\n        function planLeg(orig, dest, startMin, transferMax, typeF) {')

# In lite.html 1-Hop transfers:
old_lite_mid_check = """                        if (mid === dest) continue;"""
new_lite_mid_check = """                        if (mid === dest) continue;
                        if (isStationOvershooting(orig, dest, mid)) continue;"""

lite = lite.replace(old_lite_mid_check, new_lite_mid_check)

with open('lite.html', 'w', encoding='utf-8') as f:
    f.write(lite)
print("lite.html patched with anti-overshoot filter!")
