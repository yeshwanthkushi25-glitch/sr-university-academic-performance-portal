"""
SR University Academic Performance Portal - Flask Extensions
"""

from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_talisman import Talisman

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please sign in to access this portal."
login_manager.login_message_category = "info"

csrf = CSRFProtect()

# Content Security Policy configured for Tailwind, Chart.js, and FontAwesome
CSP_POLICY = {
    "default-src": ["'self'"],
    "script-src": [
        "'self'",
        "'unsafe-inline'",
        "'unsafe-eval'",
        "https://cdn.tailwindcss.com",
        "https://cdn.jsdelivr.net",
    ],
    "style-src": [
        "'self'",
        "'unsafe-inline'",
        "https://cdnjs.cloudflare.com",
    ],
    "font-src": [
        "'self'",
        "https://cdnjs.cloudflare.com",
        "data:",
    ],
    "img-src": [
        "'self'",
        "data:",
        "https:",
    ],
    "connect-src": [
        "'self'",
    ],
}

talisman = Talisman()
