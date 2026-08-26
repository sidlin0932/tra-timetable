import os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Comprehensive Mobile Optimization CSS
mobile_overhaul_css = """
        /* ==========================================================
           COMPREHENSIVE MOBILE RESPONSIVE OVERHAUL (手機版全方位體驗升級)
           ========================================================== */
        @media (max-width: 768px) {
            body {
                padding: 0;
            }
            .container {
                padding: 0 12px 36px;
            }
            .navbar {
                padding: 12px 14px;
                gap: 8px;
            }
            .nav-brand {
                gap: 8px;
            }
            .nav-logo {
                font-size: 1.5rem;
            }
            .nav-title h1 {
                font-size: 1.05rem;
                line-height: 1.25;
            }
            .nav-title p {
                font-size: 0.72rem;
                display: none; /* Hide subtitle on very small screens to save space */
            }
            .theme-toggle {
                padding: 6px 10px;
                font-size: 0.75rem;
            }

            /* Query Panel Mobile */
            .query-panel {
                padding: 14px;
                border-radius: 12px;
                margin-bottom: 16px;
            }
            .query-grid {
                grid-template-columns: 1fr;
                gap: 8px;
            }
            .station-input-box {
                flex-direction: row;
                gap: 6px;
            }
            .station-input {
                font-size: 1rem;
                padding: 10px 12px;
            }
            .btn-station-picker {
                padding: 10px 12px;
                font-size: 0.82rem;
                white-space: nowrap;
            }
            .btn-swap {
                transform: rotate(90deg);
                margin: 2px auto;
                width: 36px;
                height: 36px;
                font-size: 1.1rem;
            }

            /* Quick Hubs Bar Mobile */
            .quick-hubs-bar {
                padding: 8px 10px;
                margin-bottom: 12px;
            }
            .quick-hubs-list {
                overflow-x: auto;
                flex-wrap: nowrap;
                padding-bottom: 4px;
                scrollbar-width: none;
            }
            .quick-hubs-list::-webkit-scrollbar {
                display: none;
            }
            .quick-hub-btn {
                flex-shrink: 0;
                padding: 5px 10px;
                font-size: 0.78rem;
            }

            /* Filter Row Mobile */
            .filter-row {
                flex-direction: column;
                gap: 12px;
                margin-top: 12px;
            }
            .segmented-control {
                overflow-x: auto;
                flex-wrap: nowrap;
                padding: 3px;
                scrollbar-width: none;
            }
            .segmented-control::-webkit-scrollbar {
                display: none;
            }
            .segment-btn {
                flex-shrink: 0;
                padding: 6px 10px;
                font-size: 0.78rem;
                white-space: nowrap;
            }
            .btn-search {
                width: 100%;
                padding: 12px;
                font-size: 1rem;
                justify-content: center;
            }

            /* Sort Controls Mobile */
            .sort-controls-bar {
                flex-direction: column;
                align-items: stretch;
                gap: 8px;
                padding: 10px 12px;
            }
            .sort-select-group {
                flex-direction: column;
                gap: 6px;
            }
            .sort-select {
                width: 100%;
                font-size: 0.85rem;
                padding: 6px 10px;
            }
            .sort-header-row {
                display: none; /* Desktop table header hidden on mobile */
            }

            /* Trip Card Mobile Modern Layout */
            .trip-card {
                border-radius: 12px;
                margin-bottom: 12px;
            }
            .trip-header-row {
                display: flex;
                flex-direction: column;
                align-items: stretch;
                padding: 14px 16px;
                gap: 10px;
            }
            .mobile-trip-main-row {
                display: flex;
                align-items: center;
                justify-content: space-between;
                width: 100%;
            }
            .mobile-time-flow {
                display: flex;
                align-items: baseline;
                gap: 8px;
            }
            .time-display {
                font-size: 1.35rem;
            }
            .duration-display {
                font-size: 0.95rem;
                padding: 3px 8px;
                background: var(--primary-light);
                border-radius: 6px;
            }
            .train-types-badges {
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
                align-items: center;
            }
            .train-badge {
                font-size: 0.82rem;
                padding: 4px 8px;
            }

            /* Modal Bottom Sheet Mobile */
            .modal-backdrop {
                padding: 0;
                align-items: flex-end;
            }
            .modal-dialog {
                width: 100% !important;
                max-width: 100% !important;
                max-height: 88vh !important;
                border-radius: 20px 20px 0 0 !important;
                margin: 0 !important;
            }
            .modal-header {
                padding: 16px 18px 12px;
            }
            .modal-trip-stepper {
                flex-direction: row;
                gap: 6px;
                width: 100%;
            }
            .modal-step-btn {
                flex: 1;
                justify-content: center;
                padding: 8px 6px;
                font-size: 0.8rem;
            }
            .modal-tabs-nav {
                padding: 8px 14px;
                gap: 5px;
                max-height: 105px;
            }
            .modal-tab-pill {
                padding: 4px 8px;
                font-size: 0.75rem;
            }
            .station-grid {
                grid-template-columns: repeat(3, 1fr) !important;
                gap: 6px !important;
            }
            .station-btn {
                padding: 10px 4px !important;
                font-size: 0.88rem !important;
                font-weight: 700 !important;
                min-height: 42px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .modal-body {
                padding: 10px 14px 28px;
                max-height: 52vh;
            }

            /* Timeline & Itinerary details on mobile */
            .itinerary-details {
                padding: 12px 14px 18px;
            }
            .timeline {
                padding-left: 20px;
            }
            .timeline-dot {
                left: -20px;
                width: 14px;
                height: 14px;
            }
            .leg-card {
                padding: 10px 12px;
            }
        }
"""

html = html.replace('</style>', mobile_overhaul_css + '\n    </style>', 1)

# Update renderResults trip-header-row to be mobile structured
old_trip_header_html = """                        <div class="trip-header-row" onclick="toggleDetails(${rIdx})">
                            <div class="train-types-badges">
                                ${legsBadgesWithDuration}
                                ${trPassBadge}
                                ${tightTransferBadge}
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
                        </div>"""

new_trip_header_html = """                        <div class="trip-header-row" onclick="toggleDetails(${rIdx})">
                            <div class="mobile-trip-main-row">
                                <div class="mobile-time-flow">
                                    <div>
                                        <div class="time-display">${route.dep_time}</div>
                                        <div class="time-st-label"><span class="clickable-station" onclick="event.stopPropagation(); openStationTimetable('${route.legs[0].from}')">${route.legs[0].from} 📋</span></div>
                                    </div>
                                    <span style="color:var(--text-muted); font-size:1.2rem; font-weight:700; margin:0 4px;">➔</span>
                                    <div>
                                        <div class="time-display">${route.arr_time}</div>
                                        <div class="time-st-label"><span class="clickable-station" onclick="event.stopPropagation(); openStationTimetable('${route.legs[route.legs.length-1].to}')">${route.legs[route.legs.length-1].to} 📋</span></div>
                                    </div>
                                </div>
                                <div style="text-align:right;">
                                    <div class="duration-display">${minToDuration(route.duration)}</div>
                                </div>
                            </div>
                            <div class="train-types-badges">
                                ${legsBadgesWithDuration}
                                ${trPassBadge}
                                ${tightTransferBadge}
                            </div>
                            <div class="transfers-badge-group">
                                ${transferTagHtml}
                            </div>
                            <div class="btn-toggle-details">
                                <span id="toggleText-${rIdx}">展開行程動線</span> ▾
                            </div>
                        </div>"""

html = html.replace(old_trip_header_html, new_trip_header_html, 1)

# Bump version to v3.6.0 (SemVer Minor: Mobile UX Full Overhaul & Bottom-Sheet Native Modal)
html = html.replace('v3.5.1 (2026.07.01版)', 'v3.6.0 (2026.07.01版)')
html = html.replace('核心版本: v3.5.1', '核心版本: v3.6.0 (手機版全方位響應式大重構 · 底部抽屜彈窗 · 觸控大按鈕)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Applied Comprehensive Mobile Responsive Overhaul and bumped to v3.6.0!")
