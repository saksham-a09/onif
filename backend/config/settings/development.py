from .base import *
import dj_database_url
import os

DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# In development, use DATABASE_URL if available, else fallback to sqlite
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600
    )
}

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
