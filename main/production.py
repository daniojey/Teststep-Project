from .settings import *

DEBUG = False

ALLOWED_HOSTS = ['teststep.herokuapp.com']

SESSION_COOKIE_SECURE = True  # Для работы через HTTPS
CSRF_COOKIE_SECURE = True     # Для защиты от CSRF-атак
SECURE_SSL_REDIRECT = True