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
    page = request.GET.get('page', 'index')
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
                'year': film.year,
                'plot': film.plot_summary,
            },
        })
    return json_response({
        'listOfFilms': [
            {
                'id': film.id,
                'origTitle': film.orig_title,
                'year': film.year,
                'plot': film.plot_summary,
            } for film in models.Film.objects.all().order_by('-number_of_ratings')[:10]
        ],
    })
