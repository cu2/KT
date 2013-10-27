from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django import forms

from ktapp.models import Film, Vote, Comment, Topic, Poll, Artist, FilmArtistRelationship
from ktapp.forms import CommentForm, QuoteForm


def index(request):
    return render(request, "ktapp/index.html", {
        "film_list": Film.objects.all(),
        "topic_list": Topic.objects.all(),
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
    comment_form = CommentForm(initial={
        "domain": Comment.DOMAIN_FILM,
        "film": film,
        "topic": None,
        "poll": None,
        "reply_to": None,
    })
    comment_form.fields["domain"].widget = forms.HiddenInput()
    comment_form.fields["film"].widget = forms.HiddenInput()
    comment_form.fields["topic"].widget = forms.HiddenInput()
    comment_form.fields["poll"].widget = forms.HiddenInput()
    comment_form.fields["reply_to"].widget = forms.HiddenInput()
    quote_form = QuoteForm(initial={
        "film": film,
    })
    quote_form.fields["film"].widget = forms.HiddenInput()
    return render(request, "ktapp/film_main.html", {
        "film": film,
        "rating": rating,
        "ratings": range(1, 6),
        "comments": film.comment_set.all(),
        "comment_form": comment_form,
        "quotes": film.quote_set.all(),
        "quote_form": quote_form,
        "directors": film.artists.filter(filmartistrelationship__role_type=FilmArtistRelationship.ROLE_TYPE_DIRECTOR),
        "roles": film.filmartistrelationship_set.filter(role_type=FilmArtistRelationship.ROLE_TYPE_ACTOR),
    })


def artist(request, id, name):
    artist = get_object_or_404(Artist, pk=id)
    return render(request, "ktapp/artist.html", {
        "artist": artist,
        "directions": artist.filmartistrelationship_set.filter(role_type=FilmArtistRelationship.ROLE_TYPE_DIRECTOR),
        "roles": artist.filmartistrelationship_set.filter(role_type=FilmArtistRelationship.ROLE_TYPE_ACTOR),
    })


def role(request, id, name):
    role = get_object_or_404(FilmArtistRelationship, pk=id)
    return render(request, "ktapp/role.html", {
        "role": role,
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


@login_required
def new_comment(request):  # TODO: extend with poll comments
    domain_type = request.POST["domain"]
    if domain_type == Comment.DOMAIN_FILM:
        domain = get_object_or_404(Film, pk=request.POST["film"])
    elif domain_type == Comment.DOMAIN_TOPIC:
        domain = get_object_or_404(Topic, pk=request.POST["topic"])
    elif domain_type == Comment.DOMAIN_POLL:
        domain = get_object_or_404(Poll, pk=request.POST["poll"])
    else:
        raise Http404
    if request.POST:
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.created_by = request.user
            comment.save(domain=domain)  # Comment model updates domain object
    if domain_type == Comment.DOMAIN_FILM:
        return HttpResponseRedirect(reverse("film_main", args=(domain.pk, domain.orig_title)))
    elif domain_type == Comment.DOMAIN_TOPIC:
        return HttpResponseRedirect(reverse("forum", args=(domain.pk, domain.title)))
    elif domain_type == Comment.DOMAIN_POLL:
        return HttpResponseRedirect(reverse("index"))
    else:
        raise Http404


def forum(request, id, title):
    topic = get_object_or_404(Topic, pk=id)
    comment_form = CommentForm(initial={
        "domain": Comment.DOMAIN_TOPIC,
        "film": None,
        "topic": topic,
        "poll": None,
        "reply_to": None,
    })
    comment_form.fields["domain"].widget = forms.HiddenInput()
    comment_form.fields["film"].widget = forms.HiddenInput()
    comment_form.fields["topic"].widget = forms.HiddenInput()
    comment_form.fields["poll"].widget = forms.HiddenInput()
    comment_form.fields["reply_to"].widget = forms.HiddenInput()
    return render(request, "ktapp/forum.html", {
        "topic": topic,
        "comments": topic.comment_set.all(),
        "comment_form": comment_form,
    })


@login_required
def new_quote(request):
    film = get_object_or_404(Film, pk=request.POST["film"])
    if request.POST:
        quote_form = QuoteForm(data=request.POST)
        if quote_form.is_valid():
            quote = quote_form.save(commit=False)
            quote.created_by = request.user
            quote.save()
    return HttpResponseRedirect(reverse("film_main", args=(film.pk, film.orig_title)))
