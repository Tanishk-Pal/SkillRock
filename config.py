import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    # Flask Security
    SECRET_KEY = os.getenv("SECRET_KEY", "skillswap-campus-production-secret-key-change-me")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")

    # MongoDB Configuration (Connected to MongoDB Atlas)
    MONGODB_URI = os.getenv("MONGODB_URI", "").strip()
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "skillswap_campus").strip()

    # Google OAuth 2.0 Credentials
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "").strip()

    # Google Gemini AI API Key Pool (10 Slots for Auto-Failover)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_API_KEYS = []
    for _i in range(1, 11):
        _k = os.getenv(f"GEMINI_API_KEY_{_i}", "").strip()
        if _k.startswith('"') and _k.endswith('"'):
            _k = _k[1:-1].strip()
        elif _k.startswith("'") and _k.endswith("'"):
            _k = _k[1:-1].strip()
        if _k and "YOUR_GEMINI" not in _k and _k not in GEMINI_API_KEYS:
            GEMINI_API_KEYS.append(_k)
    if GEMINI_API_KEY:
        _clean_key = GEMINI_API_KEY.strip('\'"')
        if _clean_key and "YOUR_GEMINI" not in _clean_key and _clean_key not in GEMINI_API_KEYS:
            GEMINI_API_KEYS.insert(0, _clean_key)

    # Session & Cookie Security & Long-Term Persistence (60 days)
    PERMANENT_SESSION_LIFETIME = timedelta(days=60)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() in ("true", "1", "yes")

    # Flask-Login Persistent "Remember Me" Cookie (60 days)
    REMEMBER_COOKIE_DURATION = timedelta(days=60)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() in ("true", "1", "yes")
