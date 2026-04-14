document.addEventListener('DOMContentLoaded', () => {
    if(localStorage.getItem('token')) {
        window.location.href = '/dashboard';
    }

    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const otpForm = document.getElementById('otp-form');
    const alertBox = document.getElementById('alert-box');

    let currentLoginUser = '';

    const showAlert = (msg, type = 'error') => {
        alertBox.className = `mb-4 p-3 rounded-lg text-sm text-white ${type === 'error' ? 'bg-red-500/80 border border-red-500' : 'bg-green-500/80 border border-green-500'} block`;
        alertBox.textContent = msg;
        setTimeout(() => { alertBox.classList.add('hidden'); alertBox.classList.remove('block'); }, 4000);
    };

    document.getElementById('show-register').addEventListener('click', (e) => {
        e.preventDefault();
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
    });

    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        registerForm.classList.add('hidden');
        loginForm.classList.remove('hidden');
    });

    document.getElementById('back-to-login').addEventListener('click', (e) => {
        e.preventDefault();
        otpForm.classList.add('hidden');
        loginForm.classList.remove('hidden');
    });

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('reg-username').value;
        const password = document.getElementById('reg-password').value;

        try {
            const res = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();
            if (res.ok) {
                showAlert('Registration successful! Please sign in.', 'success');
                registerForm.classList.add('hidden');
                loginForm.classList.remove('hidden');
            } else {
                showAlert(data.message);
            }
        } catch (err) {
            showAlert('Network error occurred.');
        }
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();
            if (res.ok && data.require_otp) {
                currentLoginUser = username;
                showAlert('OTP generated! Check server console.', 'success');
                loginForm.classList.add('hidden');
                otpForm.classList.remove('hidden');
            } else {
                showAlert(data.message);
            }
        } catch (err) {
            showAlert('Network error occurred.');
        }
    });

    otpForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const otp = document.getElementById('otp-code').value;

        try {
            const res = await fetch('/api/verify-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: currentLoginUser, otp })
            });
            const data = await res.json();
            if (res.ok) {
                localStorage.setItem('token', data.token);
                localStorage.setItem('username', currentLoginUser);
                window.location.href = '/dashboard';
            } else {
                showAlert(data.message);
            }
        } catch (err) {
            showAlert('Network error occurred.');
        }
    });
});
