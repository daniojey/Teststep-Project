from django import template

register = template.Library()

@register.filter(name='addattr')
def addattr(field, attr):
    # Разбиваем строку атрибутов "ключ:значение" и добавляем в attrs
    key, value = attr.split(':')
    return field.as_widget(attrs={key: value})