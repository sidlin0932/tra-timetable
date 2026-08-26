# -*- coding: utf-8 -*-
import os

html_path = 'f:/Antigravity/台鐵時刻表0701/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

split_tag = '<script src="data.js'
if split_tag not in content:
    raise Exception("split_tag not found")

html_head_and_body = content.split(split_tag)[0]

full_script = """<script src="data.js?v=20260701_v385"></script>
    <script>
        let allTimetableData = window.EMBEDDED_TIMETABLE_DATA || [];
        let departuresByStation = {};
        let currentRoutes = [];
        let currentModalTarget = 'waypoint-0';
        let transferCondition = 'all'; // 'all' | 'transfer_only' | 'max2' | 'max1' | 'direct'
        let typeFilter = 'all';
        let currentDayFilter = 'today'; // 'today' | '1' | '2' | '3' | '4' | '5' | '6' | '0' | 'all'
        let activeSortColumn = 'arr_time';
        let activeSortDir = 'asc';
        let debounceTimer = null;

        let waypoints = [
            { station: '板橋', minStay: 0 },
            { station: '台北', minStay: 0 }
        ];

        // Train service days mapping for weekday/weekend operating patterns
        const TRAIN_SERVICE_DAYS = {
            // Weekday-only (Mon-Fri: 1, 2, 3, 4, 5)
            '4006': [1,2,3,4,5], '1120': [1,2,3,4,5], '1130': [1,2,3,4,5], '1008': [1,2,3,4,5],
            '1140': [1,2,3,4,5], '1004': [1,2,3,4,5], '1180': [1,2,3,4,5], '1182': [1,2,3,4,5],
            '1036': [1,2,3,4,5], '4022': [1,2,3,4,5], '2114': [1,2,3,4,5], '2120': [1,2,3,4,5],
            '2124': [1,2,3,4,5], '2134': [1,2,3,4,5], '2144': [1,2,3,4,5], '2154': [1,2,3,4,5],
            '2174': [1,2,3,4,5], '2184': [1,2,3,4,5], '2194': [1,2,3,4,5], '2204': [1,2,3,4,5],
            '2214': [1,2,3,4,5], '2224': [1,2,3,4,5], '2234': [1,2,3,4,5], '2244': [1,2,3,4,5],
            '2254': [1,2,3,4,5], '2264': [1,2,3,4,5], '2274': [1,2,3,4,5],
            // Weekend/Holiday-only (Sat-Sun: 6, 0)
            '4008': [6,0], '2008': [6,0], '2504': [6,0], '2522': [6,0], '1006': [6,0],
            '2538': [6,0], '2542': [6,0], '1038': [6,0], '2554': [6,0], '2046': [6,0],
            '1048': [6,0], '4046': [6,0],
            // Friday only
            '199': [5],
            // Friday & Sunday extra
            '161': [5,0], '280': [5,0], '127': [5,0], '135': [5,0], '143': [5,0]
        };

        function getTrainServiceInfo(trainNo) {
            const days = TRAIN_SERVICE_DAYS[trainNo];
            if (!days) {
                return { isDaily: true, label: '🟢 每日行駛', days: [0,1,2,3,4,5,6] };
            }
            if (days.length === 5 && days.includes(1) && days.includes(5)) {
                return { isDaily: false, label: '💼 平日行駛 (週一至五)', days };
            }
            if (days.length === 2 && days.includes(6) && days.includes(0)) {
                return { isDaily: false, label: '🏖️ 假日行駛 (週六日/例假日)', days };
            }
            if (days.length === 1 && days.includes(5)) {
                return { isDaily: false, label: '⚡ 逢週五行駛', days };
            }
            if (days.length === 2 && days.includes(5) && days.includes(0)) {
                return { isDaily: false, label: '⚡ 逢週五、日行駛', days };
            }
            return { isDaily: false, label: `📅 逢週${days.map(d=>d===0?'日':d).join('、')}行駛`, days };
        }

        function getSelectedDayOfWeek() {
            if (currentDayFilter === 'all') return -1;
            if (currentDayFilter === 'today') {
                return new Date().getDay(); // 0=Sun, 1=Mon, ..., 6=Sat
            }
            return parseInt(currentDayFilter, 10);
        }

        function isTrainRunningOnSelectedDay(trainNo) {
            const targetDay = getSelectedDayOfWeek();
            if (targetDay === -1) return true;
            const info = getTrainServiceInfo(trainNo);
            return info.days.includes(targetDay);
        }

        function setDayFilter(day, btn) {
            currentDayFilter = day;
            const btns = document.querySelectorAll('#dayFilter .day-btn');
            btns.forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            executeSearch();
        }

        function initDayFilterDisplay() {
            const dayNames = ['週日', '週一', '週二', '週三', '週四', '週五', '週六'];
            const todayIdx = new Date().getDay();
            const el = document.getElementById('todayDayName');
            if (el) el.textContent = dayNames[todayIdx];
        }

        // Grouped by Taiwan County / City (全台 17 縣市精確劃分)
        const COUNTY_GROUPS = [
            {
                county: '基隆市',
                stations: ['基隆', '三坑', '八堵', '七堵', '百福', '暖暖', '海科館', '八斗子']
            },
            {
                county: '台北市',
                stations: ['南港', '松山', '台北', '萬華']
            },
            {
                county: '新北市',
                stations: ['五堵', '汐止', '汐科', '板橋', '浮洲', '樹林', '南樹林', '山佳', '鶯歌', '鳳鳴', '四腳亭', '瑞芳', '猴硐', '三貂嶺', '牡丹', '雙溪', '貢寮', '福隆', '大華', '十分', '望古', '嶺腳', '平溪', '菁桐']
            },
            {
                county: '桃園市',
                stations: ['桃園', '內壢', '中壢', '埔心', '楊梅', '富岡', '新富']
            },
            {
                county: '新竹縣市',
                stations: ['北湖', '湖口', '新豐', '竹北', '北新竹', '新竹', '三姓橋', '香山', '千甲', '新莊', '竹中', '六家', '上員', '榮華', '竹東', '橫山', '九讚頭', '合興', '富貴', '內灣']
            },
            {
                county: '苗栗縣',
                stations: ['崎頂', '竹南', '談文', '造橋', '大山', '後龍', '豐富', '苗栗', '龍港', '南勢', '白沙屯', '銅鑼', '新埔', '通霄', '三義', '苑裡']
            },
            {
                county: '台中市',
                stations: ['日南', '大甲', '泰安', '后里', '台中港', '清水', '豐原', '栗林', '潭子', '頭家厝', '松竹', '太原', '精武', '台中', '五權', '大慶', '沙鹿', '龍井', '大肚', '追分', '烏日', '新烏日', '成功']
            },
            {
                county: '彰化縣',
                stations: ['彰化', '花壇', '大村', '員林', '永靖', '社頭', '田中', '二水', '源泉']
            },
            {
                county: '南投縣',
                stations: ['濁水', '龍泉', '集集', '水里', '車埕']
            },
            {
                county: '雲林縣',
                stations: ['林內', '石榴', '斗六', '斗南', '石龜']
            },
            {
                county: '嘉義縣市',
                stations: ['大林', '民雄', '嘉北', '嘉義', '水上', '南靖']
            },
            {
                county: '台南市',
                stations: ['後壁', '新營', '柳營', '林鳳營', '隆田', '拔林', '善化', '南科', '新市', '永康', '大橋', '台南', '保安', '仁德', '中洲', '長榮大學', '沙崙']
            },
            {
                county: '高雄市',
                stations: ['大湖', '路竹', '岡山', '橋頭', '楠梓', '新左營', '左營', '內惟', '美術館', '鼓山', '三塊厝', '高雄', '民族', '科工館', '正義', '鳳山', '後庄', '九曲堂']
            },
            {
                county: '屏東縣',
                stations: ['六塊厝', '屏東', '歸來', '麟洛', '西勢', '竹田', '潮州', '崁頂', '南州', '鎮安', '林邊', '佳冬', '東海', '枋寮', '加祿', '內獅', '枋山']
            },
            {
                county: '宜蘭縣',
                stations: ['石城', '大里', '大溪', '龜山', '外澳', '頭城', '頂埔', '礁溪', '四城', '宜蘭', '二結', '中里', '羅東', '冬山', '新馬', '蘇澳新', '蘇澳', '永樂', '東澳', '南澳', '武塔', '漢本']
            },
            {
                county: '花蓮縣',
                stations: ['和平', '和仁', '崇德', '新城(太魯閣)', '景美', '北埔', '花蓮', '吉安', '志學', '平和', '壽豐', '豐田', '林榮新光', '南平', '鳳林', '萬榮', '光復', '大富', '富源', '瑞穗', '三民', '玉里', '東里', '東竹', '富里']
            },
            {
                county: '台東縣',
                stations: ['池上', '海端', '關山', '月美', '瑞和', '瑞源', '鹿野', '山里', '台東', '康樂', '知本', '太麻里', '金崙', '瀧溪', '大武']
            }
        ];

        const BRANCH_LINE_STATIONS = new Set([
            '海科館', '八斗子', '大華', '十分', '望古', '嶺腳', '平溪', '菁桐',
            '千甲', '新莊', '竹中', '六家', '上員', '榮華', '竹東', '橫山', '九讚頭', '合興', '富貴', '內灣',
            '濁水', '龍泉', '集集', '水里', '車埕',
            '長榮大學', '沙崙'
        ]);

        const EXPRESS_MAJOR_STATIONS = new Set([
            '基隆', '七堵', '八堵', '南港', '松山', '台北', '萬華', '板橋', '樹林', '鶯歌',
            '桃園', '中壢', '楊梅', '新竹', '竹南', '苗栗', '豐原', '台中', '新烏日', '彰化',
            '員林', '田中', '斗六', '斗南', '嘉義', '新營', '善化', '台南', '新左營', '高雄',
            '鳳山', '屏東', '潮州', '枋寮', '頭城', '礁溪', '宜蘭', '羅東', '蘇澳新', '東澳',
            '南澳', '新城(太魯閣)', '花蓮', '吉安', '壽豐', '鳳林', '光復', '瑞穗', '玉里',
            '池上', '關山', '鹿野', '台東', '知本', '太麻里', '大武'
        ]);

        const KEY_HUBS = new Set([
            '基隆', '八堵', '七堵', '南港', '松山', '台北', '板橋', '樹林', '桃園', '中壢',
            '新竹', '竹南', '苗栗', '豐原', '台中', '彰化', '員林', '田中', '二水', '斗六',
            '嘉義', '新營', '善化', '台南', '新左營', '高雄', '鳳山', '屏東', '潮州', '枋寮',
            '瑞芳', '雙溪', '福隆', '頭城', '礁溪', '宜蘭', '羅東', '蘇澳新', '東澳', '南澳',
            '新城(太魯閣)', '花蓮', '壽豐', '鳳林', '光復', '瑞穗', '玉里', '池上', '關山', '台東',
            '知本', '枋山', '竹中', '濁水'
        ]);

        const ALL_STATIONS = [];
        COUNTY_GROUPS.forEach(g => {
            g.stations.forEach(st => {
                if (!ALL_STATIONS.includes(st)) ALL_STATIONS.push(st);
            });
        });

        function timeToMin(tStr) {
            if (!tStr) return 0;
            const [h, m] = tStr.split(':').map(Number);
            return h * 60 + m;
        }

        function minToDuration(min) {
            if (min < 0) min += 1440;
            const h = Math.floor(min / 60);
            const m = min % 60;
            if (h === 0) return `${m} 分鐘`;
            return `${h} 小時 ${m > 0 ? m + ' 分' : ''}`;
        }

        window.addEventListener('DOMContentLoaded', () => {
            initDayFilterDisplay();
            renderWaypointsUI();
            if (allTimetableData.length > 0) {
                buildDeparturesIndex();
                executeSearch();
            } else {
                fetch('full_network_timetable.json')
                    .then(res => res.json())
                    .then(data => {
                        allTimetableData = data;
                        buildDeparturesIndex();
                        executeSearch();
                    })
                    .catch(err => {
                        console.error('Failed to load JSON timetable:', err);
                    });
            }
        });

        function buildDeparturesIndex() {
            departuresByStation = {};
            allTimetableData.forEach(t => {
                t.stops.forEach((s, sIdx) => {
                    if (sIdx < t.stops.length - 1) {
                        if (!departuresByStation[s.station]) departuresByStation[s.station] = [];
                        departuresByStation[s.station].push({
                            train: t,
                            stopIdx: sIdx,
                            depTimeMin: timeToMin(s.time)
                        });
                    }
                });
            });

            for (let st in departuresByStation) {
                departuresByStation[st].sort((a, b) => a.depTimeMin - b.depTimeMin);
            }
        }

        function isTrainAllowed(t) {
            if (!isTrainRunningOnSelectedDay(t.train_number)) return false;
            if (typeFilter === 'trpass' && !t.is_trpass) return false;
            if (typeFilter === 'express' && !['自強號', '新自強(EMU3000)', '普悠瑪', '太魯閣', '莒光號'].includes(t.train_type)) return false;
            if (typeFilter === 'local' && !['區間車', '區間快'].includes(t.train_type)) return false;
            return true;
        }

        // ==========================================
        // Google Maps Multi-Stop Waypoint UI Management
        // ==========================================
        function renderWaypointsUI() {
            const listEl = document.getElementById('waypointsList');
            if (!listEl) return;
            const countBadge = document.getElementById('waypointsCountBadge');
            if (countBadge) {
                const letters = waypoints.map((_, i) => String.fromCharCode(65 + i)).join(' ➔ ');
                countBadge.textContent = `${waypoints.length} 個站點 (${letters})`;
            }

            const viaBlock = document.getElementById('viaGroupBlock');
            if (viaBlock) {
                viaBlock.style.display = (waypoints.length === 2) ? 'block' : 'none';
            }

            listEl.innerHTML = waypoints.map((wp, idx) => {
                const letter = String.fromCharCode(65 + idx);
                const isFirst = idx === 0;
                const isLast = idx === waypoints.length - 1;
                const badgeClass = isFirst ? 'origin' : (isLast ? 'dest' : 'via');
                const roleLabel = isFirst ? '起點' : (isLast ? '終點' : '中途站');

                let stayHtml = '';
                if (!isFirst) {
                    stayHtml = `
                        <div class="waypoint-stay-group">
                            <span class="waypoint-stay-label">☕ 停留:</span>
                            <select class="waypoint-stay-select" onchange="updateWaypointStay(${idx}, this.value)">
                                <option value="0" ${wp.minStay == 0 ? 'selected' : ''}>順暢接駁 (最快/同車續搭)</option>
                                <option value="15" ${wp.minStay == 15 ? 'selected' : ''}>停留 15 分</option>
                                <option value="30" ${wp.minStay == 30 ? 'selected' : ''}>停留 30 分</option>
                                <option value="60" ${wp.minStay == 60 ? 'selected' : ''}>停留 1 小時</option>
                                <option value="90" ${wp.minStay == 90 ? 'selected' : ''}>停留 1.5 小時</option>
                                <option value="120" ${wp.minStay == 120 ? 'selected' : ''}>停留 2 小時</option>
                                <option value="180" ${wp.minStay == 180 ? 'selected' : ''}>停留 3 小時</option>
                            </select>
                        </div>
                    `;
                }

                return `
                    <div class="waypoint-item">
                        <div class="waypoint-letter-badge ${badgeClass}" title="${roleLabel}">${letter}</div>
                        <div class="waypoint-input-wrapper">
                            <input type="text" id="wpInput-${idx}" class="waypoint-station-input" value="${wp.station}" placeholder="輸入 ${roleLabel} 站名..." autocomplete="off" oninput="handleWaypointInput(${idx}, this.value)">
                            <button class="btn-waypoint-picker" onclick="openStationModal('waypoint-${idx}')">🗺️ 選站</button>
                            <div class="autocomplete-list" id="wpAutoList-${idx}"></div>
                        </div>
                        ${stayHtml}
                        <div class="waypoint-actions">
                            <button class="btn-waypoint-action" onclick="moveWaypoint(${idx}, -1)" ${isFirst ? 'disabled' : ''} title="向上移動">↑</button>
                            <button class="btn-waypoint-action" onclick="moveWaypoint(${idx}, 1)" ${isLast ? 'disabled' : ''} title="向下移動">↓</button>
                            <button class="btn-waypoint-action btn-waypoint-delete" onclick="removeWaypoint(${idx})" ${waypoints.length <= 2 ? 'disabled' : ''} title="刪除此停靠站">✕</button>
                        </div>
                    </div>
                `;
            }).join('');

            setupWaypointAutocompletes();
        }

        function setupWaypointAutocompletes() {
            waypoints.forEach((_, idx) => {
                const input = document.getElementById(`wpInput-${idx}`);
                const list = document.getElementById(`wpAutoList-${idx}`);
                if (!input || !list) return;

                input.addEventListener('input', () => {
                    const query = input.value.trim().toLowerCase();
                    if (!query) {
                        list.style.display = 'none';
                        return;
                    }
                    const matches = ALL_STATIONS.filter(st => st.toLowerCase().includes(query)).slice(0, 8);
                    if (matches.length > 0) {
                        list.innerHTML = matches.map(st => `
                            <div class="autocomplete-item" onclick="selectWaypointStation(${idx}, '${st}')">
                                <span>${st}</span>
                                <span class="autocomplete-line-tag">台鐵車站</span>
                            </div>
                        `).join('');
                        list.style.display = 'block';
                    } else {
                        list.style.display = 'none';
                    }
                });

                document.addEventListener('click', (e) => {
                    if (!input.contains(e.target) && !list.contains(e.target)) {
                        list.style.display = 'none';
                    }
                });
            });

            const viaInput = document.getElementById('viaInput');
            const viaList = document.getElementById('viaAutoList');
            if (viaInput && viaList) {
                viaInput.addEventListener('input', () => {
                    const query = viaInput.value.trim().toLowerCase();
                    if (!query) {
                        viaList.style.display = 'none';
                        return;
                    }
                    const matches = ALL_STATIONS.filter(st => st.toLowerCase().includes(query)).slice(0, 8);
                    if (matches.length > 0) {
                        viaList.innerHTML = matches.map(st => `
                            <div class="autocomplete-item" onclick="selectViaStation('${st}')">
                                <span>${st}</span>
                                <span class="autocomplete-line-tag">台鐵車站</span>
                            </div>
                        `).join('');
                        viaList.style.display = 'block';
                    } else {
                        viaList.style.display = 'none';
                    }
                });

                document.addEventListener('click', (e) => {
                    if (!viaInput.contains(e.target) && !viaList.contains(e.target)) {
                        viaList.style.display = 'none';
                    }
                });
            }
        }

        function handleWaypointInput(idx, val) {
            if (waypoints[idx]) {
                waypoints[idx].station = val.trim();
            }
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                executeSearch();
            }, 250);
        }

        function selectWaypointStation(idx, st) {
            if (waypoints[idx]) {
                waypoints[idx].station = st;
            }
            const list = document.getElementById(`wpAutoList-${idx}`);
            if (list) list.style.display = 'none';
            renderWaypointsUI();
            executeSearch();
        }

        function selectViaStation(st) {
            const input = document.getElementById('viaInput');
            if (input) input.value = st;
            const list = document.getElementById('viaAutoList');
            if (list) list.style.display = 'none';
            updateClearViaButton();
            executeSearch();
        }

        function updateWaypointStay(idx, val) {
            if (waypoints[idx]) {
                waypoints[idx].minStay = parseInt(val, 10) || 0;
            }
            executeSearch();
        }

        function addWaypoint() {
            if (waypoints.length >= 6) {
                alert('最多支援新增至 6 個中途停靠站點！');
                return;
            }
            const defaultHubs = ['潮州', '台東', '花蓮', '宜蘭', '台中', '彰化', '嘉義', '台南', '高雄'];
            const currentStations = new Set(waypoints.map(w => w.station));
            const nextSt = defaultHubs.find(h => !currentStations.has(h)) || '新竹';
            
            const last = waypoints.pop();
            waypoints.push({ station: nextSt, minStay: 0 });
            waypoints.push(last);
            renderWaypointsUI();
            executeSearch();
        }

        function removeWaypoint(idx) {
            if (waypoints.length <= 2) return;
            waypoints.splice(idx, 1);
            renderWaypointsUI();
            executeSearch();
        }

        function moveWaypoint(idx, dir) {
            const targetIdx = idx + dir;
            if (targetIdx < 0 || targetIdx >= waypoints.length) return;
            const temp = waypoints[idx];
            waypoints[idx] = waypoints[targetIdx];
            waypoints[targetIdx] = temp;
            renderWaypointsUI();
            executeSearch();
        }

        function reverseWaypoints() {
            waypoints.reverse();
            renderWaypointsUI();
            executeSearch();
        }

        function quickFillWaypoint(target, st) {
            if (target === 'dest') {
                waypoints[waypoints.length - 1].station = st;
            } else if (typeof target === 'number' && waypoints[target]) {
                waypoints[target].station = st;
            }
            renderWaypointsUI();
            executeSearch();
        }

        // ==========================================
        // Single-Leg & Chained Multi-Leg Routing Core
        // ==========================================
        function getDirectLegTrains(orig, dest, startTimeMin) {
            const origDeps = departuresByStation[orig] || [];
            const results = [];

            origDeps.forEach(firstDep => {
                if (firstDep.depTimeMin < startTimeMin) return;
                if (!isTrainAllowed(firstDep.train)) return;

                const train1 = firstDep.train;
                for (let j = firstDep.stopIdx + 1; j < train1.stops.length; j++) {
                    if (train1.stops[j].station === dest) {
                        const arrMin = timeToMin(train1.stops[j].time);
                        if (arrMin <= firstDep.depTimeMin) continue;

                        const leg1 = {
                            train_number: train1.train_number,
                            train_type: train1.train_type,
                            train_model: train1.train_model,
                            is_trpass: train1.is_trpass,
                            origin: train1.origin,
                            dest: train1.dest,
                            from: orig,
                            to: dest,
                            dep: train1.stops[firstDep.stopIdx].time,
                            arr: train1.stops[j].time,
                            layover: 0,
                            all_stops: train1.stops.slice(firstDep.stopIdx, j + 1)
                        };

                        results.push({
                            transfers: 0,
                            dep_time: leg1.dep,
                            arr_time: leg1.arr,
                            duration: arrMin - firstDep.depTimeMin,
                            is_trpass: leg1.is_trpass,
                            train_types: [leg1.train_type],
                            transfer_stations: [],
                            legs: [leg1]
                        });
                    }
                }
            });

            results.sort((a, b) => timeToMin(a.dep_time) - timeToMin(b.dep_time));
            return results;
        }

        function planRoutes(orig, dest, startTimeMin, viaStation = '') {
            if (!orig || !dest || orig === dest || allTimetableData.length === 0) {
                return [];
            }

            let maxAllowedTransfers = 4;
            if (transferCondition === 'direct') maxAllowedTransfers = 0;
            else if (transferCondition === 'max1') maxAllowedTransfers = 1;
            else if (transferCondition === 'max2') maxAllowedTransfers = 2;
            else if (transferCondition === 'all' || transferCondition === 'transfer_only') maxAllowedTransfers = 4;

            const origDeps = departuresByStation[orig] || [];
            const allResults = [];

            origDeps.forEach(firstDep => {
                if (firstDep.depTimeMin < startTimeMin) return;
                if (!isTrainAllowed(firstDep.train)) return;

                const train1 = firstDep.train;
                let queue = [];

                for (let j = firstDep.stopIdx + 1; j < train1.stops.length; j++) {
                    const nextSt = train1.stops[j].station;
                    const arrMin = timeToMin(train1.stops[j].time);
                    if (arrMin <= firstDep.depTimeMin) continue;

                    const leg1 = {
                        train_number: train1.train_number,
                        train_type: train1.train_type,
                        train_model: train1.train_model,
                        is_trpass: train1.is_trpass,
                        origin: train1.origin,
                        dest: train1.dest,
                        from: orig,
                        to: nextSt,
                        dep: train1.stops[firstDep.stopIdx].time,
                        arr: train1.stops[j].time,
                        layover: 0,
                        all_stops: train1.stops.slice(firstDep.stopIdx, j + 1)
                    };

                    if (nextSt === dest) {
                        allResults.push({
                            transfers: 0,
                            dep_time: leg1.dep,
                            arr_time: leg1.arr,
                            duration: arrMin - firstDep.depTimeMin,
                            is_trpass: leg1.is_trpass,
                            train_types: [leg1.train_type],
                            transfer_stations: [],
                            legs: [leg1]
                        });
                    } else if (maxAllowedTransfers > 0 && (KEY_HUBS.has(nextSt) || nextSt === viaStation || j === train1.stops.length - 1)) {
                        queue.push({
                            currentStation: nextSt,
                            currentTimeMin: arrMin,
                            legs: [leg1],
                            visited: new Set([orig, nextSt])
                        });
                    }
                }

                const bestAtStation = {};

                for (let hop = 1; hop <= maxAllowedTransfers; hop++) {
                    const nextQueue = [];
                    for (const state of queue) {
                        const deps = departuresByStation[state.currentStation] || [];
                        const minDep = state.currentTimeMin + 3;

                        for (const d of deps) {
                            if (d.depTimeMin < minDep) continue;
                            if (d.depTimeMin > minDep + 90) continue;
                            if (!isTrainAllowed(d.train)) continue;
                            if (d.train.train_number === state.legs[state.legs.length - 1].train_number) continue;

                            const train = d.train;
                            for (let j = d.stopIdx + 1; j < train.stops.length; j++) {
                                const nextSt = train.stops[j].station;
                                const arrMin = timeToMin(train.stops[j].time);
                                if (arrMin <= d.depTimeMin) continue;
                                if (state.visited.has(nextSt)) continue;

                                if (nextSt !== dest && !KEY_HUBS.has(nextSt) && nextSt !== viaStation && j !== train.stops.length - 1) continue;

                                const newLeg = {
                                    train_number: train.train_number,
                                    train_type: train.train_type,
                                    train_model: train.train_model,
                                    is_trpass: train.is_trpass,
                                    origin: train.origin,
                                    dest: train.dest,
                                    from: state.currentStation,
                                    to: nextSt,
                                    dep: train.stops[d.stopIdx].time,
                                    arr: train.stops[j].time,
                                    layover: d.depTimeMin - state.currentTimeMin,
                                    all_stops: train.stops.slice(d.stopIdx, j + 1)
                                };

                                const newLegs = [...state.legs, newLeg];

                                if (nextSt === dest) {
                                    allResults.push({
                                        transfers: newLegs.length - 1,
                                        dep_time: newLegs[0].dep,
                                        arr_time: newLeg.arr,
                                        duration: arrMin - timeToMin(newLegs[0].dep),
                                        is_trpass: newLegs.every(l => l.is_trpass),
                                        train_types: newLegs.map(l => l.train_type),
                                        transfer_stations: newLegs.slice(0, -1).map(l => l.to),
                                        legs: newLegs
                                    });
                                } else if (hop < maxAllowedTransfers) {
                                    if (!bestAtStation[nextSt] || arrMin < bestAtStation[nextSt]) {
                                        bestAtStation[nextSt] = arrMin;
                                        const nextVis = new Set(state.visited);
                                        nextVis.add(nextSt);
                                        nextQueue.push({
                                            currentStation: nextSt,
                                            currentTimeMin: arrMin,
                                            legs: newLegs,
                                            visited: nextVis
                                        });
                                    }
                                }
                            }
                        }
                    }
                    queue = nextQueue;
                    if (queue.length === 0) break;
                }
            });

            let filteredResults = allResults;

            if (viaStation) {
                filteredResults = filteredResults.filter(r => r.transfer_stations.includes(viaStation));
            } else if (transferCondition === 'direct') {
                filteredResults = filteredResults.filter(r => r.transfers === 0);
            } else if (transferCondition === 'transfer_only') {
                filteredResults = filteredResults.filter(r => r.transfers > 0);
            }

            if (typeFilter === 'mixed') {
                filteredResults = filteredResults.filter(r => r.legs.length > 1 && 
                    r.train_types.some(t => ['自強號', '新自強(EMU3000)', '普悠瑪', '太魯閣', '莒光號'].includes(t)) && 
                    r.train_types.some(t => ['區間車', '區間快'].includes(t))
                );
            } else if (typeFilter === 'trpass') {
                filteredResults = filteredResults.filter(r => r.is_trpass);
            } else if (typeFilter === 'express') {
                filteredResults = filteredResults.filter(r => r.train_types.every(t => ['自強號', '新自強(EMU3000)', '普悠瑪', '太魯閣', '莒光號'].includes(t)));
            } else if (typeFilter === 'local') {
                filteredResults = filteredResults.filter(r => r.train_types.every(t => ['區間車', '區間快'].includes(t)));
            }

            const seen = new Map();
            const uniqueResults = [];
            for (const r of filteredResults) {
                const key = `${r.dep_time}_${r.arr_time}_${r.train_types.join('+')}_${r.transfer_stations.join('>')}`;
                if (!seen.has(key)) {
                    seen.set(key, r);
                    uniqueResults.push(r);
                }
            }

            const groupedByFirstLeg = {};
            for (const r of uniqueResults) {
                if (r.transfers === 0) {
                    const key = `direct_${r.dep_time}_${r.legs[0].train_number}`;
                    if (!groupedByFirstLeg[key]) groupedByFirstLeg[key] = [];
                    groupedByFirstLeg[key].push(r);
                } else {
                    const firstTrain = r.legs[0].train_number;
                    const key = `trans_${firstTrain}_${r.dep_time}`;
                    if (!groupedByFirstLeg[key]) groupedByFirstLeg[key] = [];
                    groupedByFirstLeg[key].push(r);
                }
            }

            const finalResults = [];
            for (const [k, list] of Object.entries(groupedByFirstLeg)) {
                if (k.startsWith('direct_')) {
                    finalResults.push(...list);
                } else {
                    list.sort((a, b) => timeToMin(a.arr_time) - timeToMin(b.arr_time) || a.duration - b.duration);
                    finalResults.push(...list.slice(0, 3));
                }
            }

            finalResults.sort((a, b) => timeToMin(a.dep_time) - timeToMin(b.dep_time));
            return finalResults;
        }

        function planMultiStopRoutes(wps, startTimeMin) {
            if (wps.length < 2) return [];
            if (wps.length === 2) {
                const via = (document.getElementById('viaInput') && document.getElementById('viaInput').value) ? document.getElementById('viaInput').value.trim() : '';
                return planRoutes(wps[0].station, wps[1].station, startTimeMin, via);
            }

            // Step 1: Precompute leg tables
            // For multi-stop tours between hubs, get ALL direct trains across the full day; if none, fallback to planRoutes
            const legTables = [];
            for (let k = 0; k < wps.length - 1; k++) {
                const fSt = wps[k].station;
                const tSt = wps[k + 1].station;
                if (!fSt || !tSt || fSt === tSt) return [];

                const minT = (k === 0 ? startTimeMin : 0);
                let directs = getDirectLegTrains(fSt, tSt, minT);
                if (directs.length > 0) {
                    legTables.push(directs);
                } else {
                    const fallbackRoutes = planRoutes(fSt, tSt, minT, '');
                    if (fallbackRoutes.length === 0) return [];
                    legTables.push(fallbackRoutes);
                }
            }

            // Step 2: Chain legs efficiently in memory across the entire day
            let currentItineraries = legTables[0].map(r => ({
                legs: [...r.legs],
                stopovers: [],
                dep_time: r.dep_time,
                arr_time: r.arr_time,
                duration: r.duration,
                is_trpass: r.is_trpass,
                train_types: [...r.train_types],
                transfer_stations: [...r.transfer_stations]
            }));

            for (let i = 1; i < wps.length - 1; i++) {
                const fromSt = wps[i].station;
                const toSt = wps[i + 1].station;
                const minStay = wps[i].minStay || 0;
                const nextLegRoutes = legTables[i];
                const nextItineraries = [];

                for (const itin of currentItineraries) {
                    const arrM = timeToMin(itin.arr_time);
                    const lastLeg = itin.legs[itin.legs.length - 1];

                    // Option A: Direct through-ride check on the SAME train
                    if (minStay === 0) {
                        const trainObj = allTimetableData.find(t => t.train_number === lastLeg.train_number);
                        if (trainObj) {
                            const fIdx = trainObj.stops.findIndex(s => s.station === fromSt);
                            const tIdx = trainObj.stops.findIndex(s => s.station === toSt);
                            if (fIdx !== -1 && tIdx !== -1 && fIdx < tIdx) {
                                const throughArrTime = trainObj.stops[tIdx].time;
                                const throughArrM = timeToMin(throughArrTime);
                                if (throughArrM > arrM) {
                                    const throughLeg = {
                                        train_number: trainObj.train_number,
                                        train_type: trainObj.train_type,
                                        train_model: trainObj.train_model,
                                        is_trpass: trainObj.is_trpass,
                                        origin: trainObj.origin,
                                        dest: trainObj.dest,
                                        from: fromSt,
                                        to: toSt,
                                        dep: trainObj.stops[fIdx].time,
                                        arr: throughArrTime,
                                        layover: 0,
                                        is_through: true,
                                        all_stops: trainObj.stops.slice(fIdx, tIdx + 1)
                                    };

                                    nextItineraries.push({
                                        legs: [...itin.legs, throughLeg],
                                        stopovers: [...itin.stopovers, { station: fromSt, stayMin: 0, is_through: true }],
                                        dep_time: itin.dep_time,
                                        arr_time: throughArrTime,
                                        duration: throughArrM - timeToMin(itin.dep_time),
                                        is_trpass: itin.is_trpass && throughLeg.is_trpass,
                                        train_types: [...itin.train_types, throughLeg.train_type],
                                        transfer_stations: [...itin.transfer_stations]
                                    });
                                }
                            }
                        }
                    }

                    // Option B: Next train connection across the whole day
                    const earliestNextDepMin = arrM + (minStay > 0 ? (minStay + 3) : 3);
                    for (const nxt of nextLegRoutes) {
                        const nxtDepM = timeToMin(nxt.dep_time);
                        if (nxtDepM < earliestNextDepMin) continue;
                        const actualStayMin = nxtDepM - arrM;

                        const mergedLegs = [...itin.legs, ...nxt.legs];
                        const finalArrM = timeToMin(nxt.arr_time);
                        const startDepM = timeToMin(itin.dep_time);
                        if (finalArrM <= startDepM) continue;

                        nextItineraries.push({
                            legs: mergedLegs,
                            stopovers: [...itin.stopovers, { station: fromSt, stayMin: actualStayMin, is_through: false }],
                            dep_time: itin.dep_time,
                            arr_time: nxt.arr_time,
                            duration: finalArrM - startDepM,
                            is_trpass: itin.is_trpass && nxt.is_trpass,
                            train_types: [...itin.train_types, ...nxt.train_types],
                            transfer_stations: [...itin.transfer_stations, fromSt, ...nxt.transfer_stations]
                        });
                    }
                }

                if (nextItineraries.length === 0) return [];

                // Deduplicate
                const seenKeys = new Set();
                const deduped = [];
                for (const item of nextItineraries) {
                    const key = `${item.dep_time}_${item.arr_time}_${item.legs.map(l=>l.train_number).join('-')}`;
                    if (!seenKeys.has(key)) {
                        seenKeys.add(key);
                        deduped.push(item);
                    }
                }

                currentItineraries = deduped;
            }

            currentItineraries.forEach(itin => {
                let actualTransfers = 0;
                for (let k = 1; k < itin.legs.length; k++) {
                    if (itin.legs[k].train_number !== itin.legs[k - 1].train_number) {
                        actualTransfers++;
                    }
                }
                itin.transfers = actualTransfers;
            });

            return currentItineraries;
        }

        function sortRoutes(routes) {
            const primaryVal = document.getElementById('primarySort').value;
            const secondaryVal = document.getElementById('secondarySort').value;

            const [pKey, pDir] = primaryVal.split('-');
            const [sKey, sDir] = secondaryVal.split('-');

            function getFieldVal(item, key) {
                if (key === 'arr_time') return timeToMin(item.arr_time);
                if (key === 'dep_time') return timeToMin(item.dep_time);
                if (key === 'duration') return item.duration;
                if (key === 'transfers') return item.transfers;
                if (key === 'train_no') return item.legs[0].train_number;
                if (key === 'layover') {
                    const stopoverM = item.stopovers ? item.stopovers.reduce((s, st) => s + (st.is_through ? 0 : st.stayMin), 0) : 0;
                    return item.legs.reduce((sum, l) => sum + (l.layover || 0), 0) + stopoverM;
                }
                if (key === 'pure_moving') {
                    const totalLayover = item.legs.reduce((sum, l) => sum + (l.layover || 0), 0) + (item.stopovers ? item.stopovers.reduce((s, st) => s + (st.is_through ? 0 : st.stayMin), 0) : 0);
                    return item.duration - totalLayover;
                }
                return 0;
            }

            routes.sort((a, b) => {
                const valA1 = getFieldVal(a, pKey);
                const valB1 = getFieldVal(b, pKey);

                if (valA1 !== valB1) {
                    return pDir === 'asc' ? (valA1 > valB1 ? 1 : -1) : (valA1 < valB1 ? 1 : -1);
                }

                const valA2 = getFieldVal(a, sKey);
                const valB2 = getFieldVal(b, sKey);
                if (valA2 !== valB2) {
                    return sDir === 'asc' ? (valA2 > valB2 ? 1 : -1) : (valA2 < valB2 ? 1 : -1);
                }

                return a.transfers - b.transfers;
            });

            return routes;
        }

        function toggleColumnSort(columnKey) {
            if (activeSortColumn === columnKey) {
                activeSortDir = activeSortDir === 'asc' ? 'desc' : 'asc';
            } else {
                activeSortColumn = columnKey;
                activeSortDir = 'asc';
            }

            const primarySelect = document.getElementById('primarySort');
            const targetVal = `${columnKey}-${activeSortDir}`;
            let optionExists = false;
            for (let opt of primarySelect.options) {
                if (opt.value === targetVal) {
                    primarySelect.value = targetVal;
                    optionExists = true;
                    break;
                }
            }
            if (!optionExists) {
                const newOpt = new Option(`${columnKey} (${activeSortDir})`, targetVal);
                primarySelect.add(newOpt);
                primarySelect.value = targetVal;
            }

            updateSortHeaderIcons();
            handleSortChange();
        }

        function updateSortHeaderIcons() {
            const cols = ['train_no', 'dep_time', 'arr_time', 'duration', 'transfers'];
            cols.forEach(col => {
                const icon = document.getElementById(`sortIcon-${col}`);
                if (!icon) return;
                const th = icon.parentElement;
                if (col === activeSortColumn) {
                    th.classList.add('active');
                    icon.textContent = activeSortDir === 'asc' ? '▲' : '▼';
                } else {
                    th.classList.remove('active');
                    icon.textContent = '▲▼';
                }
            });
        }

        function handleSortChange() {
            const [pKey, pDir] = document.getElementById('primarySort').value.split('-');
            activeSortColumn = pKey;
            activeSortDir = pDir;
            updateSortHeaderIcons();

            currentRoutes = sortRoutes(currentRoutes);
            renderResults();
        }

        function executeSearch() {
            const timeStr = document.getElementById('timeInput') ? (document.getElementById('timeInput').value || '00:00') : '00:00';
            const startTimeMin = timeToMin(timeStr);
            const via = document.getElementById('viaInput') ? document.getElementById('viaInput').value.trim() : '';

            const routeStr = waypoints.map(w => w.station).join(' ➔ ');
            const summaryEl = document.getElementById('routeSummaryText');
            if (summaryEl) {
                if (waypoints.length === 2 && via) {
                    summaryEl.textContent = `${waypoints[0].station} ➔ [經由 ${via}] ➔ ${waypoints[1].station}`;
                } else {
                    summaryEl.textContent = routeStr;
                }
            }
            updateClearViaButton();

            let rawRoutes = [];
            if (waypoints.length === 2) {
                rawRoutes = planRoutes(waypoints[0].station, waypoints[1].station, startTimeMin, via);
            } else {
                rawRoutes = planMultiStopRoutes(waypoints, startTimeMin);
            }

            const seen = new Set();
            currentRoutes = rawRoutes.filter(r => {
                const key = `${r.dep_time}-${r.arr_time}-${r.transfers}-${r.legs.map(l=>l.train_number).join('_')}`;
                if (seen.has(key)) return false;
                seen.add(key);
                return true;
            });

            currentRoutes = sortRoutes(currentRoutes);
            renderResults();
        }

        function findBackupLeg(fromStation, toStation, currentDepTime) {
            const depMin = timeToMin(currentDepTime);
            const candidates = [];
            allTimetableData.forEach(t => {
                if (!isTrainRunningOnSelectedDay(t.train_number)) return;
                const fromStop = t.stops.find(s => s.station === fromStation);
                const toStop = t.stops.find(s => s.station === toStation);
                if (fromStop && toStop) {
                    const fIdx = t.stops.indexOf(fromStop);
                    const tIdx = t.stops.indexOf(toStop);
                    if (fIdx < tIdx) {
                        const tDep = timeToMin(fromStop.time);
                        if (tDep > depMin) {
                            candidates.push({
                                train_number: t.train_number,
                                train_type: t.train_type,
                                dep: fromStop.time,
                                arr: toStop.time,
                                depMin: tDep,
                                delayMin: tDep - depMin
                            });
                        }
                    }
                }
            });
            candidates.sort((a, b) => a.depMin - b.depMin);
            return candidates[0] || null;
        }

        function renderResults() {
            const container = document.getElementById('resultsList');
            const countBadge = document.getElementById('resultsCount');
            countBadge.textContent = `${currentRoutes.length} 個方案`;

            if (currentRoutes.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <h3>🔍 查無符合條件的列車乘車方案</h3>
                        <p>建議調整出發時間、搭乘星期、選擇「全部方案」或確認起訖站點是否正確。</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = currentRoutes.map((route, rIdx) => {
                const isDirect = route.transfers === 0;
                
                const totalLayoverMin = route.legs.reduce((sum, l) => sum + (l.layover || 0), 0) + (route.stopovers ? route.stopovers.reduce((s, st) => s + (st.is_through ? 0 : st.stayMin), 0) : 0);
                const pureMovingMin = route.duration - totalLayoverMin;

                const transferStationsWithLayovers = route.legs.slice(0, -1).map((leg, idx) => {
                    const nextLeg = route.legs[idx + 1];
                    if (nextLeg && nextLeg.is_through) {
                        return `<span class="transfer-hop-station">${leg.to}<span class="transfer-hop-wait normal" style="background:#ecfdf5; color:#059669; border-color:#a7f3d0;">🟢原車續乘</span></span>`;
                    }
                    const layoverM = (nextLeg && nextLeg.layover) ? nextLeg.layover : 0;
                    const isTight = layoverM > 0 && layoverM <= 15;
                    const badgeClass = isTight ? 'transfer-hop-wait tight' : 'transfer-hop-wait normal';
                    const waitIcon = isTight ? '⚡等' : '等';
                    const layoverStr = layoverM > 0 
                        ? `<span class="${badgeClass}">${waitIcon} ${layoverM}分</span>`
                        : '';
                    return `<span class="transfer-hop-station">${leg.to}${layoverStr}</span>`;
                }).join('<span style="color:var(--text-muted); margin:0 3px;">、</span>');

                const isMultiStop = waypoints.length > 2;

                const transferTagHtml = isDirect 
                    ? `<div class="transfer-tag transfer-direct">🟢 直達無須換車</div>`
                    : (isMultiStop
                        ? `<div class="transfer-tag transfer-hop">🗺️ 多站行程 (${route.legs.length}段列車 · 換車${route.transfers}次)</div>
                           <div style="font-size:0.75rem; color:var(--text-muted); margin-top:2px;">純車行 ${minToDuration(pureMovingMin)} · 總停留 ${totalLayoverMin}分</div>`
                        : `<div class="transfer-tag transfer-hop">🟠 轉乘 ${route.transfers} 次 (${transferStationsWithLayovers})</div>
                           <div style="font-size:0.75rem; color:var(--text-muted); margin-top:2px;">純車行 ${minToDuration(pureMovingMin)} · 總等車 ${totalLayoverMin}分</div>`
                      );

                const legsBadgesWithDuration = route.legs.map(l => {
                    const legDurationMin = timeToMin(l.arr) - timeToMin(l.dep);
                    const durStr = legDurationMin > 0 ? `<span style="font-size:0.75rem; opacity:0.85; margin-left:3px;">(${legDurationMin}分)</span>` : '';
                    return `<span style="display:inline-flex; align-items:center;">${getTrainTypeBadge(l.train_type, l.train_number, l.from, l.to)}${durStr}</span>`;
                }).join(' <span style="color:var(--text-muted); font-size:0.8rem; font-weight:700; margin:0 2px;">➔</span> ');

                const trPassBadge = route.is_trpass
                    ? `<span class="badge-trpass">✅ TR-PASS 適用</span>`
                    : `<span class="badge-not-trpass">⚠️ 部分列車禁用TR-PASS</span>`;

                const hasTightTransfer = route.legs.some(l => !l.is_through && l.layover > 0 && l.layover <= 15);
                const tightTransferBadge = hasTightTransfer 
                    ? `<span class="badge-tight-transfer">⚡ 含緊湊轉乘 · 附備案</span>`
                    : '';

                // Service day badges
                const trainServiceBadges = route.legs.map(l => {
                    const info = getTrainServiceInfo(l.train_number);
                    if (info.isDaily) return '';
                    const badgeClass = info.label.includes('平日') ? 'badge-service-weekday' : 'badge-service-weekend';
                    return `<span class="badge-service-day ${badgeClass}">${l.train_number}次: ${info.label}</span>`;
                }).filter(Boolean).join(' ');

                const itineraryHtml = route.legs.map((leg, legIdx) => {
                    let layoverAlert = '';
                    let planBHtml = '';

                    if (leg.is_through) {
                        layoverAlert = `<div class="layover-alert through" style="background:#f0fdf4; color:#166534; border:1px solid #bbf7d0; padding:8px 12px; border-radius:6px; margin-bottom:8px; font-size:0.85rem;">🟢 <strong>原車直通繼續行駛</strong> · 列車抵達 <strong>${leg.from}</strong> 站後繼續開往 <strong>${leg.to}</strong>，旅客留在原車即可。</div>`;
                    } else if (leg.layover) {
                        const isTight = leg.layover <= 15;
                        const alertClass = isTight ? 'layover-alert tight' : 'layover-alert';
                        const tightNotice = isTight ? ' <span style="color:#ef4444; font-weight:800;">(⚠️ 緊湊轉乘)</span>' : '';
                        layoverAlert = `<div class="${alertClass}">⏳ 在 <strong>${leg.from}</strong> 站轉乘，停留等候 <strong>${leg.layover} 分鐘</strong>${tightNotice}</div>`;

                        const backup = findBackupLeg(leg.from, leg.to, leg.dep);
                        if (backup) {
                            planBHtml = `
                                <div class="plan-b-card">
                                    <div class="plan-b-title">
                                        <span>🛡️ 萬一轉乘不及之【第二備案】：</span>
                                    </div>
                                    <div>
                                        下一班可搭乘 <strong>${backup.train_type} ${backup.train_number}</strong> (${leg.from} ${backup.dep} ➔ ${leg.to} ${backup.arr})，預估延後 <strong>${backup.delayMin} 分鐘</strong>抵達。
                                    </div>
                                </div>
                            `;
                        }
                    }

                    const serviceInfo = getTrainServiceInfo(leg.train_number);
                    const serviceNoteTag = !serviceInfo.isDaily 
                        ? `<span style="font-size:0.75rem; font-weight:700; color:var(--primary); margin-left:6px;">(${serviceInfo.label})</span>`
                        : '';

                    const stopsChips = leg.all_stops.map(s => 
                        `<span class="stop-chip clickable" onclick="openStationTimetable('${s.station}')" title="查看 ${s.station} 全日發車時刻表">${s.station} (${s.time})</span>`
                    ).join('');

                    return `
                        <div class="timeline-step">
                            <div class="timeline-dot ${legIdx > 0 ? (leg.is_through ? 'through' : 'transfer') : ''}"></div>
                            ${layoverAlert}
                            ${planBHtml}
                            <div class="leg-card">
                                <div class="leg-header">
                                    <div class="leg-route">
                                        第 ${legIdx + 1} 段：<span class="clickable-station" onclick="openStationTimetable('${leg.from}')">${leg.from}</span> (${leg.dep}) ➔ <span class="clickable-station" onclick="openStationTimetable('${leg.to}')">${leg.to}</span> (${leg.arr})
                                    </div>
                                    <div>
                                        ${getTrainTypeBadge(leg.train_type, leg.train_number, leg.from, leg.to)}
                                        ${serviceNoteTag}
                                        <span style="font-size:0.8rem; color:var(--text-muted); margin-left:6px;">(${leg.origin} 開往 ${leg.dest})</span>
                                    </div>
                                </div>
                                <div style="font-size:0.82rem; color:var(--text-muted); margin-top:6px;">
                                    沿途停靠 (${leg.all_stops.length} 站)：
                                </div>
                                <div class="all-stops-list">
                                    ${stopsChips}
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');

                return `
                    <div class="trip-card">
                        <div class="trip-header-row" onclick="toggleDetails(${rIdx})">
                            <div class="train-types-badges">
                                ${legsBadgesWithDuration}
                                ${trPassBadge}
                                ${tightTransferBadge}
                                ${trainServiceBadges}
                            </div>
                            <div>
                                <div class="time-display">${route.dep_time}</div>
                                <div class="time-st-label"><span class="clickable-station" onclick="event.stopPropagation(); openStationTimetable('${route.legs[0].from}')">${route.legs[0].from} 出發 📋</span></div>
                            </div>
                            <div>
                                <div class="time-display">${route.arr_time}</div>
                                <div class="time-st-label"><span class="clickable-station" onclick="event.stopPropagation(); openStationTimetable('${route.legs[route.legs.length-1].to}')">${route.legs[route.legs.length-1].to} 抵達 📋</span></div>
                            </div>
                            <div>
                                <div class="duration-display">${minToDuration(route.duration)}</div>
                            </div>
                            <div class="transfers-badge-group">
                                ${transferTagHtml}
                            </div>
                            <div class="btn-toggle-details">
                                <span id="toggleText-${rIdx}">展開行程</span> ▾
                            </div>
                        </div>
                        <div class="itinerary-details" id="details-${rIdx}">
                            <h4 style="font-size:0.95rem; font-weight:700; color:var(--text-main); margin-bottom:8px;">🗺️ 詳細乘車與轉乘動線</h4>
                            <div class="timeline">
                                ${itineraryHtml}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function getTrainTypeBadge(type, number, fromSt, toSt) {
            let badgeClass = 'badge-local';
            if (type.includes('新自強') || type.includes('3000')) badgeClass = 'badge-3000';
            else if (type.includes('自強') || type.includes('普悠瑪') || type.includes('太魯閣')) badgeClass = 'badge-express';
            else if (type.includes('莒光')) badgeClass = 'badge-chu';
            else if (type.includes('快')) badgeClass = 'badge-fastlocal';

            const fromArg = fromSt ? `'${fromSt}'` : "''";
            const toArg = toSt ? `'${toSt}'` : "''";

            return `<span class="train-badge clickable ${badgeClass}" onclick="event.stopPropagation(); openTrainTimetable('${number}', ${fromArg}, ${toArg})" title="點擊查看 ${type} ${number} 次全線停靠時刻表">${type} ${number} 🔍</span>`;
        }

        let currentStationDepList = [];
        let currentStationDepFilter = 'all';
        let activeModalZIndex = 1000;

        function bringModalToFront(modal) {
            if (!modal) return;
            activeModalZIndex += 2;
            modal.style.zIndex = activeModalZIndex;
        }

        function openStationTimetable(stationName) {
            const deps = [];
            allTimetableData.forEach(t => {
                const sIdx = t.stops.findIndex(s => s.station === stationName);
                if (sIdx !== -1 && sIdx < t.stops.length - 1) {
                    deps.push({
                        time: t.stops[sIdx].time,
                        timeMin: timeToMin(t.stops[sIdx].time),
                        train_number: t.train_number,
                        train_type: t.train_type,
                        train_model: t.train_model,
                        origin: t.origin,
                        dest: t.dest,
                        is_trpass: t.is_trpass,
                        line: t.line || '',
                        nextStation: t.stops[sIdx + 1].station
                    });
                }
            });

            deps.sort((a, b) => a.timeMin - b.timeMin);
            currentStationDepList = deps;

            document.getElementById('stationDepModalTitle').innerHTML = `📍 <strong>${stationName}</strong> 車站全日發車時刻表`;
            document.getElementById('stationDepModalSubtitle').textContent = `全日共收錄 ${deps.length} 班出發列車 · 依發車時間順序排列`;

            const filterBtns = document.querySelectorAll('#stationDepTypeFilter .segment-btn');
            filterBtns.forEach(b => b.classList.remove('active'));
            if (filterBtns[0]) filterBtns[0].classList.add('active');
            currentStationDepFilter = 'all';

            renderStationDepRows();
            const modal = document.getElementById('stationDeparturesModal');
            bringModalToFront(modal);
            modal.classList.add('open');
        }

        function filterStationDepTable(filterType, btn) {
            currentStationDepFilter = filterType;
            const filterBtns = document.querySelectorAll('#stationDepTypeFilter .segment-btn');
            filterBtns.forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            renderStationDepRows();
        }

        function renderStationDepRows() {
            const tbody = document.getElementById('stationDepModalBody');
            
            const filtered = currentStationDepList.filter(d => {
                if (currentStationDepFilter === 'trpass' && !d.is_trpass) return false;
                if (currentStationDepFilter === 'express' && !['自強號', '新自強(EMU3000)', '普悠瑪', '太魯閣', '莒光號'].includes(d.train_type)) return false;
                if (currentStationDepFilter === 'local' && !['區間車', '區間快'].includes(d.train_type)) return false;
                return true;
            });

            if (filtered.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:30px; color:var(--text-muted);">查無符合條件的發車班次</td></tr>`;
                return;
            }

            tbody.innerHTML = filtered.map((d, idx) => {
                const trBadge = d.is_trpass 
                    ? '<span class="badge-trpass">TR-PASS 適用</span>'
                    : '<span class="badge-not-trpass">不適用TR-PASS</span>';

                return `
                    <tr>
                        <td style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: var(--primary);">
                            ${d.time}
                        </td>
                        <td>
                            ${getTrainTypeBadge(d.train_type, d.train_number)}
                        </td>
                        <td>
                            <strong style="font-size: 1rem;">開往 <span class="clickable-station" onclick="openStationTimetable('${d.dest}')" title="查看 ${d.dest} 全日發車時刻表">${d.dest}</span></strong>
                            <span style="font-size: 0.78rem; color: var(--text-muted); display: block;">始發: <span class="clickable-station" onclick="openStationTimetable('${d.origin}')" title="查看 ${d.origin} 全日發車時刻表">${d.origin}</span></span>
                        </td>
                        <td style="color: var(--text-muted); font-size: 0.9rem;">
                            ➔ <span class="clickable-station" onclick="openStationTimetable('${d.nextStation}')" title="查看 ${d.nextStation} 全日發車時刻表">${d.nextStation}</span>
                        </td>
                        <td style="text-align: right;">
                            ${trBadge}
                        </td>
                    </tr>
                `;
            }).join('');
        }

        function closeStationDeparturesModal(e) {
            if (!e || e.target.id === 'stationDeparturesModal' || e.target.classList.contains('btn-modal-close')) {
                document.getElementById('stationDeparturesModal').classList.remove('open');
            }
        }

        function openTrainTimetable(trainNumber, highlightFrom, highlightTo) {
            const train = allTimetableData.find(t => t.train_number === trainNumber);
            if (!train) {
                alert('查無該列車時刻表');
                return;
            }

            const modal = document.getElementById('trainTimetableModal');
            const title = document.getElementById('trainModalTitle');
            const subtitle = document.getElementById('trainModalSubtitle');
            const body = document.getElementById('trainModalBody');

            title.innerHTML = `
                ${getTrainTypeBadge(train.train_type, train.train_number)}
                <span><span class="clickable-station" onclick="openStationTimetable('${train.origin}')" title="查看 ${train.origin} 全日發車時刻表">${train.origin}</span> ➔ <span class="clickable-station" onclick="openStationTimetable('${train.dest}')" title="查看 ${train.dest} 全日發車時刻表">${train.dest}</span></span>
            `;

            const trBadge = train.is_trpass 
                ? '<span class="badge-trpass" style="margin-left:6px;">✅ TR-PASS 適用</span>' 
                : '<span class="badge-not-trpass" style="margin-left:6px;">⚠️ 不適用TR-PASS</span>';

            subtitle.innerHTML = `
                <span>車種車型: <strong>${train.train_model || train.train_type}</strong> · 路線: <strong>${train.line || '台鐵本線'}</strong></span>
                ${trBadge}
            `;

            let inHighlightRange = false;
            body.innerHTML = train.stops.map((stop, sIdx) => {
                if (highlightFrom && stop.station === highlightFrom) inHighlightRange = true;

                const isHighlighted = inHighlightRange || stop.station === highlightFrom || stop.station === highlightTo;
                const rowClass = isHighlighted ? 'highlight-trip' : '';

                if (highlightTo && stop.station === highlightTo) inHighlightRange = false;

                return `
                    <tr class="${rowClass}">
                        <td><span class="station-dot-seq">${sIdx + 1}</span></td>
                        <td>
                            <strong style="font-size: 1.05rem;" class="clickable-station" onclick="openStationTimetable('${stop.station}')" title="查看 ${stop.station} 全日發車時刻表">${stop.station}</strong>
                            ${stop.station === train.origin ? `<span class="clickable-station" onclick="openStationTimetable('${train.origin}')" style="font-size:0.75rem; color:var(--primary); margin-left:4px;" title="查看 ${train.origin} 全日發車時刻表">[始發站]</span>` : ''}
                            ${stop.station === train.dest ? `<span class="clickable-station" onclick="openStationTimetable('${train.dest}')" style="font-size:0.75rem; color:var(--primary); margin-left:4px;" title="查看 ${train.dest} 全日發車時刻表">[終點站]</span>` : ''}
                        </td>
                        <td style="text-align: right; font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700;">
                            ${stop.time}
                        </td>
                    </tr>
                `;
            }).join('');

            bringModalToFront(modal);
            modal.classList.add('open');
        }

        function closeTrainModal(e) {
            if (!e || e.target.id === 'trainTimetableModal' || e.target.classList.contains('btn-modal-close')) {
                document.getElementById('trainTimetableModal').classList.remove('open');
            }
        }

        function toggleDetails(idx) {
            const panel = document.getElementById(`details-${idx}`);
            const text = document.getElementById(`toggleText-${idx}`);
            if (panel.classList.contains('open')) {
                panel.classList.remove('open');
                text.textContent = '展開行程';
            } else {
                panel.classList.add('open');
                text.textContent = '收合行程';
            }
        }

        function setCurrentTime() {
            const now = new Date();
            const h = String(now.getHours()).padStart(2, '0');
            const m = String(now.getMinutes()).padStart(2, '0');
            const timeInput = document.getElementById('timeInput');
            if (timeInput) timeInput.value = `${h}:${m}`;
            executeSearch();
        }

        function setTransferCondition(val, btn) {
            transferCondition = val;
            const btns = document.querySelectorAll('#transferFilter .segment-btn');
            btns.forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            executeSearch();
        }

        function setTypeFilter(val, btn) {
            typeFilter = val;
            const btns = document.querySelectorAll('#typeFilter .segment-btn');
            btns.forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            executeSearch();
        }

        function clearViaStation() {
            const input = document.getElementById('viaInput');
            if (input) input.value = '';
            updateClearViaButton();
            executeSearch();
        }

        function updateClearViaButton() {
            const viaVal = document.getElementById('viaInput') ? document.getElementById('viaInput').value.trim() : '';
            const btn = document.getElementById('btnClearVia');
            if (btn) btn.style.display = viaVal ? 'inline-block' : 'none';
        }

        let modalInitialTarget = 'waypoint-0';

        function openStationModal(type) {
            modalInitialTarget = type || 'waypoint-0';
            setModalTarget(type || 'waypoint-0');
            document.getElementById('modalSearchInput').value = '';
            renderStationModal();
            filterModalStations();
            const modal = document.getElementById('stationModal');
            bringModalToFront(modal);
            modal.classList.add('open');
        }

        function updateModalTripStepper() {
            const stepper = document.getElementById('modalTripStepper');
            if (!stepper) return;

            let buttonsHtml = waypoints.map((wp, idx) => {
                const letter = String.fromCharCode(65 + idx);
                const isFirst = idx === 0;
                const isLast = idx === waypoints.length - 1;
                const icon = isFirst ? '🚩' : (isLast ? '🏁' : '📍');
                const role = isFirst ? '出發' : (isLast ? '抵達' : `停靠 ${letter}`);
                const activeClass = currentModalTarget === `waypoint-${idx}` ? 'active' : '';

                return `
                    <button class="modal-step-btn ${activeClass}" id="modalStep-${idx}" onclick="setModalTarget('waypoint-${idx}')">
                        <span class="step-icon">${icon}</span>
                        <span class="step-label">${role}:</span>
                        <strong>${wp.station || '未選'}</strong>
                    </button>
                `;
            }).join('<span class="modal-step-arrow">➔</span>');

            if (waypoints.length === 2) {
                const viaVal = (document.getElementById('viaInput') && document.getElementById('viaInput').value.trim()) ? document.getElementById('viaInput').value.trim() : '不限';
                const activeVia = currentModalTarget === 'via' ? 'active' : '';
                buttonsHtml += `
                    <span class="modal-step-arrow" style="margin:0 4px; color:var(--text-muted);">|</span>
                    <button class="modal-step-btn ${activeVia}" id="modalStep-via" onclick="setModalTarget('via')">
                        <span class="step-icon">🔀</span>
                        <span class="step-label">指定轉乘:</span>
                        <strong>${viaVal}</strong>
                    </button>
                `;
            }

            stepper.innerHTML = buttonsHtml;
        }

        function setModalTarget(type) {
            currentModalTarget = type;
            updateModalTripStepper();

            if (type.startsWith('waypoint-')) {
                const idx = parseInt(type.replace('waypoint-', ''), 10);
                const letter = String.fromCharCode(65 + idx);
                if (idx === 0) {
                    document.getElementById('modalTitle').textContent = `🗺️ 第 1 步：請點選【${letter} 出發站】（選完自動跳下一站）`;
                } else if (idx === waypoints.length - 1) {
                    document.getElementById('modalTitle').textContent = `🗺️ 請點選【${letter} 最終抵達站】（點擊即選定完成）`;
                } else {
                    document.getElementById('modalTitle').textContent = `🗺️ 請點選【${letter} 中途停靠站】（點擊即選定跳下一站）`;
                }
            } else if (type === 'via') {
                document.getElementById('modalTitle').textContent = '🔀 請點選【指定轉乘站】（點擊即選定轉乘站）';
            }
        }

        function modalPickStation(st) {
            if (currentModalTarget.startsWith('waypoint-')) {
                const idx = parseInt(currentModalTarget.replace('waypoint-', ''), 10);
                if (waypoints[idx]) {
                    waypoints[idx].station = st;
                }
                renderWaypointsUI();

                if (idx < waypoints.length - 1) {
                    const nextIdx = idx + 1;
                    setModalTarget(`waypoint-${nextIdx}`);
                    document.getElementById('modalSearchInput').value = '';
                    filterModalStations();
                    const stationList = document.getElementById('modalStationList');
                    if (stationList) stationList.scrollTop = 0;
                } else {
                    document.getElementById('stationModal').classList.remove('open');
                    executeSearch();
                }
            } else if (currentModalTarget === 'via') {
                const viaInput = document.getElementById('viaInput');
                if (viaInput) viaInput.value = st;
                updateClearViaButton();
                document.getElementById('stationModal').classList.remove('open');
                executeSearch();
            }
        }

        function closeStationModal(e) {
            if (!e || e.target.id === 'stationModal' || e.target.classList.contains('btn-modal-close')) {
                document.getElementById('stationModal').classList.remove('open');
            }
        }

        function renderStationModal() {
            const tabsContainer = document.getElementById('modalCountyTabs');
            const body = document.getElementById('modalStationList');

            tabsContainer.innerHTML = COUNTY_GROUPS.map((group, idx) => `
                <a href="#county-${idx}" class="modal-tab-pill" onclick="scrollToCounty('county-${idx}', event)">${group.county}</a>
            `).join('');

            body.innerHTML = COUNTY_GROUPS.map((group, idx) => `
                <div class="county-section" id="county-${idx}">
                    <div class="county-section-title">📍 ${group.county} (${group.stations.length} 站)</div>
                    <div class="station-grid">
                        ${group.stations.map(st => {
                            const isHub = EXPRESS_MAJOR_STATIONS.has(st);
                            const isBranch = BRANCH_LINE_STATIONS.has(st);
                            
                            let btnClass = '';
                            let iconPrefix = '';
                            let titleTip = '';

                            if (isHub) {
                                btnClass = 'express-hub';
                                iconPrefix = '⭐ ';
                                titleTip = '自強號特快停靠核心大站';
                            } else if (isBranch) {
                                btnClass = 'branch-station';
                                iconPrefix = '🌿 ';
                                titleTip = '台鐵觀光支線車站 (平溪/深澳/內灣/六家/集集/沙崙線)';
                            }

                            return `<button class="station-btn ${btnClass}" onclick="modalPickStation('${st}')" title="${titleTip}">${iconPrefix}${st}</button>`;
                        }).join('')}
                    </div>
                </div>
            `).join('');
        }

        function scrollToCounty(id, e) {
            if (e) e.preventDefault();
            const el = document.getElementById(id);
            if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }

        function filterModalStations() {
            const query = (document.getElementById('modalSearchInput').value || '').trim().toLowerCase();
            const sections = document.querySelectorAll('.county-section');

            sections.forEach(sec => {
                const btns = sec.querySelectorAll('.station-btn');
                let hasMatch = false;
                btns.forEach(btn => {
                    const st = btn.textContent.toLowerCase();
                    if (!query || st.includes(query)) {
                        btn.style.display = 'block';
                        hasMatch = true;
                    } else {
                        btn.style.display = 'none';
                    }
                });
                sec.style.display = hasMatch ? 'block' : 'none';
            });
        }

        function toggleTheme() {
            const current = document.documentElement.getAttribute('data-theme');
            const target = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', target);
        }
    </script>
</body>
</html>
"""

new_content = html_head_and_body + full_script

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully injected v3.8.5 script into index.html!")
