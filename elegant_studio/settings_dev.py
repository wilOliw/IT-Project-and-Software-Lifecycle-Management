"""
Настройки Django для разработки
"""
from .settings import *

# Используем SQLite для разработки
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Отключаем отладку для продакшена
DEBUG = True

# Настройки для разработки
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Упрощенные настройки allauth для разработки
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_RATE_LIMITS = {}
