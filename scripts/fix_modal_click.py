import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix openStationModal, setModalTarget and modalPickStation
clean_modal_js = """
        function openStationModal(type) {
            setModalTarget(type || 'origin');
            document.getElementById('modalSearchInput').value = '';
            renderStationModal();
            filterModalStations();
            document.getElementById('stationModal').classList.add('open');
        }

        function setModalTarget(type) {
            currentModalTarget = type;
            const origVal = document.getElementById('originInput').value || '未選擇';
            const destVal = document.getElementById('destInput').value || '未選擇';
            
            const origEl = document.getElementById('modalOriginVal');
            const destEl = document.getElementById('modalDestVal');
            if (origEl) origEl.textContent = origVal;
            if (destEl) destEl.textContent = destVal;

            const btnOrig = document.getElementById('modalStepOrigin');
            const btnDest = document.getElementById('modalStepDest');

            if (type === 'origin') {
                if (btnOrig) btnOrig.classList.add('active');
                if (btnDest) btnDest.classList.remove('active');
                document.getElementById('modalTitle').textContent = '🗺️ 第 1 步：請點選【出發站】';
            } else {
                if (btnOrig) btnOrig.classList.remove('active');
                if (btnDest) btnDest.classList.add('active');
                document.getElementById('modalTitle').textContent = '🗺️ 第 2 步：請點選【抵達站】';
            }
        }

        function modalPickStation(st) {
            if (currentModalTarget === 'origin') {
                document.getElementById('originInput').value = st;
                const origEl = document.getElementById('modalOriginVal');
                if (origEl) origEl.textContent = st;
                // Move to Destination selection
                setModalTarget('dest');
                document.getElementById('modalSearchInput').value = '';
                filterModalStations();
            } else {
                document.getElementById('destInput').value = st;
                const destEl = document.getElementById('modalDestVal');
                if (destEl) destEl.textContent = st;
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
        }
"""

old_open_block_start = html.find("function openStationModal(type) {")
old_open_block_end = html.find("function renderStationModal() {")

if old_open_block_start != -1 and old_open_block_end != -1:
    html = html[:old_open_block_start] + clean_modal_js + "\n        " + html[old_open_block_end:]

# Bump version to v3.0.1
html = html.replace('v3.0.0 (2026.07.01版)', 'v3.0.1 (2026.07.01版)')
html = html.replace('核心版本: v3.0.0', '核心版本: v3.0.1 (完美修復一站式選站點擊)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Fixed modalPickStation and updated index.html to v3.0.1!")
