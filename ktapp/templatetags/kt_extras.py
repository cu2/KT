from django import template
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse


register = template.Library()


@register.filter
def film_url_html(film, subpage='film_main'):
    if film.other_titles:
        second_row = film.other_titles.split('\n')[0]
    else:
        second_row = '&nbsp;'
    return mark_safe(u'<a href="{url}">{orig_title}</a><br />\n<span class="td_sub">{second_row}</span>'.format(
        url=reverse(subpage, args=(film.pk, film.film_slug)),
        orig_title=film.orig_title,
        second_row=second_row,
    ))


@register.filter
def film_rating_html(film, with_count=True):
    num_rating = film.num_rating()
    if num_rating == 0:
        return ''
    avg_rating = film.avg_rating()
    if avg_rating is not None:
        avg_rating = round(avg_rating, 1)
    if with_count:
        return mark_safe(u'{avg_rating}<br />\n<span class="td_sub">({num_rating})</span>'.format(
            avg_rating=avg_rating,
            num_rating=num_rating,
        ))
    return mark_safe(u'{avg_rating}'.format(
        avg_rating=avg_rating,
    ))