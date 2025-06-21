from .settings import *

DEBUG = False

ALLOWED_HOSTS = ['https://teststep1-df3bdde0196a.herokuapp.com/' "https://teststep1-df3bdde0196a.herokuapp.com", 'localhost', '*']
ALLOWED_HOSTS += [os.environ.get('HEROKU_APP_NAME', '') + '.herokuapp.com']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True  # Для работы через HTTPS
CSRF_COOKIE_SECURE = True     # Для защиты от CSRF-атак
SECURE_SSL_REDIRECT = True

SECURE_HSTS_SECONDS = 3600  # 1 час
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'