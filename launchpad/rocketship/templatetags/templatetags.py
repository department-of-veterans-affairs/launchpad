from django import template
import datetime as dt
register = template.Library()

@register.filter
def underscore_to_space(value):
    return value.replace('_', ' ')

@register.filter
def first_letter_upper(value):
    if value[0:3].lower() == 'va ':
        return value[0:2].upper() + ''.join([letter for letter in value[2:]])
    return value[0].upper() + ''.join([letter for letter in value[1:]])

@register.filter
def clean_date(date):
    return dt.date.strftime(date, '%Y-%m-%d')
