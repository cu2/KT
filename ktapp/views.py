from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django import forms

from ktapp.models import Film, Vote, Comment, Topic, Poll
from ktapp.forms import CommentForm


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
    return render(request, "ktapp/film_main.html", {
        "film": film,
        "rating": rating,
        "ratings": range(1, 6),
        "comments": film.comment_set.all(),
        "comment_form": comment_form,
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
def new_comment(request):  # TODO: extend with topic and poll comments
    if request.POST["domain"] == Comment.DOMAIN_FILM:
        film = get_object_or_404(Film, pk=request.POST["film"])
    elif request.POST["domain"] == Comment.DOMAIN_TOPIC:
        topic = get_object_or_404(Topic, pk=request.POST["topic"])
    elif request.POST["domain"] == Comment.DOMAIN_POLL:
        poll = get_object_or_404(Poll, pk=request.POST["poll"])
    else:
        raise Http404
    if request.POST:
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.created_by = request.user
            comment.save()
    if request.POST["domain"] == Comment.DOMAIN_FILM:
        return HttpResponseRedirect(reverse("film_main", args=(film.pk, film.orig_title)))
    elif request.POST["domain"] == Comment.DOMAIN_TOPIC:
        return HttpResponseRedirect(reverse("index"))
    elif request.POST["domain"] == Comment.DOMAIN_POLL:
        return HttpResponseRedirect(reverse("index"))
    else:
        raise Http404
