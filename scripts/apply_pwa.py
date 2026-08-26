# -*- coding: utf-8 -*-
html_path = 'f:/Antigravity/台鐵時刻表0701/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add PWA head meta tags & manifest
old_head = """<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>2026 台鐵時刻表與全路網跨區間轉乘規劃系統</title>"""

new_head = """<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#0284c7">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="台鐵時刻表">
    <meta name="description" content="2026 台鐵全路網時刻表 & 智慧接駁系統，支援多中繼站遊程規劃、平日週末開行日篩選與全島離線極速查詢。">
    <link rel="manifest" href="manifest.json">
    <link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
    <link rel="apple-touch-icon" href="icon-192.png">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>2026 台鐵時刻表與全路網跨區間轉乘規劃系統</title>"""

if old_head in content:
    content = content.replace(old_head, new_head)
else:
    print("Warning: old_head not found directly, checking variations")

# 2. Add Install PWA button in nav-actions
old_nav = """        <div class="nav-actions">
            <button class="theme-toggle" onclick="toggleTheme()" id="themeBtn">🌓 深淺模式</button>
        </div>"""

new_nav = """        <div class="nav-actions">
            <button class="btn-install-pwa" id="btnInstallPwa" onclick="installPwa()" style="display:none; background: #10b981; color:#fff; border:none; padding:7px 14px; border-radius:8px; font-size:0.85rem; font-weight:700; cursor:pointer; align-items:center; gap:6px; box-shadow:0 2px 6px rgba(16,185,129,0.3); transition:all 0.2s;">📲 安裝 App (離線可用)</button>
            <button class="theme-toggle" onclick="toggleTheme()" id="themeBtn">🌓 深淺模式</button>
        </div>"""

if old_nav in content:
    content = content.replace(old_nav, new_nav)

# 3. Add Service Worker registration and PWA install prompt handler at end of script
old_script_end = """        function toggleTheme() {
            const current = document.documentElement.getAttribute('data-theme');
            const target = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', target);
        }
    </script>"""

new_script_end = """        function toggleTheme() {
            const current = document.documentElement.getAttribute('data-theme');
            const target = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', target);
        }

        // ==========================================
        // PWA & Offline Service Worker Registration
        // ==========================================
        let deferredPrompt = null;
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            const btn = document.getElementById('btnInstallPwa');
            if (btn) {
                btn.style.display = 'inline-flex';
            }
        });

        function installPwa() {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {
                    if (choiceResult.outcome === 'accepted') {
                        console.log('User accepted the PWA install prompt');
                    }
                    deferredPrompt = null;
                    const btn = document.getElementById('btnInstallPwa');
                    if (btn) btn.style.display = 'none';
                });
            } else {
                alert('📱 提示：\n在 iPhone/iPad 請點擊 Safari 下方「分享」按鈕，選擇「加入主畫面」即可安裝為離線 App！\n在 Android/Chrome 請點擊右上角選單選擇「安裝應用程式」。');
            }
        }

        window.addEventListener('appinstalled', () => {
            const btn = document.getElementById('btnInstallPwa');
            if (btn) btn.style.display = 'none';
            console.log('PWA was installed successfully!');
        });

        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('./sw.js')
                    .then((reg) => {
                        console.log('[PWA] ServiceWorker registered successfully with scope:', reg.scope);
                    })
                    .catch((err) => {
                        console.log('[PWA] ServiceWorker registration failed:', err);
                    });
            });
        }
    </script>"""

if old_script_end in content:
    content = content.replace(old_script_end, new_script_end)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully injected PWA configuration and Service Worker into index.html!")
