import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Update openStationModal, setModalTarget, modalPickStation with modalInitialTarget
perfect_flow_modal = """
        let modalInitialTarget = 'origin';

        function openStationModal(type) {
            modalInitialTarget = type || 'origin';
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
                document.getElementById('modalTitle').textContent = '🗺️ 第 1 步：請點選【出發站】（選完自動跳抵達站）';
            } else {
                if (btnOrig) btnOrig.classList.remove('active');
                if (btnDest) btnDest.classList.add('active');
                document.getElementById('modalTitle').textContent = '🗺️ 請點選【抵達站】（點擊即選定完成）';
            }
        }

        function modalPickStation(st) {
            if (currentModalTarget === 'origin') {
                document.getElementById('originInput').value = st;
                const origEl = document.getElementById('modalOriginVal');
                if (origEl) origEl.textContent = st;

                if (modalInitialTarget === 'origin') {
                    // Started from Origin: Seamlessly advance to Destination selection!
                    setModalTarget('dest');
                    document.getElementById('modalSearchInput').value = '';
                    filterModalStations();
                } else {
                    document.getElementById('stationModal').classList.remove('open');
                    executeSearch();
                }
            } else {
                // Picked Destination: Close and search immediately!
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
    html = html[:old_open_block_start] + perfect_flow_modal + "\n        " + html[old_open_block_end:]

# Bump version to v3.1.2
html = html.replace('v3.1.1 (2026.07.01版)', 'v3.1.2 (2026.07.01版)')
html = html.replace('核心版本: v3.1.1', '核心版本: v3.1.2 (出發連選抵達 · 抵達單擊秒關 · 最完美選站流)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated to v3.1.2 with perfect 2-in-1 / 1-in-1 hybrid station picker flow!")
