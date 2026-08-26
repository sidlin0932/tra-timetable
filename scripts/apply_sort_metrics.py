import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add options to #primarySort and #secondarySort
old_primary_options = """                <select id="primarySort" class="sort-select" onchange="handleSortChange()">
                    <option value="arr_time-asc">抵達時間 最早 (早➔晚)</option>
                    <option value="arr_time-desc">抵達時間 最晚 (晚➔早)</option>
                    <option value="dep_time-asc">出發時間 最早 (早➔晚)</option>
                    <option value="dep_time-desc">出發時間 最晚 (晚➔早)</option>
                    <option value="duration-asc">行駛時間 最短 (快➔慢)</option>
                    <option value="duration-desc">行駛時間 最長 (慢➔快)</option>
                    <option value="transfers-asc">轉乘次數 最少 (少➔多)</option>
                </select>"""

new_primary_options = """                <select id="primarySort" class="sort-select" onchange="handleSortChange()">
                    <option value="arr_time-asc">抵達時間 最早 (早➔晚)</option>
                    <option value="arr_time-desc">抵達時間 最晚 (晚➔早)</option>
                    <option value="dep_time-asc">出發時間 最早 (早➔晚)</option>
                    <option value="dep_time-desc">出發時間 最晚 (晚➔早)</option>
                    <option value="duration-asc">總行駛時間 最短 (快➔慢)</option>
                    <option value="pure_moving-asc">純車行時間 最短 (快➔慢)</option>
                    <option value="layover-asc">等車時間 最少 (少➔多)</option>
                    <option value="transfers-asc">轉乘次數 最少 (少➔多)</option>
                    <option value="duration-desc">總行駛時間 最長 (慢➔快)</option>
                </select>"""

html = html.replace(old_primary_options, new_primary_options, 1)

old_sec_options = """                <select id="secondarySort" class="sort-select" onchange="handleSortChange()">
                    <option value="duration-asc">行駛時間 最短</option>
                    <option value="transfers-asc">轉乘次數 最少</option>
                    <option value="dep_time-asc">出發時間 最早</option>
                    <option value="arr_time-asc">抵達時間 最早</option>
                </select>"""

new_sec_options = """                <select id="secondarySort" class="sort-select" onchange="handleSortChange()">
                    <option value="duration-asc">總行駛時間 最短</option>
                    <option value="pure_moving-asc">純車行時間 最短</option>
                    <option value="layover-asc">等車時間 最少</option>
                    <option value="transfers-asc">轉乘次數 最少</option>
                    <option value="dep_time-asc">出發時間 最早</option>
                    <option value="arr_time-asc">抵達時間 最早</option>
                </select>"""

html = html.replace(old_sec_options, new_sec_options, 1)

# 2. Update getFieldVal inside sortRoutes in JS
old_get_field = """            function getFieldVal(item, key) {
                if (key === 'arr_time') return timeToMin(item.arr_time);
                if (key === 'dep_time') return timeToMin(item.dep_time);
                if (key === 'duration') return item.duration;
                if (key === 'transfers') return item.transfers;
                if (key === 'train_no') return item.legs[0].train_number;
                return 0;
            }"""

new_get_field = """            function getFieldVal(item, key) {
                if (key === 'arr_time') return timeToMin(item.arr_time);
                if (key === 'dep_time') return timeToMin(item.dep_time);
                if (key === 'duration') return item.duration;
                if (key === 'transfers') return item.transfers;
                if (key === 'train_no') return item.legs[0].train_number;
                if (key === 'layover') {
                    return item.legs.reduce((sum, l) => sum + (l.layover || 0), 0);
                }
                if (key === 'pure_moving') {
                    const totalLayover = item.legs.reduce((sum, l) => sum + (l.layover || 0), 0);
                    return item.duration - totalLayover;
                }
                return 0;
            }"""

html = html.replace(old_get_field, new_get_field, 1)

# 3. Bump version to v3.5.0 (SemVer Minor: New Custom Transit Sort Metrics: Pure Moving Time & Layover Duration)
html = html.replace('v3.4.0 (2026.07.01版)', 'v3.5.0 (2026.07.01版)')
html = html.replace('核心版本: v3.4.0', '核心版本: v3.5.0 (新增純車行時間最短 & 等車時間最少自訂排序指標)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Added Pure Moving Time & Layover Duration sorting metrics and bumped to v3.5.0!")
