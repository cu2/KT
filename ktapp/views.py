from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from ktapp.models import Film, Vote


def index(request):
    film_list = Film.objects.all()
    return render(request, "ktapp/index.html", {
        "film_list": film_list,
    })


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


@login_required
def vote(request):
    film = get_object_or_404(Film, pk=request.POST["film_id"])
    try:
        rating = int(request.POST["rating"])
    except ValueError:
        rating = 0
    if rating == 0:
        Vote.objects.filter(film=film, user=request.user).delete()
    elif 1 <= rating <= 5:
        vote, created = Vote.objects.get_or_create(film=film, user=request.user, defaults={"rating": rating})
        vote.rating = rating
        vote.save()
    return HttpResponseRedirect(reverse("film_main", args=(film.pk, film.orig_title)))


def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = UserCreationForm()
    return render(request, "ktapp/registration.html", {
        'form': form,
    })
