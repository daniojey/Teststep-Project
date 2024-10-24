# app/templatetags/timedelta_filters.py
from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def format_duration(value):
    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}г {minutes}хв {seconds}с"
        else:
            return f"{minutes}хв {seconds}с"
    return value  # Если значение не является timedelta, возвращаем его как есть

@register.filter
def format_duration_minutes(value):
    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}г {minutes}хв"
        else:
            return f"{minutes}хв"
    return value  # Если значение не является timedelta, возвращаем его как есть