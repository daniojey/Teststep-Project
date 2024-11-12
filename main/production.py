from .settings import *

DEBUG = True

ALLOWED_HOSTS = ['teststep.herokuapp.com', 'teststep-54d2adad5311.herokuapp.com']

SESSION_COOKIE_SECURE = True  # Для работы через HTTPS
CSRF_COOKIE_SECURE = True     # Для защиты от CSRF-атак
SECURE_SSL_REDIRECT = True