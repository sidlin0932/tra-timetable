# -*- coding: utf-8 -*-
import re

print("Optimizing station clicking and search execution to be instantaneous (<10ms)...")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Optimize executeSearch: remove artificial setInterval delay and render instantly
old_execute_search = """            // 3. Update Real Progress to 100% and Render smoothly
            let step = 0;
            const totalSteps = 6;
            const timer = setInterval(() => {
                step++;
                const count = Math.round((step / totalSteps) * totalTrains);
                updateRealProgress(count, totalTrains);
                if (step >= totalSteps) {
                    clearInterval(timer);
                    renderResults();
                }
            }, 25);"""

new_execute_search = """            // 3. Instant Render (0ms microsecond execution)
            renderResults();"""

html = html.replace(old_execute_search, new_execute_search)

# 2. Optimize openStationTimetable: use departuresByStation index for 0ms instantaneous modal opening
old_open_station = """        function openStationTimetable(stationName) {
            const deps = [];
            allTimetableData.forEach(t => {
                const sIdx = t.stops.findIndex(s => s.station === stationName);
                if (sIdx !== -1 && sIdx < t.stops.length - 1) {
                    const times = calculateArrivalAndDepTime(t, sIdx, stationName);
                    deps.push({
                        time: t.stops[sIdx].time,
                        timeMin: timeToMin(t.stops[sIdx].time),
                        arrTime: times.arrTime,
                        depTime: times.depTime,
                        dwellLabel: times.dwellLabel,
                        train_number: t.train_number,
                        train_type: t.train_type,
                        train_model: t.train_model,
                        origin: t.origin,
                        dest: t.dest,
                        route_dir: t.route_dir || '',
                        is_trpass: t.is_trpass,
                        line: t.line || '',
                        nextStation: t.stops[sIdx + 1].station
                    });
                }
            });

            deps.sort((a, b) => a.timeMin - b.timeMin);
            currentStationDepList = deps;"""

new_open_station = """        function openStationTimetable(stationName) {
            const indexedDeps = departuresByStation[stationName] || [];
            const deps = indexedDeps.map(d => {
                const t = d.train;
                const sIdx = d.stopIdx;
                const times = calculateArrivalAndDepTime(t, sIdx, stationName);
                return {
                    time: t.stops[sIdx].time,
                    timeMin: d.depTimeMin,
                    arrTime: times.arrTime,
                    depTime: times.depTime,
                    dwellLabel: times.dwellLabel,
                    train_number: t.train_number,
                    train_type: t.train_type,
                    train_model: t.train_model,
                    origin: t.origin,
                    dest: t.dest,
                    route_dir: t.route_dir || '',
                    is_trpass: t.is_trpass,
                    line: t.line || '',
                    nextStation: (sIdx < t.stops.length - 1) ? t.stops[sIdx + 1].station : ''
                };
            });

            currentStationDepList = deps;"""

html = html.replace(old_open_station, new_open_station)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html station clicking and search execution optimized successfully!")
