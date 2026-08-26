import json
import re

with open('full_network_timetable.json', 'r', encoding='utf-8') as f:
    trains = json.load(f)

def time_to_min(t_str):
    if not t_str or ':' not in t_str: return -1
    parts = t_str.split(':')
    try:
        return int(parts[0]) * 60 + int(parts[1])
    except:
        return -1

report = {
    'total_trains': len(trains),
    'time_inversion_issues': [],
    'invalid_station_names': [],
    'single_stop_trains': [],
    'duplicate_train_numbers': [],
    'unrealistic_speed_issues': [],
    'trpass_inconsistencies': [],
    'line_stats': {},
    'type_stats': {}
}

# Standard Stations Reference (215 stations)
valid_time_pattern = re.compile(r'^\d{2}:\d{2}$')

seen_train_numbers = {}

for idx, t in enumerate(trains):
    t_no = t.get('train_number', f'UNKNOWN_{idx}')
    t_type = t.get('train_type', '未知')
    stops = t.get('stops', [])
    line = t.get('line', '未知')

    # Line stats
    report['line_stats'][line] = report['line_stats'].get(line, 0) + 1
    report['type_stats'][t_type] = report['type_stats'].get(t_type, 0) + 1

    # Check 1: Single stop train
    if len(stops) < 2:
        report['single_stop_trains'].append(f'{t_no} ({t_type}): only {len(stops)} stops')
        continue

    # Check 2: Duplicate train numbers
    if t_no in seen_train_numbers:
        report['duplicate_train_numbers'].append(f'{t_no} (already seen, conflict with {seen_train_numbers[t_no]})')
    seen_train_numbers[t_no] = t_type

    # Check 3: Stops and Times Validation
    prev_time_min = -1
    for s_idx, s in enumerate(stops):
        st_name = s.get('station', '')
        t_str = s.get('time', '')

        # Station name check
        if not st_name or st_name in ['nan', 'None', '車次', '車種', '時間'] or len(st_name) > 10:
            report['invalid_station_names'].append(f'{t_no}: Invalid station name [{st_name}]')

        # Time format check
        if not valid_time_pattern.match(t_str):
            report['time_inversion_issues'].append(f'{t_no} at {st_name}: Invalid time format [{t_str}]')
            continue

        curr_time_min = time_to_min(t_str)

        # Monotonicity check
        if s_idx > 0:
            # Check if time went backwards without midnight crossover
            if curr_time_min < prev_time_min:
                # Check if it's midnight crossover (e.g. 23:50 -> 00:30)
                if not (prev_time_min >= 23 * 60 and curr_time_min <= 4 * 60):
                    report['time_inversion_issues'].append(
                        f'{t_no} ({t_type}): Time backwards from {stops[s_idx-1]["station"]} ({stops[s_idx-1]["time"]}) to {st_name} ({t_str})'
                    )

            # Unrealistic speed / identical time between different stations
            if curr_time_min == prev_time_min and stops[s_idx-1]["station"] != st_name:
                report['unrealistic_speed_issues'].append(
                    f'{t_no}: Identical time at {stops[s_idx-1]["station"]} and {st_name} ({t_str})'
                )

        prev_time_min = curr_time_min

    # Check 4: TR-PASS consistency
    is_tr = t.get('is_trpass', False)
    if t_type in ['自強號', '莒光號', '區間車', '區間快'] and not is_tr:
        report['trpass_inconsistencies'].append(f'{t_no} ({t_type}): should be TR-PASS eligible')
    elif t_type in ['普悠瑪', '太魯閣', '新自強(EMU3000)'] and is_tr:
        # Note: In standard TR-PASS without reservation, EMU3000/Puyuma are not allowed.
        pass

print("=== 2026 台鐵時刻表資料庫全方位稽核報告 ===")
print(f"1. 總檢核列車總數: {report['total_trains']} 班次")
print(f"2. 停靠站不足 2 站的異常列車: {len(report['single_stop_trains'])} 班")
print(f"3. 車次重複/衝突: {len(report['duplicate_train_numbers'])} 班")
print(f"4. 站名無效/亂碼異常: {len(report['invalid_station_names'])} 處")
print(f"5. 時間倒流/格式錯誤異常: {len(report['time_inversion_issues'])} 處")
print(f"6. 零耗時跳站異常: {len(report['unrealistic_speed_issues'])} 處")

print("\n=== 車種分類統計 ===")
for t_type, cnt in sorted(report['type_stats'].items(), key=lambda x: x[1], reverse=True):
    print(f"  • {t_type}: {cnt} 班")

print("\n=== 各幹線與支線列車覆蓋統計 ===")
for line, cnt in sorted(report['line_stats'].items(), key=lambda x: x[1], reverse=True):
    print(f"  • {line}: {cnt} 班")

if len(report['time_inversion_issues']) > 0:
    print("\n[時間異常列表樣例]:")
    for err in report['time_inversion_issues'][:5]:
        print("  ❌", err)

if len(report['invalid_station_names']) > 0:
    print("\n[站名異常列表樣例]:")
    for err in report['invalid_station_names'][:5]:
        print("  ❌", err)
