import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Modal HTML to have 2-in-1 Step Selector
old_modal_header = """            <div class="modal-header">
                <h3 id="modalTitle">🗺️ 選擇車站（依縣市分類）</h3>
                <button class="btn-modal-close" onclick="closeStationModal()">&times;</button>
            </div>"""

new_modal_header = """            <div class="modal-header">
                <div>
                    <h3 id="modalTitle">🗺️ 快速選站（全台 17 縣市）</h3>
                    <div class="modal-trip-stepper" id="modalTripStepper">
                        <button class="modal-step-btn active" id="modalStepOrigin" onclick="setModalTarget('origin')">
                            <span class="step-icon">🚩</span>
                            <span class="step-label">出發站:</span>
                            <strong id="modalOriginVal">台北</strong>
                        </button>
                        <span class="modal-step-arrow">➔</span>
                        <button class="modal-step-btn" id="modalStepDest" onclick="setModalTarget('dest')">
                            <span class="step-icon">🏁</span>
                            <span class="step-label">抵達站:</span>
                            <strong id="modalDestVal">請選擇</strong>
                        </button>
                    </div>
                </div>
                <button class="btn-modal-close" onclick="closeStationModal()">&times;</button>
            </div>"""

html = html.replace(old_modal_header, new_modal_header, 1)

# 2. Add Quick Station Pills directly under the input boxes in query-panel
old_query_grid_end = """                <div class="form-group">
                    <label class="form-label" for="timeInput">🕒 出發時間</label>"""

new_quick_chips = """            <!-- Quick Hub Station Pills -->
            <div class="quick-hubs-bar">
                <span class="quick-hubs-title">⚡ 常用大站快捷：</span>
                <div class="quick-hubs-list">
                    <button class="quick-hub-btn" onclick="quickFillStation('origin', '台北')">🚩 台北</button>
                    <button class="quick-hub-btn" onclick="quickFillStation('origin', '板橋')">🚩 板橋</button>
                    <button class="quick-hub-btn" onclick="quickFillStation('origin', '新竹')">🚩 新竹</button>
                    <button class="quick-hub-btn" onclick="quickFillStation('origin', '台中')">🚩 台中</button>
                    <button class="quick-hub-btn" onclick="quickFillStation('dest', '瑞芳')">🏁 瑞芳</button>
                    <button class="quick-hub-btn" onclick="quickFillStation('dest', '八斗子')">🏁 八斗子</button>
                    <button class="quick-hub-btn" onclick="quickFillStation('dest', '花蓮')">🏁 花蓮</button>
                    <button class="quick-hub-btn" onclick="quickFillStation('dest', '台東')">🏁 台東</button>
                    <button class="quick-hub-btn" onclick="quickFillStation('dest', '內灣')">🏁 內灣</button>
                    <button class="quick-hub-btn" onclick="quickFillStation('dest', '高雄')">🏁 高雄</button>
                </div>
            </div>

            <div class="query-grid">
                <div class="form-group">
                    <label class="form-label" for="timeInput">🕒 出發時間</label>"""

html = html.replace("""                <div class="form-group">
                    <label class="form-label" for="timeInput">🕒 出發時間</label>""", new_quick_chips, 1)

# 3. Add CSS for Stepper and Quick Hubs
stepper_css = """
        .quick-hubs-bar {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 16px;
            padding: 8px 12px;
            background: var(--bg-subtle);
            border-radius: 8px;
            flex-wrap: wrap;
        }
        .quick-hubs-title {
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--text-muted);
        }
        .quick-hubs-list {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }
        .quick-hub-btn {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            font-size: 0.78rem;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 16px;
            cursor: pointer;
            transition: all 0.15s;
        }
        .quick-hub-btn:hover {
            border-color: var(--primary);
            color: var(--primary);
            background: var(--primary-light);
        }

        .modal-trip-stepper {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 8px;
        }
        .modal-step-btn {
            background: var(--bg-subtle);
            border: 1.5px solid var(--border-color);
            padding: 6px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.85rem;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            color: var(--text-muted);
            transition: all 0.2s;
        }
        .modal-step-btn.active {
            background: var(--primary-light);
            border-color: var(--primary);
            color: var(--primary);
            font-weight: 700;
            box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.2);
        }
        .modal-step-arrow {
            color: var(--text-muted);
            font-weight: 700;
        }
"""

html = html.replace("</style>", stepper_css + "\n    </style>", 1)

# 4. Update openStationModal and modalPickStation in JS for 2-in-1 flow
old_modal_js = """        function openStationModal(type) {
            currentModalTarget = type;
            document.getElementById('modalTitle').textContent = `🗺️ 選擇${type === 'origin' ? '出發' : '抵達'}車站（依縣市分類）`;
            document.getElementById('modalSearchInput').value = '';
            renderStationModal(); // Force fresh render on open
            filterModalStations();
            document.getElementById('stationModal').classList.add('open');
        }

        function closeStationModal(e) {
            if (!e || e.target.id === 'stationModal' || e.target.classList.contains('btn-modal-close')) {
                document.getElementById('stationModal').classList.remove('open');
            }
        }"""

new_modal_js = """        function openStationModal(type) {
            setModalTarget(type);
            document.getElementById('modalSearchInput').value = '';
            renderStationModal();
            filterModalStations();
            document.getElementById('stationModal').classList.add('open');
        }

        function setModalTarget(type) {
            currentModalTarget = type;
            const origVal = document.getElementById('originInput').value || '未選擇';
            const destVal = document.getElementById('destInput').value || '未選擇';
            
            document.getElementById('modalOriginVal').textContent = origVal;
            document.getElementById('modalDestVal').textContent = destVal;

            const btnOrig = document.getElementById('modalStepOrigin');
            const btnDest = document.getElementById('modalStepDest');

            if (type === 'origin') {
                btnOrig.classList.add('active');
                btnDest.classList.remove('active');
                document.getElementById('modalTitle').textContent = '🗺️ 第 1 步：請點擊選擇【出發站】';
            } else {
                btnOrig.classList.remove('active');
                btnDest.classList.add('active');
                document.getElementById('modalTitle').textContent = '🗺️ 第 2 步：請點擊選擇【抵達站】';
            }
        }

        function modalPickStation(st) {
            if (currentModalTarget === 'origin') {
                document.getElementById('originInput').value = st;
                document.getElementById('modalOriginVal').textContent = st;
                // Seamlessly advance to Step 2 (Destination selection) without closing!
                setModalTarget('dest');
                document.getElementById('modalSearchInput').value = '';
                filterModalStations();
            } else {
                document.getElementById('destInput').value = st;
                document.getElementById('modalDestVal').textContent = st;
                // Both stations picked! Close modal and execute search instantly
                document.getElementById('stationModal').classList.remove('open');
                executeSearch();
            }
        }

        function quickFillStation(target, st) {
            document.getElementById(`${target}Input`).value = st;
            executeSearch();
        }

        function closeStationModal(e) {
            if (!e || e.target.id === 'stationModal' || e.target.classList.contains('btn-modal-close')) {
                document.getElementById('stationModal').classList.remove('open');
            }
        }"""

html = html.replace(old_modal_js, new_modal_js, 1)

# 5. Remove redundant modalPickStation definition at the bottom if duplicate
old_dup_pick = """        function modalPickStation(st) {
            document.getElementById(`${currentModalTarget}Input`).value = st;
            document.getElementById('stationModal').classList.remove('open');
            executeSearch();
        }"""
html = html.replace(old_dup_pick, "", 1)

# 6. Bump version to v2.9.0
html = html.replace('v2.8.0 (2026.07.01版)', 'v2.9.0 (2026.07.01版)')
html = html.replace('核心版本: v2.8.0', '核心版本: v2.9.0 (一站式極速連續選站與常用大站快捷)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Applied 2-in-1 Seamless Station Picker and updated index.html to v2.9.0!")
