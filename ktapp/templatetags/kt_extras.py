import datetime

from django import template
from django.utils.safestring import mark_safe
from django.utils.http import urlquote_plus as urlquote_plus_function
from django.core.urlresolvers import reverse

from kt import settings
from ktapp.utils import strip_whitespace as strip_whitespace_function


register = template.Library()


@register.filter
def film_directors(film):
    if not film.directors_cache:
        return '?'
    ids, slugs, names = film.directors_cache.split(';')
    ids = ids.split(',')
    slugs = slugs.split(',')
    names = names.split(',')
    if len(ids) > 3:
        more = ' - ...'
    else:
        more = ''
    dir_links = []
    for id, slug_cache, name in zip(ids[:3], slugs, names):
        dir_links.append(u'<a href="{url}">{name}</a>'.format(
            url=reverse('artist', args=(id, slug_cache)),
            name=name,
        ))
    return mark_safe(' - '.join(dir_links) + more)


@register.filter
def film_genres(film, all=None):
    if not film.genres_cache:
        return '?'
    ids, slugs, names = film.genres_cache.split(';')
    ids = ids.split(',')
    slugs = slugs.split(',')
    names = names.split(',')
    if len(ids) > 3 and all is None:
        more = ', ...'
    else:
        more = ''
    if all is None:
        ids = ids[:3]
    genre_links = []
    for id, slug_cache, name in zip(ids, slugs, names):
        genre_links.append(name)
    return mark_safe(', '.join(genre_links) + more)


@register.filter
def film_genres_jsonld(film):
    if not film.genres_cache:
        return ''
    ids, slugs, names = film.genres_cache.split(';')
    ids = ids.split(',')
    slugs = slugs.split(',')
    names = names.split(',')
    genre_links = []
    for id, slug_cache, name in zip(ids, slugs, names):
        genre_links.append('"%s"' % name)
    return mark_safe('"genre": [%s],' % (', '.join(genre_links)))


@register.filter
def film_url_html(film, subpage='film_main'):
    if film.second_title:
        second_row = film.second_title
    else:
        second_row = '&nbsp;'
    return mark_safe(u'<a href="{url}"{vapiti}>{orig_title}</a><br />\n<span class="td_sub">{second_row}</span>'.format(
        url=reverse(subpage, args=(film.id, film.slug_cache)),
        vapiti=' class="vapiti"' if film.main_premier_year == settings.VAPITI_YEAR else '',
        orig_title=film.orig_title,
        second_row=second_row,
    ))


@register.filter
def film_url_html_big(film, subpage='film_main'):
    if film.second_title:
        second_row = film.second_title
    else:
        second_row = '&nbsp;'
    return mark_safe(u'<b><a href="{url}"{vapiti}>{orig_title}</a></b><br />\n{second_row}'.format(
        url=reverse(subpage, args=(film.id, film.slug_cache)),
        vapiti=' class="vapiti"' if film.main_premier_year == settings.VAPITI_YEAR else '',
        orig_title=film.orig_title,
        second_row='%s<br />\n' % second_row if second_row else '',
    ))


@register.filter
def film_url_html_from_role(role, subpage='film_main'):
    if role.film_second_title:
        second_row = role.film_second_title
    else:
        second_row = '&nbsp;'
    return mark_safe(u'<a href="{url}"{vapiti}>{orig_title}</a><br />\n<span class="td_sub">{second_row}</span>'.format(
        url=reverse(subpage, args=(role.film_id, role.film_slug_cache)),
        vapiti=' class="vapiti"' if role.film_main_premier_year == settings.VAPITI_YEAR else '',
        orig_title=role.film_orig_title,
        second_row=second_row,
    ))


@register.filter
def film_url_html_from_article(article, subpage='film_main'):
    if article.film_second_title:
        second_row = article.film_second_title
    else:
        second_row = '&nbsp;'
    return mark_safe(u'<a href="{url}"{vapiti}>{orig_title}</a>{year}<br />\n<span class="td_sub">{second_row}</span>'.format(
        url=reverse(subpage, args=(article.film_id, article.film_slug_cache)),
        vapiti=' class="vapiti"' if article.film_main_premier_year == settings.VAPITI_YEAR else '',
        orig_title=article.film_orig_title,
        year=' (%s)' % article.film_year if article.film_year else '',
        second_row=second_row,
    ))


@register.filter
def film_url_html_w_year(film, subpage='film_main'):
    if film.second_title:
        second_row = film.second_title
    else:
        second_row = '&nbsp;'
    return mark_safe(u'<a href="{url}"{vapiti}>{orig_title}</a>{year}<br />\n<span class="td_sub">{second_row}</span>'.format(
        url=reverse(subpage, args=(film.id, film.slug_cache)),
        vapiti=' class="vapiti"' if film.main_premier_year == settings.VAPITI_YEAR else '',
        orig_title=film.orig_title,
        year=' (%s)' % film.year if film.year else '',
        second_row=second_row,
    ))


@register.filter
def film_url_html_w_linked_year(film, subpage='film_main'):
    if film.second_title:
        second_row = film.second_title
    else:
        second_row = '&nbsp;'
    return mark_safe(u'<a href="{url}"{vapiti}>{orig_title}{year}</a><br />\n<span class="td_sub">{second_row}</span>'.format(
        url=reverse(subpage, args=(film.id, film.slug_cache)),
        vapiti=' class="vapiti"' if film.main_premier_year == settings.VAPITI_YEAR else '',
        orig_title=film.orig_title,
        year=' (%s)' % film.year if film.year else '',
        second_row=second_row,
    ))


@register.filter
def oneliner_film_url_html_simple(film, subpage='film_main'):
    return mark_safe(u'<a href="{url}"{vapiti}>{orig_title}</a>'.format(
        url=reverse(subpage, args=(film.id, film.slug_cache)),
        vapiti=' class="vapiti"' if film.main_premier_year == settings.VAPITI_YEAR else '',
        orig_title=film.orig_title,
    ))


@register.filter
def oneliner_film_url_html_w_year(film, subpage='film_main'):
    return mark_safe(u'<a href="{url}"{vapiti}>{orig_title}{year}{second_row}</a>'.format(
        url=reverse(subpage, args=(film.id, film.slug_cache)),
        vapiti=' class="vapiti"' if film.main_premier_year == settings.VAPITI_YEAR else '',
        orig_title=film.orig_title,
        year=' (%s)' % film.year if film.year else '',
        second_row=' / %s' % film.second_title if film.second_title else '',
    ))


@register.filter
def oneliner_film_html_w_year(film):
    return mark_safe(u'{orig_title}{year}{second_row}'.format(
        orig_title=film.orig_title,
        year=' (%s)' % film.year if film.year else '',
        second_row=' / %s' % film.second_title if film.second_title else '',
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
            avg_rating=unicode(avg_rating).replace('.', ','),
            num_rating=film.number_of_ratings,
        ))
    return mark_safe(u'{avg_rating}'.format(
        avg_rating=unicode(avg_rating).replace('.', ','),
    ))


@register.filter
def film_avg_rating_html(film):
    if film.number_of_ratings == 0:
        return ''
    if film.average_rating is None:
        avg_rating = '?'
    else:
        avg_rating = round(film.average_rating, 1)
    return unicode(avg_rating).replace('.', ',')


@register.filter
def film_avg_rating_english(film):
    if film.average_rating:
        avg_rating = round(film.average_rating, 1)
        return unicode(avg_rating)
    return ''


@register.filter
def film_num_rating_html(film):
    if film.number_of_ratings == 0:
        return ''
    return unicode(film.number_of_ratings)


@register.filter
def film_rating_sort_value(film):
    if film.number_of_ratings == 0:
        return '-0.1'
    if film.average_rating is None:
        return '0.0'
    return unicode(film.average_rating)


@register.filter
def film_fav_rating_html(film, with_count=True):
    if film.fav_number_of_ratings == 0:
        return ''
    if film.fav_average_rating is None:
        avg_rating = '?'
    else:
        avg_rating = round(film.fav_average_rating, 1)
    if with_count:
        return mark_safe(u'{avg_rating}<br />\n<span class="td_sub">({num_rating})</span>'.format(
            avg_rating=unicode(avg_rating).replace('.', ','),
            num_rating=film.fav_number_of_ratings,
        ))
    return mark_safe(u'{avg_rating}'.format(
        avg_rating=unicode(avg_rating).replace('.', ','),
    ))


@register.filter
def film_fav_rating_sort_value(film):
    if film.fav_number_of_ratings == 0:
        return '0000000'
    if film.fav_average_rating is None:
        return '00%05d' % film.fav_number_of_ratings
    return '%02d%05d' % (int(10 * film.fav_average_rating), film.fav_number_of_ratings)


@register.filter
def urlquote_plus(value):
    return urlquote_plus_function(value)


@register.filter
def strip_whitespace(value):
    return strip_whitespace_function(value)


@register.filter
def percent(num, denom):
    return int(round(100.0 * float(num) / float(denom)))


@register.filter
def str2date(str):
    return datetime.datetime.strptime(str, '%Y-%m-%d')
