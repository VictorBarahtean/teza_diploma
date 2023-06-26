from django import template

register = template.Library()

@register.filter
def set_variable(value):
    return value
    