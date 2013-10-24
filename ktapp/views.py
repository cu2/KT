from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from ktapp.models import Film, Vote


def index(request):
    film_list = Film.objects.all()
    return render(request, "ktapp/index.html", {"film_list": film_list})


def film_main(request, id, orig_title):
    film = get_object_or_404(Film, pk=id)
    rating = 0
    if request.user.is_authenticated():
        try:
            vote = Vote.objects.get(film=film, user=request.user)
            rating = vote.rating
        except Vote.DoesNotExist:
            pass
    return render(request, "ktapp/film_main.html", {
        "film": film,
        "rating": rating,
        "ratings": range(1, 6),
    })


def vote(request):  # TODO: implement this
    film = get_object_or_404(Film, pk=request.POST["film_id"])
    return HttpResponseRedirect(reverse("film_main", args=(film.pk, film.orig_title)))
