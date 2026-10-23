/**
 * LAK04 — Student Notes & Subject Management System
 * Interactive Client Script & PWA Controller
 */

// -------------------------------------------------------------
// Global In-App PDF Viewer Modal Controller
// -------------------------------------------------------------
window.openInAppPdfViewer = function(pdfUrl, title) {
    const modal = document.getElementById('in-app-pdf-modal');
    const iframe = document.getElementById('pdf-viewer-frame');
    const titleEl = document.getElementById('pdf-modal-title');
    if (!modal || !iframe) return;

    if (titleEl && title) {
        titleEl.textContent = title;
    }
    iframe.src = pdfUrl;
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
};

window.closeInAppPdfViewer = function() {
    const modal = document.getElementById('in-app-pdf-modal');
    const iframe = document.getElementById('pdf-viewer-frame');
    if (!modal) return;

    modal.style.display = 'none';
    if (iframe) {
        iframe.src = 'about:blank';
    }
    document.body.style.overflow = '';
};

document.addEventListener('DOMContentLoaded', () => {
    // ---------------------------------------------------------
    // 1. Reset Theme to Clean Default Light Mode
    // ---------------------------------------------------------
    try {
        localStorage.removeItem('lak04-theme');
        document.documentElement.removeAttribute('data-theme');
        document.body.removeAttribute('data-theme');
    } catch (e) {}

    // ---------------------------------------------------------
    // 2. Mobile Navigation Drawer Toggle
    // ---------------------------------------------------------
    const mobileToggle = document.getElementById('mobile-menu-toggle');
    const primaryNav = document.getElementById('primary-nav-menu');
    const toggleIcon = document.getElementById('toggle-icon');

    if (mobileToggle && primaryNav) {
        mobileToggle.addEventListener('click', (e) => {
            e.stopPropagation();
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

        // Close mobile nav when clicking any link inside
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
    // 3. PWA Installation Handler (Mobile & Desktop)
    // ---------------------------------------------------------
    let deferredPrompt = null;
    const navInstallBtn = document.getElementById('nav-install-btn');
    const pwaBanner = document.getElementById('pwa-install-banner');
    const pwaInstallBtn = document.getElementById('pwa-install-btn');
    const pwaDismissBtn = document.getElementById('pwa-dismiss-btn');

    window.addEventListener('beforeinstallprompt', (e) => {
        // Prevent default mini-infobar
        e.preventDefault();
        deferredPrompt = e;

        // Show header button
        if (navInstallBtn) navInstallBtn.style.display = 'inline-flex';

        // Show banner if user hasn't explicitly dismissed it recently
        const dismissed = localStorage.getItem('lak04-pwa-dismissed');
        if (pwaBanner && !dismissed) {
            pwaBanner.style.display = 'flex';
        }
    });

    async function triggerPwaPrompt() {
        if (!deferredPrompt) {
            alert('To install LAK04 on iOS Safari: tap Share > "Add to Home Screen". On Chrome Desktop: click the install icon in the address bar.');
            return;
        }
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log('PWA installation choice:', outcome);
        deferredPrompt = null;
        if (pwaBanner) pwaBanner.style.display = 'none';
        if (navInstallBtn) navInstallBtn.style.display = 'none';
    }

    if (pwaInstallBtn) pwaInstallBtn.addEventListener('click', triggerPwaPrompt);
    if (navInstallBtn) navInstallBtn.addEventListener('click', triggerPwaPrompt);

    if (pwaDismissBtn) {
        pwaDismissBtn.addEventListener('click', () => {
            if (pwaBanner) pwaBanner.style.display = 'none';
            localStorage.setItem('lak04-pwa-dismissed', 'true');
        });
    }

    window.addEventListener('appinstalled', () => {
        console.log('LAK04 installed successfully!');
        if (pwaBanner) pwaBanner.style.display = 'none';
        if (navInstallBtn) navInstallBtn.style.display = 'none';
        deferredPrompt = null;
    });

    // ---------------------------------------------------------
    // 4. Password Visibility Toggle
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
    // 5. Auto-Dismiss Flash Alerts
    // ---------------------------------------------------------
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach((alert) => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1), transform 0.4s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-12px)';
            setTimeout(() => {
                if (alert.parentElement) {
                    alert.remove();
                }
            }, 400);
        }, 5500);
    });

    // ---------------------------------------------------------
    // 6. Modal Backdrop & Escape Key Handlers
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
            window.closeInAppPdfViewer();
        }
    });

    // ---------------------------------------------------------
    // 7. Prevent Duplicate Form Submissions
    // ---------------------------------------------------------
    const forms = document.querySelectorAll('form');
    forms.forEach((form) => {
        form.addEventListener('submit', (e) => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                if (form.checkValidity()) {
                    setTimeout(() => {
                        submitBtn.classList.add('btn-loading');
                    }, 50);
                }
            }
        });
    });

    // ---------------------------------------------------------
    // 8. Floating Back to Top Button
    // ---------------------------------------------------------
    const backToTopBtn = document.getElementById('back-to-top-btn');
    if (backToTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 280) {
                backToTopBtn.classList.add('visible');
            } else {
                backToTopBtn.classList.remove('visible');
            }
        }, { passive: true });

        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // ---------------------------------------------------------
    // 9. Desktop Keyboard Shortcut ('/' to Focus Search)
    // ---------------------------------------------------------
    document.addEventListener('keydown', (e) => {
        if (e.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
            const searchInput = document.getElementById('hero-search-input') || 
                                document.getElementById('notes-search-input') ||
                                document.getElementById('subject-search-input');
            if (searchInput) {
                e.preventDefault();
                searchInput.focus();
                searchInput.select();
            }
        }
    });

    // ---------------------------------------------------------
    // 10. Register Service Worker for Mobile PWA
    // ---------------------------------------------------------
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/static/sw.js')
                .then((reg) => console.log('LAK04 Service Worker registered:', reg.scope))
                .catch((err) => console.log('LAK04 Service Worker error:', err));
        });
    }
});
