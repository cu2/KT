from django import template
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse


register = template.Library()


@register.filter
def film_url_html(film, subpage='film_main'):
    if film.second_title:
        second_row = film.second_title
    else:
        second_row = '&nbsp;'
    return mark_safe(u'<a href="{url}">{orig_title}</a><br />\n<span class="td_sub">{second_row}</span>'.format(
        url=reverse(subpage, args=(film.id, film.slug_cache)),
        orig_title=film.orig_title,
        second_row=second_row,
    ))


@register.filter
def film_url_html_w_year(film, subpage='film_main'):
    if film.second_title:
        second_row = film.second_title
    else:
        second_row = '&nbsp;'
    return mark_safe(u'<a href="{url}">{orig_title}</a>{year}<br />\n<span class="td_sub">{second_row}</span>'.format(
        url=reverse(subpage, args=(film.id, film.slug_cache)),
        orig_title=film.orig_title,
        year=' (%s)' % film.year if film.year else '',
        second_row=second_row,
    ))


@register.filter
def film_rating_html(film, with_count=True):
    if film.number_of_ratings == 0:
        return ''
    if film.average_rating is None:
        avg_rating = '?'
    else:
        avg_rating = round(film.average_rating, 1)
    if with_count:
        return mark_safe(u'{avg_rating}<br />\n<span class="td_sub">({num_rating})</span>'.format(
            avg_rating=avg_rating,
            num_rating=film.number_of_ratings,
        ))
    return mark_safe(u'{avg_rating}'.format(
        avg_rating=avg_rating,
    ))
