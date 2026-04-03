from django import template

register = template.Library()


@register.filter
def split(value, separator):
    """
    Split a string by a separator and strip whitespace from each item
    Usage: {{ string_value|split:"," }}
    """
    if not value:
        return []
    return [item.strip() for item in value.split(separator)]

