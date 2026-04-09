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
