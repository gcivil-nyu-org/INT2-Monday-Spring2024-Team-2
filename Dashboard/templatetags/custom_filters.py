from django import template

register = template.Library()


@register.filter
def remove_prefix(value, prefix):
    if value.startswith(prefix):
        return value[len(prefix):]
    return value
