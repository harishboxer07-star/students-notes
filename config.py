import os
from pathlib import Path

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'lak04-educational-portal-dev-key-7e9b4a1c')
    DATABASE = os.environ.get('DATABASE_PATH', str(BASE_DIR / 'lak04.db'))
    
    # Session security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds
    
    # App Information
    APP_NAME = "LAK04"
    APP_TAGLINE = "Student Notes and Subject Management System"

    # File Upload settings
    UPLOAD_FOLDER = str(BASE_DIR / 'static' / 'uploads')
    ALLOWED_EXTENSIONS = {'pdf'}
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB max upload
