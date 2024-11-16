from datetime import timedelta
from django.utils.timezone import now

from users.models import LoginAttempt

def is_blocked(email=None, ip_address=None, limit=5, timeframe=30):
    """
    Проверяет, заблокирован ли пользователь или IP-адрес.
    """
    time_threshold = now() - timedelta(minutes=timeframe)
    attempts = LoginAttempt.objects.filter(timestamp__gte=time_threshold, success=False)

    if email:
        attempts = attempts.filter(email=email)
    if ip_address:
        attempts = attempts.filter(ip_address=ip_address)

    return attempts.count() >= limit