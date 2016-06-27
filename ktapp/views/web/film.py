# -*- coding: utf-8 -*-

import json
import math

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils.http import urlquote_plus

from kt import settings
from ktapp import models
from ktapp import forms as kt_forms
from ktapp import utils as kt_utils
from ktapp import sqls as kt_sqls
from ktapp.helpers import filmlist


COMMENTS_PER_PAGE = 100


def _generic_film_view(view_function):

    def extended_view_function(request, id, film_slug, *args, **kwargs):
        film = get_object_or_404(models.Film, pk=id)
        rating = 0
        rating_date = None
        your_wish_status = 0
        if request.user.is_authenticated():
            try:
                vote = models.Vote.objects.get(film=film, user=request.user)
                rating = vote.rating
                rating_date = vote.when
            except models.Vote.DoesNotExist:
                pass
            your_wish_status = models.Wishlist.objects.filter(
                film=film,
                wished_by=request.user,
                wish_type=models.Wishlist.WISH_TYPE_YES,
            ).count()
        base_context = {
            'film': film,
            'film_directors': list(film.directors()),
            'countries': list(film.countries()),
            'genres': film.genres_cache,
            'vapiti_year': settings.VAPITI_YEAR,
            'film_link_imdb': 'http://www.imdb.com/title/%s/' % film.imdb_link if film.imdb_link else '',
            'film_link_porthu': 'http://www.port.hu/pls/fi/films.film_page?i_where=2&i_film_id=%s&i_city_id=-1&i_county_id=1' % film.porthu_link if film.porthu_link else '',
            'film_link_rt': 'http://www.rottentomatoes.com/search/?search=' + urlquote_plus(film.orig_title),
            'film_link_youtube': 'http://www.youtube.com/results?search_query=%s+trailer&search=Search' % urlquote_plus(film.orig_title),
            'film_link_wiki_en': film.wikipedia_link_en.strip() if film.wikipedia_link_en else ('http://en.wikipedia.org/w/wiki.phtml?search=' + urlquote_plus(film.orig_title)),
            'film_link_wiki_hu': film.wikipedia_link_hu.strip(),
            'your_rating': rating,
            'your_rating_date': rating_date,
            'ratings': range(1, 6),
            'film_avg_rating_int': int(film.average_rating) if film.average_rating else 0,
            'film_avg_rating_frac': int(10 * (film.average_rating - int(film.average_rating))) if film.average_rating else 0,
            'your_wish_status': your_wish_status,
        }
        return view_function(request, id, film_slug, film, base_context, *args, **kwargs)

    return extended_view_function


@_generic_film_view
def film_main(request, id, film_slug, film, base_context):
    rating = 0
    special_users = set()
    if request.user.is_authenticated():
        special_users.add(request.user.id)
        for friend in request.user.get_follows():
            special_users.add(friend.id)
        try:
            vote = models.Vote.objects.get(film=film, user=request.user)
            rating = vote.rating
        except models.Vote.DoesNotExist:
            pass
    leader_users = set()
    for u in film.vote_set.select_related('user').filter(user__opinion_leader=True).order_by('-user__number_of_followers'):
        if u.user.id not in special_users:
            leader_users.add(u.user.id)
            if len(leader_users) >= 12:
                break
    votes = []
    for idx, r in enumerate(range(5, 0, -1)):
        votes.append(([], []))
        for u in film.vote_set.filter(rating=r).select_related('user').order_by('user__username'):
            if u.user.id in special_users or u.user.id in leader_users:
                votes[idx][0].append(u)
            else:
                votes[idx][1].append(u)

    wish_leader_users = set()
    for wish in models.Wishlist.objects.filter(film=film).select_related('wished_by').filter(wished_by__opinion_leader=True).order_by('-wished_by__number_of_followers'):
        if wish.wished_by_id not in special_users:
            wish_leader_users.add(wish.wished_by_id)
            if len(wish_leader_users) >= 12:
                break
    my_wishes = dict((wish_type[0], False) for wish_type in models.Wishlist.WISH_TYPES)
    all_wishes = dict((wish_type[0], [[], []]) for wish_type in models.Wishlist.WISH_TYPES)
    wish_count = [0, 0]
    for wish in models.Wishlist.objects.filter(film=film).select_related('wished_by').order_by('wished_by__username'):
        if wish.wished_by_id in special_users or wish.wished_by_id in wish_leader_users:
            all_wishes[wish.wish_type][0].append(wish.wished_by)
        else:
            all_wishes[wish.wish_type][1].append(wish.wished_by)
        if wish.wish_type == models.Wishlist.WISH_TYPE_YES:
            wish_count[0] += 1
        if wish.wish_type == models.Wishlist.WISH_TYPE_NO:
            wish_count[1] += 1
        if wish.wished_by_id == request.user.id:
            my_wishes[wish.wish_type] = True

    utls = models.UserToplistItem.objects.filter(film=film).select_related('usertoplist', 'usertoplist__created_by').order_by('-usertoplist__ordered', 'serial_number', 'usertoplist__title', 'usertoplist__id')
    # if request.user.is_authenticated():
    #     recommended_films = list(models.Film.objects.raw(kt_sqls.RECOMMENDED_FILMS_LOGGED_IN.format(film_id=film.id, user_id=request.user.id)))
    # else:
    #     recommended_films = list(models.Film.objects.raw(kt_sqls.RECOMMENDED_FILMS.format(film_id=film.id)))
    recommended_films = list(models.Film.objects.raw(kt_sqls.RECOMMENDED_FILMS.format(film_id=film.id)))
    sequels = []
    for seq in film.all_sequels():
        films, _ = filmlist.filmlist(
            user_id=request.user.id,
            filters=[('sequel', seq.id)],
            ordering='year',
            films_per_page=None,
        )
        sequels.append({
            'sequel': seq,
            'films': films,
        })
    return render(request, 'ktapp/film_subpages/film_main.html', dict(base_context, **{
        'active_tab': 'main',
        'rating': rating,
        'ratings': range(1, 6),
        'roles': film.filmartistrelationship_set.filter(role_type=models.FilmArtistRelationship.ROLE_TYPE_ACTOR).select_related('artist').order_by('role_name'),
        'votes': zip(
            [film.num_specific_rating(r) for r in range(5, 0, -1)],
            votes,
        ),
        'special_users': special_users,
        'my_wishes': my_wishes,
        'wish_count': wish_count,
        'wish_count_sum': wish_count[0] + wish_count[1],
        'all_wishes': all_wishes,
        'recommended_films': recommended_films,
        'utls': utls,
        'premier_types': models.PremierType.objects.all().order_by('name'),
        'other_premiers': film.other_premiers(),
        'sequels': sequels,
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
        'permission_edit_premiers': kt_utils.check_permission('edit_premiers', request.user),
        'permission_new_role': kt_utils.check_permission('new_role', request.user),
        'permission_edit_iszdb': kt_utils.check_permission('edit_iszdb', request.user),
    }))


@_generic_film_view
def film_comments(request, id, film_slug, film, base_context):
    p = int(request.GET.get('p', 0))
    if p == 1:
        return HttpResponseRedirect(reverse('film_comments', args=(film.id, film.slug_cache)))
    max_pages = int(math.ceil(1.0 * film.number_of_comments / COMMENTS_PER_PAGE))
    if max_pages == 0:
        max_pages = 1
    if p == 0:
        p = 1
    if p > max_pages:
        return HttpResponseRedirect(reverse('film_comments', args=(film.id, film.slug_cache)) + '?p=' + str(max_pages))
    comments_qs = film.comment_set.select_related('created_by', 'reply_to', 'reply_to__created_by')
    if max_pages > 1:
        first_comment = film.number_of_comments - COMMENTS_PER_PAGE * (p - 1) - (COMMENTS_PER_PAGE - 1)
        last_comment = film.number_of_comments - COMMENTS_PER_PAGE * (p - 1)
        comments = comments_qs.filter(serial_number__lte=last_comment, serial_number__gte=first_comment)
    else:
        comments = comments_qs.all()
    reply_to_comment = None
    reply_to_id = None
    if request.GET.get('valasz'):
        try:
            reply_to_comment = models.Comment.objects.get(id=request.GET.get('valasz'))
            reply_to_id = reply_to_comment.id
        except models.Comment.DoesNotExist:
            pass
    comment_form = kt_forms.CommentForm(initial={
        'domain': models.Comment.DOMAIN_FILM,
        'film': film,
        'topic': None,
        'poll': None,
        'reply_to': reply_to_id,
    })
    comment_form.fields['domain'].widget = forms.HiddenInput()
    comment_form.fields['film'].widget = forms.HiddenInput()
    comment_form.fields['topic'].widget = forms.HiddenInput()
    comment_form.fields['poll'].widget = forms.HiddenInput()
    comment_form.fields['reply_to'].widget = forms.HiddenInput()
    return render(request, 'ktapp/film_subpages/film_comments.html', dict(base_context, **{
        'active_tab': 'comments',
        'comments': comments,
        'comment_form': comment_form,
        'reply_to_comment': reply_to_comment,
        'p': p,
        'max_pages': max_pages,
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
    }))


@_generic_film_view
def film_quotes(request, id, film_slug, film, base_context):
    quote_form = kt_forms.QuoteForm(initial={'film': film})
    quote_form.fields['film'].widget = forms.HiddenInput()
    return render(request, 'ktapp/film_subpages/film_quotes.html', dict(base_context, **{
        'active_tab': 'quotes',
        'quotes': film.quote_set.all(),
        'quote_form': quote_form,
        'permission_new_quote': kt_utils.check_permission('new_quote', request.user),
        'permission_edit_quote': kt_utils.check_permission('edit_quote', request.user),
        'permission_delete_quote': kt_utils.check_permission('delete_quote', request.user),
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
    }))


@_generic_film_view
def film_trivias(request, id, film_slug, film, base_context):
    trivia_form = kt_forms.TriviaForm(initial={'film': film})
    trivia_form.fields['film'].widget = forms.HiddenInput()
    return render(request, 'ktapp/film_subpages/film_trivias.html', dict(base_context, **{
        'active_tab': 'trivias',
        'trivias': film.trivia_set.all(),
        'trivia_form': trivia_form,
        'permission_new_trivia': kt_utils.check_permission('new_trivia', request.user),
        'permission_edit_trivia': kt_utils.check_permission('edit_trivia', request.user),
        'permission_delete_trivia': kt_utils.check_permission('delete_trivia', request.user),
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
    }))


@_generic_film_view
def film_articles(request, id, film_slug, film, base_context):
    review_form = kt_forms.ReviewForm(initial={'film': film})
    review_form.fields['film'].widget = forms.HiddenInput()
    links = film.link_set.select_related('author')
    return render(request, 'ktapp/film_subpages/film_articles.html', dict(base_context, **{
        'active_tab': 'articles',
        'reviews': film.review_set.filter(approved=True).all(),
        'unapproved_reviews': film.review_set.filter(approved=False).all(),
        'review_form': review_form,
        'permission_new_review': kt_utils.check_permission('new_review', request.user),
        'permission_approve_review': kt_utils.check_permission('approve_review', request.user),
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
        'links_reviews': links.filter(link_type=models.Link.LINK_TYPE_REVIEWS),
        'links_interviews': links.filter(link_type=models.Link.LINK_TYPE_INTERVIEWS),
        'links_official': links.filter(link_type=models.Link.LINK_TYPE_OFFICIAL),
        'links_other': links.filter(link_type=models.Link.LINK_TYPE_OTHER),
        'permission_suggest_link': kt_utils.check_permission('suggest_link', request.user),
        'permission_new_link': kt_utils.check_permission('new_link', request.user),
        'permission_edit_link': kt_utils.check_permission('edit_link', request.user),
        'permission_delete_link': kt_utils.check_permission('delete_link', request.user),
    }))


@_generic_film_view
def film_article(request, id, film_slug, film, base_context, review_id):
    review = get_object_or_404(models.Review, pk=review_id, approved=True)
    if review.film != film:
        raise Http404
    return render(request, 'ktapp/film_subpages/film_article.html', dict(base_context, **{
        'active_tab': 'articles',
        'review': review,
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
    }))


@_generic_film_view
def film_awards(request, id, film_slug, film, base_context):
    return render(request, 'ktapp/film_subpages/film_awards.html', dict(base_context, **{
        'active_tab': 'awards',
        'awards': film.award_set.all().order_by('name', 'year', 'category'),
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
    }))


@_generic_film_view
def film_pictures(request, id, film_slug, film, base_context):
    pictures = sorted(film.picture_set.all(), key=lambda pic: (pic.order_key, pic.id))
    upload_form = kt_forms.PictureUploadForm(initial={'film': film})
    upload_form.fields['film'].widget = forms.HiddenInput()
    context = dict(base_context, **{
        'active_tab': 'pictures',
        'pictures': pictures,
        'upload_form': upload_form,
        'all_artists_in_film': film.artists.filter(filmartistrelationship__role_type=models.FilmArtistRelationship.ROLE_TYPE_ACTOR).all().order_by('name'),
        'permission_new_picture': kt_utils.check_permission('new_picture', request.user),
        'permission_edit_picture': kt_utils.check_permission('edit_picture', request.user),
        'permission_delete_picture': kt_utils.check_permission('delete_picture', request.user),
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
    })
    if len(pictures) == 1:
        next_picture = kt_utils.get_next_picture(pictures, pictures[0])
        context.update(kt_utils.get_selected_picture_details(models.Picture, film, pictures[0], next_picture))
    return render(request, 'ktapp/film_subpages/film_pictures.html', context)


@_generic_film_view
def film_picture(request, id, film_slug, film, base_context, picture_id):
    picture = get_object_or_404(models.Picture, pk=picture_id)
    if picture.film != film:
        raise Http404
    pictures = sorted(film.picture_set.all(), key=lambda pic: (pic.order_key, pic.id))
    next_picture = kt_utils.get_next_picture(pictures, picture)
    upload_form = kt_forms.PictureUploadForm(initial={'film': film})
    upload_form.fields['film'].widget = forms.HiddenInput()
    context = dict(base_context, **{
        'active_tab': 'pictures',
        'pictures': pictures,
        'upload_form': upload_form,
        'all_artists_in_film': film.artists.filter(filmartistrelationship__role_type=models.FilmArtistRelationship.ROLE_TYPE_ACTOR).all().order_by('name'),
        'permission_new_picture': kt_utils.check_permission('new_picture', request.user),
        'permission_edit_picture': kt_utils.check_permission('edit_picture', request.user),
        'permission_delete_picture': kt_utils.check_permission('delete_picture', request.user),
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
    })
    context.update(kt_utils.get_selected_picture_details(models.Picture, film, picture, next_picture))
    return render(request, 'ktapp/film_subpages/film_pictures.html', context)


@_generic_film_view
def film_keywords(request, id, film_slug, film, base_context):
    rating = 0
    if request.user.is_authenticated():
        try:
            vote = models.Vote.objects.get(film=film, user=request.user)
            rating = vote.rating
        except models.Vote.DoesNotExist:
            pass
    major_keywords = models.FilmKeywordRelationship.objects.filter(film=film, keyword__keyword_type=models.Keyword.KEYWORD_TYPE_MAJOR)
    other_keywords = models.FilmKeywordRelationship.objects.filter(film=film, keyword__keyword_type=models.Keyword.KEYWORD_TYPE_OTHER)
    major_and_other_keywords = models.FilmKeywordRelationship.objects.filter(film=film, keyword__keyword_type__in=(models.Keyword.KEYWORD_TYPE_MAJOR, models.Keyword.KEYWORD_TYPE_OTHER))
    if rating == 0:  # hide spoiler keywords
        major_keywords = major_keywords.exclude(spoiler=True)
        other_keywords = other_keywords.exclude(spoiler=True)
        major_and_other_keywords = major_and_other_keywords.exclude(spoiler=True)
    return render(request, 'ktapp/film_subpages/film_keywords.html', dict(base_context, **{
        'active_tab': 'keywords',
        'major_keywords': [(x.keyword, x.spoiler) for x in major_keywords.order_by('keyword__name', 'keyword__id')],
        'other_keywords': [(x.keyword, x.spoiler) for x in other_keywords.order_by('keyword__name', 'keyword__id')],
        'major_and_other_keywords': [(x.keyword, x.spoiler) for x in major_and_other_keywords.order_by('keyword__name', 'keyword__id')],
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
    }))


@login_required
@kt_utils.kt_permission_required('new_film')
def new_film(request):
    if request.POST:
        film_orig_title = kt_utils.strip_whitespace(request.POST.get('film_orig_title', ''))
        if film_orig_title == '':
            return render(request, 'ktapp/new_film.html')
        state_before = {}
        film = models.Film.objects.create(
            orig_title=film_orig_title,
            created_by=request.user,
        )
        film.second_title = kt_utils.strip_whitespace(request.POST.get('film_second_title', ''))
        film.third_title = kt_utils.strip_whitespace(request.POST.get('film_third_title', ''))
        try:
            film_year = int(request.POST.get('film_year', None))
        except ValueError:
            film_year = None
        if film_year == 0:
            film_year = None
        film.year = film_year

        directors = set()
        for director_name in kt_utils.strip_whitespace(request.POST.get('film_directors', '')).split(','):
            director_name = kt_utils.strip_whitespace_and_separator(director_name)
            if director_name == '':
                continue
            director = models.Artist.get_artist_by_name(director_name)
            if director is None:
                director = models.Artist.objects.create(name=director_name)
            directors.add(director)
        for director in directors:
            models.FilmArtistRelationship.objects.create(
                film=film,
                artist=director,
                role_type=models.FilmArtistRelationship.ROLE_TYPE_DIRECTOR,
                created_by=request.user,
            )

        for type_name, type_code in [('countries', 'C'), ('genres', 'G')]:
            new_keywords = set()
            for keyword_name in kt_utils.strip_whitespace(request.POST.get(type_name, '')).split(','):
                keyword_name = kt_utils.strip_whitespace_and_separator(keyword_name)
                if keyword_name.endswith('*'):
                    keyword_name = keyword_name[:-1]
                if not keyword_name:
                    continue
                keyword = models.Keyword.get_keyword_by_name(keyword_name, type_code)
                if keyword:
                    new_keywords.add(keyword.id)
            for keyword_id in new_keywords:
                models.FilmKeywordRelationship.objects.create(
                    film=film,
                    keyword=models.Keyword.objects.get(id=keyword_id),
                    created_by=request.user,
                    spoiler=False,
                )
        film.fix_keywords()

        film.plot_summary = request.POST.get('film_plot', '').strip()

        film_imdb_link = kt_utils.strip_whitespace(request.POST.get('film_imdb_link', ''))
        if film_imdb_link.startswith('tt'):
            film.imdb_link = film_imdb_link
        elif 'imdb.com' in film_imdb_link and '/tt' in film_imdb_link:
            film.imdb_link = film_imdb_link[film_imdb_link.index('/tt')+1:].split('/')[0]
        else:
            film.imdb_link = ''
        film_porthu_link = kt_utils.strip_whitespace(request.POST.get('film_porthu_link', ''))
        if film_porthu_link.isdigit():
            film.porthu_link = film_porthu_link
        elif 'i_film_id' in film_porthu_link:
            try:
                film.porthu_link = int(film_porthu_link[film_porthu_link.index('i_film_id')+10:].split('&')[0])
            except ValueError:
                film.porthu_link = None
        else:
            film.porthu_link = None
        film.wikipedia_link_en = kt_utils.strip_whitespace(request.POST.get('film_wikipedia_link_en', ''))
        film.wikipedia_link_hu = kt_utils.strip_whitespace(request.POST.get('film_wikipedia_link_hu', ''))
        film.save()
        state_after = {
            'orig_title': film.orig_title,
            'second_title': film.second_title,
            'third_title': film.third_title,
            'year': film.year,
            'plot_summary': film.plot_summary,
            'imdb_link': film.imdb_link,
            'porthu_link': film.porthu_link,
            'wikipedia_link_en': film.wikipedia_link_en,
            'wikipedia_link_hu': film.wikipedia_link_hu,
        }
        kt_utils.changelog(
            models.Change,
            request.user,
            'new_film',
            'film:%s' % film.id,
            state_before, state_after
        )
        return HttpResponseRedirect(reverse('film_main', args=(film.id, film.slug_cache)))
    return render(request, 'ktapp/new_film.html')


@login_required
@kt_utils.kt_permission_required('suggest_film')
def suggest_film(request):
    if request.POST:
        film_orig_title = kt_utils.strip_whitespace(request.POST.get('film_orig_title', ''))
        if film_orig_title == '':
            return render(request, 'ktapp/suggest_film.html')
        try:
            film_year = int(request.POST.get('film_year', None))
        except ValueError:
            film_year = None
        if film_year == 0:
            film_year = None

        film_imdb_link = kt_utils.strip_whitespace(request.POST.get('film_imdb_link', ''))
        if film_imdb_link.startswith('tt'):
            film_imdb_link = film_imdb_link
        elif 'imdb.com' in film_imdb_link and '/tt' in film_imdb_link:
            film_imdb_link = film_imdb_link[film_imdb_link.index('/tt')+1:].split('/')[0]
        else:
            film_imdb_link = ''
        film_porthu_link = kt_utils.strip_whitespace(request.POST.get('film_porthu_link', ''))
        if film_porthu_link.isdigit():
            film_porthu_link = film_porthu_link
        elif 'i_film_id' in film_porthu_link:
            try:
                film_porthu_link = int(film_porthu_link[film_porthu_link.index('i_film_id')+10:].split('&')[0])
            except ValueError:
                film_porthu_link = None
        else:
            film_porthu_link = None

        models.SuggestedContent.objects.create(
            created_by=request.user,
            domain=models.SuggestedContent.DOMAIN_FILM,
            content=json.dumps({
                'orig_title': film_orig_title,
                'second_title': kt_utils.strip_whitespace(request.POST.get('film_second_title', '')),
                'third_title': kt_utils.strip_whitespace(request.POST.get('film_third_title', '')),
                'year': film_year,
                'directors': kt_utils.strip_whitespace(request.POST.get('film_directors', '')),
                'countries': kt_utils.strip_whitespace(request.POST.get('countries', '')),
                'genres': kt_utils.strip_whitespace(request.POST.get('genres', '')),
                'plot_summary': request.POST.get('film_plot', '').strip(),
                'imdb_link': film_imdb_link,
                'porthu_link': film_porthu_link,
                'wikipedia_link_en': kt_utils.strip_whitespace(request.POST.get('film_wikipedia_link_en', '')),
                'wikipedia_link_hu': kt_utils.strip_whitespace(request.POST.get('film_wikipedia_link_hu', '')),
            }),
        )

        return HttpResponseRedirect(reverse('suggested_films'))
    return render(request, 'ktapp/suggest_film.html')


def suggested_films(request):

    def get_real_imdb_link(film_imdb_link):
        if film_imdb_link:
            return 'http://www.imdb.com/title/%s/' % film_imdb_link
        return None

    return render(request, 'ktapp/suggested_films.html', {
        'permission_new_film': kt_utils.check_permission('new_film', request.user),
        'films': [
            {
                'id': f.id,
                'created_by': f.created_by,
                'created_at': f.created_at,
                'content': json.loads(f.content),
                'imdb_link': get_real_imdb_link(json.loads(f.content).get('imdb_link', '')),
            }
            for f in models.SuggestedContent.objects.select_related('created_by').filter(domain=models.SuggestedContent.DOMAIN_FILM).order_by('-created_at')
        ],
    })


@login_required
@kt_utils.kt_permission_required('check_missing_data')
def films_with_missing_data(request):
    p = int(request.GET.get('p', 0))
    if p < 1:
        p = 1
    offset_min, offset_max = (p - 1) * 100, p * 100
    miss_type = request.GET.get('tipus', '')
    if miss_type not in {'tortenet', 'plakat', 'szereplok'}:
        miss_type = 'tortenet'
    if miss_type == 'tortenet':
        films = models.Film.objects.filter(plot_summary='').filter(genre_cache_is_short=False).order_by('-number_of_ratings')[offset_min:offset_max]
    elif miss_type == 'plakat':
        films = models.Film.objects.filter(main_poster=None).filter(genre_cache_is_short=False).order_by('-number_of_ratings')[offset_min:offset_max]
    elif miss_type == 'szereplok':
        films = models.Film.objects.filter(genre_cache_is_animation=False, genre_cache_is_short=False, genre_cache_is_docu=False, number_of_actors=0).order_by('-number_of_ratings')[offset_min:offset_max]
    else:
        raise Http404
    return render(request, 'ktapp/films_with_missing_data.html', {
        'active_tab': miss_type,
        'films': films,
        'p': p,
    })
