from .settings import *

DEBUG = True

ALLOWED_HOSTS = ['teststep.herokuapp.com', 'teststep-54d2adad5311.herokuapp.com', 'teststep-container-928592b92ce5.herokuapp.com', 'localhost']

# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True  # Для работы через HTTPS
CSRF_COOKIE_SECURE = True     # Для защиты от CSRF-атак
SECURE_SSL_REDIRECT = True

SECURE_HSTS_SECONDS = 3600  # 1 час
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

