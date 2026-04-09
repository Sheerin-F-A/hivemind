// Login Page Functionality

document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const togglePassword = document.getElementById('togglePassword');
    const loginBtn = document.getElementById('loginBtn');
    const errorMessage = document.getElementById('errorMessage');

    // Toggle password visibility
    if (togglePassword) {
        togglePassword.addEventListener('click', function () {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
        });
    }

    // Handle form submission
    if (loginForm) {
        loginForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const email = emailInput.value.trim();
            const password = passwordInput.value;

            // Hide error message
            errorMessage.style.display = 'none';

            // Show loading state
            showLoadingState();

            // Perform backend silent login using the credentials provided
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: email, password: password })
                });

                if (response.ok) {
                    window.location.href = 'dashboard.html';
                } else {
                    hideLoadingState();
                    showError();
                }
            } catch (error) {
                hideLoadingState();
                showError();
            }
        });
    }

    function showLoadingState() {
        loginBtn.disabled = true;
        loginBtn.querySelector('.btn-text').style.display = 'none';
        loginBtn.querySelector('.btn-loading').style.display = 'flex';
    }

    function hideLoadingState() {
        loginBtn.disabled = false;
        loginBtn.querySelector('.btn-text').style.display = 'block';
        loginBtn.querySelector('.btn-loading').style.display = 'none';
    }

    function showError() {
        errorMessage.style.display = 'flex';
    }

    // Update time in footer if present
    updateTime();
    setInterval(updateTime, 1000);

    function updateTime() {
        const timeElements = document.querySelectorAll('.time');
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });

        timeElements.forEach(el => {
            if (el) el.textContent = timeString;
        });
    }
});
