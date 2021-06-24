from datetime import timedelta

from django import template
from django.utils import timezone, dateformat
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def daterange(start: timezone, end: timezone):
    if end.day == start.day:
        return dateformat.format(start, "d F")
    elif end - start < timedelta(days=365):
        return f"{dateformat.format(start, 'd F')} - {dateformat.format(end, 'd F')}"
    else:
        return (
            f"{dateformat.format(start, 'd F Y')} - {dateformat.format(end, 'd F Y')}"
        )


@register.simple_tag
def datetimerange(start: timezone, end: timezone):
    if end.day == start.day:
        return format_html(
            '<span class="ws-nowrap">{}</span> - <span class="ws-nowrap">{}</span>',
            dateformat.format(start, "G:i"),
            dateformat.format(end, "G:i"),
        )
    elif end - start < timedelta(days=365):
        return format_html(
            '<span class="ws-nowrap">{}</span> - <span class="ws-nowrap">{}</span>',
            dateformat.format(start, "G:i d F"),
            dateformat.format(end, "G:i d F"),
        )
    else:
        return format_html(
            '<span class="ws-nowrap">{}</span> - <span class="ws-nowrap">{}</span>',
            dateformat.format(start, "G:i x"),
            dateformat.format(end, "G:i x"),
        )
