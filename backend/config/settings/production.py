from .base import *
import dj_database_url
import os

DEBUG = False

allowed_hosts_env = os.getenv('ALLOWED_HOSTS')
ALLOWED_HOSTS = allowed_hosts_env.split(',') if allowed_hosts_env else ['*']

# Database
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600
    )
}

# Security Settings
# Make sure to set SECURE_SSL_REDIRECT=True in .env once you have HTTPS (SSL) configured!
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# CORS Settings
cors_origins_env = os.getenv('CORS_ALLOWED_ORIGINS')
CORS_ALLOWED_ORIGINS = cors_origins_env.split(',') if cors_origins_env else []

# Whitenoise for serving static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
