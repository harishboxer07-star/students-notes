/**
 * LAK04 - Student Notes & Subject Management System
 * Interactive Client Script
 */

document.addEventListener('DOMContentLoaded', () => {
    // ---------------------------------------------------------
    // 1. Mobile Navigation Menu Toggle
    // ---------------------------------------------------------
    const mobileToggle = document.getElementById('mobile-menu-toggle');
    const primaryNav = document.getElementById('primary-nav-menu');
    const toggleIcon = document.getElementById('toggle-icon');

    if (mobileToggle && primaryNav) {
        mobileToggle.addEventListener('click', () => {
            const isOpen = primaryNav.classList.toggle('open');
            mobileToggle.setAttribute('aria-expanded', isOpen);
            if (toggleIcon) {
                if (isOpen) {
                    toggleIcon.classList.remove('fa-bars');
                    toggleIcon.classList.add('fa-xmark');
                } else {
                    toggleIcon.classList.remove('fa-xmark');
                    toggleIcon.classList.add('fa-bars');
                }
            }
        });

        // Close mobile nav when clicking any nav link
        primaryNav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                if (primaryNav.classList.contains('open')) {
                    primaryNav.classList.remove('open');
                    mobileToggle.setAttribute('aria-expanded', 'false');
                    if (toggleIcon) {
                        toggleIcon.classList.remove('fa-xmark');
                        toggleIcon.classList.add('fa-bars');
                    }
                }
            });
        });

        // Close mobile nav when clicking outside
        document.addEventListener('click', (e) => {
            if (!primaryNav.contains(e.target) && !mobileToggle.contains(e.target)) {
                if (primaryNav.classList.contains('open')) {
                    primaryNav.classList.remove('open');
                    mobileToggle.setAttribute('aria-expanded', 'false');
                    if (toggleIcon) {
                        toggleIcon.classList.remove('fa-xmark');
                        toggleIcon.classList.add('fa-bars');
                    }
                }
            }
        });
    }

    // ---------------------------------------------------------
    // 2. Admin Login Password Show / Hide Toggle
    // ---------------------------------------------------------
    const passwordToggleBtn = document.getElementById('password-toggle');
    const passwordInput = document.getElementById('password');
    const passwordToggleIcon = document.getElementById('password-toggle-icon');

    if (passwordToggleBtn && passwordInput && passwordToggleIcon) {
        passwordToggleBtn.addEventListener('click', () => {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
            
            if (isPassword) {
                passwordToggleIcon.classList.remove('fa-eye');
                passwordToggleIcon.classList.add('fa-eye-slash');
            } else {
                passwordToggleIcon.classList.remove('fa-eye-slash');
                passwordToggleIcon.classList.add('fa-eye');
            }
        });
    }

    // ---------------------------------------------------------
    // 3. Auto-Dismiss Flash Alerts after 6 Seconds
    // ---------------------------------------------------------
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach((alert) => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                if (alert.parentElement) {
                    alert.remove();
                }
            }, 400);
        }, 6000);
    });

    // ---------------------------------------------------------
    // 4. Modal Backdrop Close on Click Outside or Escape Key
    // ---------------------------------------------------------
    const modals = document.querySelectorAll('.modal-backdrop');
    modals.forEach((modal) => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            modals.forEach((modal) => {
                modal.style.display = 'none';
            });
        }
    });

    // ---------------------------------------------------------
    // 5. Prevent Duplicate Form Submissions
    // ---------------------------------------------------------
    const forms = document.querySelectorAll('form');
    forms.forEach((form) => {
        form.addEventListener('submit', (e) => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                // If form is valid
                if (form.checkValidity()) {
                    setTimeout(() => {
                        submitBtn.classList.add('btn-loading');
                    }, 50);
                }
            }
        });
    });
});
