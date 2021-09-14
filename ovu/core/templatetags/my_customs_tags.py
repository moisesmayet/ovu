from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
def trim(value: str):
    return value.lower().replace(" ", "")


@register.filter
def index(indexable, i):
    return indexable[i]
