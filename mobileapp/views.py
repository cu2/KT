import json
import time

from django.shortcuts import render
from django.http import HttpResponse, Http404

from kt import settings
from ktapp import models


def json_response(response_object):
    return HttpResponse(json.dumps(response_object), content_type='application/json')


def index(request):
    return render(request, 'mobileapp/index.html')


def api(request):
    if settings.ENV == 'local':
        time.sleep(0.5)
    page = request.GET.get('page', 'search')
    if page == 'film':
        try:
            film_id = int(request.GET.get('film_id', ''))
        except ValueError:
            film_id = 0
        try:
            film = models.Film.objects.get(id=film_id)
        except models.Film.DoesNotExist:
            raise Http404
        return json_response({
            'filmId': film.id,
            'filmData': {
                'id': film.id,
                'origTitle': film.orig_title,
                'secondTitle': film.second_title,
                'year': film.year,
                'plot': film.plot_summary,
                'poster': film.main_poster.get_display_url('mid') if film.main_poster else '',
            },
        })
    search_domain = request.GET.get('domain', 'film')
    if search_domain not in {'', 'film'}:
        raise Http404
    if search_domain == '':  # index
        return json_response([
            {
                'id': film.id,
                'origTitle': film.orig_title,
                'year': film.year,
                'plot': film.plot_summary,
                'poster': film.main_poster.get_display_url('min') if film.main_poster else '',
            } for film in models.Film.objects.all().order_by('-number_of_ratings')[:20]
        ])
    if search_domain == 'film':
        search_title = request.GET.get('title', '')
        film_qs = models.Film.objects.all()
        if search_title:
            film_qs = film_qs.filter(orig_title__icontains=search_title)
        return json_response([
            {
                'id': film.id,
                'origTitle': film.orig_title,
                'year': film.year,
                'plot': film.plot_summary,
                'poster': film.main_poster.get_display_url('min') if film.main_poster else '',
            } for film in film_qs.order_by('-number_of_ratings')[:20]
        ])
