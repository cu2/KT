from django.conf import settings
from django.conf.urls import patterns, url, include
from django.conf.urls.static import static
from django.contrib.auth.views import login, logout
from rest_framework import routers

from ktapp.views import web_views, api_views


# API urls

router = routers.DefaultRouter()
router.register(r'users', api_views.UserViewSet)
router.register(r'films', api_views.FilmViewSet)
router.register(r'keywords', api_views.KeywordViewSet)
router.register(r'artists', api_views.ArtistViewSet)
router.register(r'sequels', api_views.SequelViewSet)

urlpatterns = patterns(
    '',
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # custom api endpoints:
    url(r'^api/autocomplete/users$', api_views.get_users, name='get_users'),
    url(r'^api/autocomplete/artists$', api_views.get_artists, name='get_artists'),
    url(r'^api/autocomplete/keywords$', api_views.get_keywords, name='get_keywords'),
)


# Web urls (should be Hungarian SEO compliant)

urlpatterns += patterns(
    '',
    url(r'^$', web_views.index, name='index'),

    url(r'^keres$', web_views.search, name='search'),

    url(r'^film/(?P<id>\d+)/(?P<film_slug>.*)/velemenyek$', web_views.film_comments, name='film_comments'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>.*)/idezetek$', web_views.film_quotes, name='film_quotes'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>.*)/erdekessegek$', web_views.film_trivias, name='film_trivias'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>.*)/kulcsszavak$', web_views.film_keywords, name='film_keywords'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>.*)/elemzesek$', web_views.film_reviews, name='film_reviews'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>.*)/elemzes/(?P<review_id>\d+)$', web_views.film_review, name='film_review'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>.*)/dijak$', web_views.film_awards, name='film_awards'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>.*)/linkek$', web_views.film_links, name='film_links'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>.*)/kepek$', web_views.film_pictures, name='film_pictures'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>.*)/kepek/(?P<picture_id>\d+)$', web_views.film_picture, name='film_picture'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>.*)$', web_views.film_main, name='film_main'),

    url(r'^szavaz$', web_views.vote, name='vote'),
    url(r'^kivan$', web_views.wish, name='wish'),
    url(r'^kommentel$', web_views.new_comment, name='new_comment'),
    url(r'^uj_idezet$', web_views.new_quote, name='new_quote'),
    url(r'^uj_erdekesseg$', web_views.new_trivia, name='new_trivia'),
    url(r'^uj_elemzes$', web_views.new_review, name='new_review'),
    url(r'^uj_kep$', web_views.new_picture, name='new_picture'),
    url(r'^szerk_kep$', web_views.edit_picture, name='edit_picture'),
    url(r'^torol_kep$', web_views.delete_picture, name='delete_picture'),

    url(r'^szerk_film$', web_views.edit_film, name='edit_film'),
    url(r'^szerk_sztori$', web_views.edit_plot, name='edit_plot'),
    url(r'^szerk_bemutatok$', web_views.edit_premiers, name='edit_premiers'),
    url(r'^szerk_kulcsszavak$', web_views.edit_keywords, name='edit_keywords'),

    url(r'^muvesz/(?P<id>\d+)/(?P<name_slug>.*)$', web_views.artist, name='artist'),
    url(r'^szereplo/(?P<id>\d+)/(?P<name_slug>.*)$', web_views.role, name='role'),
    url(r'^uj_szereplo$', web_views.new_role, name='new_role'),
    url(r'^torol_szereplo$', web_views.delete_role, name='delete_role'),
    url(r'^osszevon_muvesz$', web_views.merge_artist, name='merge_artist'),

    url(r'^forum/(?P<id>\d+)/(?P<title_slug>.*)$', web_views.forum, name='forum'),
    url(r'^forum/$', web_views.list_of_topics, name='list_of_topics'),
    url(r'^uj_topik$', web_views.new_topic, name='new_topic'),
    url(r'^legfrissebb_kommentek$', web_views.latest_comments, name='latest_comments'),

    url(r'^tag/(?P<id>\d+)/(?P<name_slug>.*)$', web_views.user_profile, name='user_profile'),
    url(r'^jelszo_modositasa/$', web_views.change_password, name='change_password'),
    url(r'^bejelentkezes/$', web_views.custom_login, name='login'),
    url(r'^kijelentkezes/$', logout, name='logout'),
    url(r'^regisztracio/$', web_views.registration, name='registration'),
    url(r'^email_ellenorzes/(?P<token>.*)$', web_views.verify_email, name='verify_email'),
    url(r'^jelszo_reset/(?P<token>.*)$', web_views.reset_password, name='reset_password'),

    url(r'^uzik/$', web_views.messages, name='messages'),
    url(r'^uj_uzenet$', web_views.new_message, name='new_message'),
)


# Static

if settings.DEBUG:  # in production webserver should serve these
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
