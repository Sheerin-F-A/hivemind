/**
 * Global App Interactivity
 */
document.addEventListener('DOMContentLoaded', () => {
    // Top-right User Menu Dropdown
    const userMenuBtn = document.getElementById('userMenuBtn');
    if (userMenuBtn) {
        const userDropdown = userMenuBtn.querySelector('.dropdown-menu');
        userMenuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            // Close other dropdowns first
            closeAllDropdowns(userDropdown);
            userDropdown.classList.toggle('show');
        });
    }

    // Notification Dropdown
    const notificationWrapper = document.querySelector('.notification-wrapper');
    if (notificationWrapper) {
        const notifBtn = notificationWrapper.querySelector('.notification-btn');
        const notifMenu = notificationWrapper.querySelector('.dropdown-menu');
        
        notifBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            // Close other dropdowns first
            closeAllDropdowns(notifMenu);
            notifMenu.classList.toggle('show');
        });
    }

    // Close Dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.user-menu') && !e.target.closest('.notification-wrapper')) {
            closeAllDropdowns();
        }
    });

    function closeAllDropdowns(except = null) {
        document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
            if (menu !== except) {
                menu.classList.remove('show');
            }
        });
    }

    // Google Sheets Mock Sync (Story 6 Implementation)
    const exportBtns = document.querySelectorAll('.settings-group .btn-external');
    exportBtns.forEach(btn => {
        if (btn.textContent.includes('Download history')) {
            btn.textContent = 'Sync to Google Sheets (gspread)';
            btn.addEventListener('click', () => {
                btn.innerHTML = `<svg class="spinner" width="16" height="16" viewBox="0 0 20 20" style="vertical-align:middle;margin-right:5px;"><circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="40" stroke-dashoffset="10"/></svg> Authenticating gspread Service Account...`;
                btn.style.pointerEvents = 'none';
                
                setTimeout(() => btn.innerHTML = `<svg class="spinner" width="16" height="16" viewBox="0 0 20 20" style="vertical-align:middle;margin-right:5px;"><circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="40" stroke-dashoffset="10"/></svg> Writing vault rows... (Rate Limiting)`, 1500);
                setTimeout(() => {
                    btn.innerHTML = `Successfully written 100 rows to Google Sheets!`;
                    btn.style.backgroundColor = '#4CAF50';
                    btn.style.color = '#fff';
                    btn.style.borderColor = '#4CAF50';
                    setTimeout(() => {
                        btn.textContent = 'Sync to Google Sheets (gspread)';
                        btn.removeAttribute('style');
                    }, 4000);
                }, 4000);
            });
        }
    });

    // Auth Session Synchronization
    async function syncSessionStatus() {
        try {
            const res = await fetch('/api/auth/status');
            const data = await res.json();
            
            if (data.authenticated) {
                // Find any element containing exactly 'username' or 'u/username' text
                // Also explicitly target common classes just in case
                const els = document.querySelectorAll('.username, .profile-username, .comment-author');
                els.forEach(el => {
                    if (!el) return;
                    if (el.textContent.includes('u/username')) {
                        el.textContent = el.textContent.replace('u/username', 'u/' + data.username);
                    } else if (el.textContent.trim() === 'username') {
                        el.textContent = data.username;
                    }
                });
            } else {
                // If not authenticated and not on index.html, redirect back to login
                if (!window.location.pathname.endsWith('index.html') && window.location.pathname !== '/' && !window.location.pathname.endsWith('login.js')) {
                    window.location.href = 'index.html';
                }
            }
        } catch (e) {
            console.error('Session sync failed:', e);
        }
    }

    // Handle logout button
    const logoutBtns = Array.from(document.querySelectorAll('a.dropdown-item')).filter(el => el.textContent.trim().toLowerCase() === 'logout');
    logoutBtns.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                await fetch('/api/auth/logout', { method: 'POST' });
                window.location.href = 'index.html';
            } catch (err) {
                console.error("Logout failed", err);
            }
        });
    });

    // Fire sync
    syncSessionStatus();
});
