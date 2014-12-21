#-*- coding: utf-8 -*-

from django import template
import datetime
from time import gmtime, strptime

register = template.Library()

def dayssince(value):
    "Returns number of days between today and value."
    today = datetime.date.today()
    diff  = today - value.date()

    if diff.days > 1:
        return '%s일 전' % diff.days
    elif diff.days == 1:
        return '어제'
    elif diff.days == 0:
        return '오늘'
    else:
        # Date is in the future; return formatted date.
        return value.strftime("%B %d, %Y")

register.filter('dayssince', dayssince)