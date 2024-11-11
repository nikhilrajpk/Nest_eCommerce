from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        return value * arg
    except (TypeError, ValueError):
        return 0
