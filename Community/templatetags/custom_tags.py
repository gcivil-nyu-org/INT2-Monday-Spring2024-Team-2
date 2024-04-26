from django import template

register = template.Library()


@register.filter(name="get_topic")
def get_topic(list, key):
    for tuple in list:
        if tuple[0] == key:
            return tuple[1]

    return "Other"
