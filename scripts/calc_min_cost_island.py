# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

# TRA Official Fare Calculation:
# Base per km rate:
# 區間車 (Local): 1.46 NT$/km
# 莒光號 (Chu-Kwang): 1.75 NT$/km
# 自強號 (Tze-Chiang / EMU3000 / Puyuma): 2.27 NT$/km

# Official Station Distances from 板橋 (approx cumulative km around island):
# 板橋 -> 花蓮: 196.8 km (自強 440, 莒光 340, 區間 283)
# 花蓮 -> 台東: 150.9 km (自強 343, 莒光 264, 區間 219)
# 板橋 -> 台東 (東部幹線): 347.7 km (自強 783, 莒光 604, 區間 502)
# 台東 -> 潮州 (南迴線): 108.5 km (自強 246, 莒光 190, 區間 158)
# 台東 -> 枋寮 (南迴線): 83.3 km (自強 189, 莒光 146, 區間 122)
# 潮州 -> 板橋 (西部幹線): 398.6 km (自強 905, 莒光 698, 區間 582)

# Full Island Distance (板橋 -> 台東 -> 潮州 -> 板橋):
# 347.7 + 108.5 + 398.6 = 854.8 km

# Let's compare all cost strategies:
print("=== 台灣環島一圈票價方案精算 (板橋出發) ===")
print("全島總里程: 約 855 公里\n")

# Strategy 1: All Tze-Chiang (Fastest, High Comfort)
fare_tc_all = 783 + 246 + 905
print(f"方案 1: 全段自強號/EMU3000/普悠瑪單程票")
print(f"  板橋 ➔ 台東: NT$ 783 (402次 05:54-10:10)")
print(f"  台東 ➔ 潮州: NT$ 246 (168次 16:00-17:20)")
print(f"  潮州 ➔ 板橋: NT$ 905 (168次 17:20-22:15 直通 / 或 154次)")
print(f"  💰 總金錢成本: NT$ {fare_tc_all}")
print(f"  ⏱️ 總旅行時間: 約 16 小時 (含台東停留 5.8 小時)\n")

# Strategy 2: TR-PASS 學生版 5日券 + 補 1 段特快
# Student TR-PASS 5-day is NT$ 599 (Valid on all PP Tze-Chiang, Chu-Kwang, Local Trains)
# Add 1 segment ticket: 枋寮 ➔ 台東 (EMU3000 自強號 NT$ 189) or 花蓮 ➔ 台東
print(f"方案 2: 【學生/青年最省】TR-PASS 學生版 5日券 (NT$ 599) + 單段自強補票 (NT$ 189)")
print(f"  票券費用: NT$ 599 (學生版 TR-PASS 5日券)")
print(f"  加購自強號 (枋寮 ➔ 台東): NT$ 189 (搭 431次 EMU3000)")
print(f"  其餘全線 (板橋➔枋寮, 台東➔花蓮➔板橋): 全程 TR-PASS 免費無限搭乘")
print(f"  💰 總金錢成本: NT$ {599 + 189} (平均每天只要 NT$ 157，若用 5 天更是超值)")
print(f"  ⏱️ 總旅行時間: 約 17 小時\n")

# Strategy 3: TR-PASS 一般版 3日券 (NT$ 1,800) + 補 1 段
print(f"方案 3: 【一般成人 TR-PASS 方案】TR-PASS 一般版 3日券 (NT$ 1,800) + 補票 NT$ 189")
print(f"  票券費用: NT$ 1,800 + NT$ 189 = NT$ 1,989")
print(f"  (若只環島 1 天，與方案 1 單買差不多；但若 3 天內還有其他台鐵行程，則極划算)\n")

# Strategy 4: 純單買混合平價票 (區間快 + 莒光號 + 優惠自強號)
fare_mixed = 502 + 190 + 905 # (東部區間快 + 南迴莒光 + 西部自強)
print(f"方案 4: 【小資單買混合票】區間快 + 莒光號 + 自強號")
print(f"  板橋 ➔ 台東 (區間快車): NT$ 502")
print(f"  台東 ➔ 潮州 (莒光號 708次): NT$ 190")
print(f"  潮州 ➔ 板橋 (自強號 152次/154次): NT$ 905")
print(f"  💰 總金錢成本: NT$ {fare_mixed}")
print(f"  ⏱️ 總旅行時間: 約 18 小時\n")
