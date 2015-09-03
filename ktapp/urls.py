from django.conf import settings
from django.conf.urls import patterns, url, include
from django.conf.urls.static import static
from django.contrib.auth.views import logout
from django.views.generic.base import RedirectView
from rest_framework import routers

from ktapp.views import web_views, api_views
from ktapp.views.web import user_profile as user_profile_views
from ktapp.views.web import post as post_views
from ktapp.views.web import film as film_views
from ktapp.views.web import user as user_views


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
    url(r'^api/autocomplete/users/$', api_views.get_users, name='get_users'),
    url(r'^api/autocomplete/artists/$', api_views.get_artists, name='get_artists'),
    url(r'^api/autocomplete/keywords/$', api_views.get_keywords, name='get_keywords'),
    url(r'^api/autocomplete/films/$', api_views.get_films, name='get_films'),
)


# Web urls (should be Hungarian SEO compliant)

urlpatterns += patterns(
    '',
    url(r'^$', web_views.index, name='index'),

    url(r'^keres/$', web_views.search, name='search'),
    url(r'^bongeszes/$', web_views.browse, name='browse'),
    url(r'^bemutatok/$', web_views.premiers, name='premiers'),
    url(r'^top_filmek/$', web_views.top_films, name='top_films'),

    url(r'^folytatasok/$', web_views.sequels, name='sequels'),
    url(r'^folytatas/(?P<id>\d+)/(?P<title_slug>[^/]*)$', web_views.sequel, name='sequel'),

    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/velemenyek/$', film_views.film_comments, name='film_comments'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/idezetek/$', film_views.film_quotes, name='film_quotes'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/erdekessegek/$', film_views.film_trivias, name='film_trivias'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/kulcsszavak/$', film_views.film_keywords, name='film_keywords'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/elemzesek/$', film_views.film_reviews, name='film_reviews'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/elemzesek/(?P<review_id>\d+)$', film_views.film_review, name='film_review'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/dijak/$', film_views.film_awards, name='film_awards'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/linkek/$', film_views.film_links, name='film_links'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/kepek/$', film_views.film_pictures, name='film_pictures'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/kepek/(?P<picture_id>\d+)$', film_views.film_picture, name='film_picture'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)$', film_views.film_main, name='film_main'),

    url(r'^szavaz$', post_views.vote, name='vote'),
    url(r'^kivan$', post_views.wish, name='wish'),
    url(r'^kommentel$', post_views.new_comment, name='new_comment'),
    url(r'^uj_idezet$', post_views.new_quote, name='new_quote'),
    url(r'^uj_erdekesseg$', post_views.new_trivia, name='new_trivia'),
    url(r'^uj_elemzes$', post_views.new_review, name='new_review'),
    url(r'^uj_kep$', post_views.new_picture, name='new_picture'),
    url(r'^szerk_kep$', post_views.edit_picture, name='edit_picture'),
    url(r'^torol_kep$', post_views.delete_picture, name='delete_picture'),
    url(r'^elemzes_elfogadasa$', post_views.approve_review, name='approve_review'),
    url(r'^elemzes_elutasitasa$', post_views.disapprove_review, name='disapprove_review'),

    url(r'^uj_film$', web_views.new_film, name='new_film'),
    url(r'^szerk_film$', post_views.edit_film, name='edit_film'),
    url(r'^szerk_sztori$', post_views.edit_plot, name='edit_plot'),
    url(r'^szerk_bemutatok$', post_views.edit_premiers, name='edit_premiers'),
    url(r'^szerk_kulcsszavak$', post_views.edit_keywords, name='edit_keywords'),

    url(r'^valtozasok/$', web_views.changes, name='changes'),

    url(r'^muvesz/(?P<id>\d+)/(?P<name_slug>[^/]*)/kepek/$', web_views.artist_pictures, name='artist_pictures'),
    url(r'^muvesz/(?P<id>\d+)/(?P<name_slug>[^/]*)/kepek/(?P<picture_id>\d+)$', web_views.artist_picture, name='artist_picture'),
    url(r'^muvesz/(?P<id>\d+)/(?P<name_slug>[^/]*)$', web_views.artist_main, name='artist'),
    url(r'^szereplo/(?P<id>\d+)/(?P<name_slug>[^/]*)$', web_views.role, name='role'),
    url(r'^uj_szereplo$', post_views.new_role, name='new_role'),
    url(r'^torol_szereplo$', post_views.delete_role, name='delete_role'),
    url(r'^osszevon_muvesz$', post_views.merge_artist, name='merge_artist'),

    url(r'^forum/(?P<id>\d+)/(?P<title_slug>[^/]*)$', web_views.forum, name='forum'),
    url(r'^forum/$', web_views.list_of_topics, name='list_of_topics'),
    url(r'^uj_topik$', post_views.new_topic, name='new_topic'),
    url(r'^legfrissebb_kommentek/$', web_views.latest_comments, name='latest_comments'),
    url(r'^kedvencek/$', web_views.favourites, name='favourites'),

    url(r'^felhasznaloi_toplista/(?P<id>\d+)/(?P<title_slug>[^/]*)$', web_views.usertoplist, name='usertoplist'),
    url(r'^felhasznaloi_toplistak/$', web_views.usertoplists, name='usertoplists'),

    url(r'^kozkerdes/(?P<id>\d+)/(?P<title_slug>[^/]*)$', web_views.poll, name='poll'),
    url(r'^kozkerdesek/$', web_views.polls, name='polls'),
    url(r'^kozkerdesre_szavaz$', post_views.poll_vote, name='poll_vote'),
    url(r'^kozkerdest_archival', post_views.poll_archive, name='poll_archive'),
    url(r'^kozkerdest_aktival', post_views.poll_activate, name='poll_activate'),
    url(r'^kozkerdest_tamogat', post_views.poll_support, name='poll_support'),
    url(r'^uj_kozkerdes', post_views.new_poll, name='new_poll'),

    url(r'^elemzesek/$', web_views.list_of_reviews, name='list_of_reviews'),
    url(r'^portrek/$', web_views.list_of_bios, name='list_of_bios'),
    url(r'^kepek/$', web_views.latest_pictures, name='latest_pictures'),
    url(r'^idezetek/$', web_views.latest_quotes, name='latest_quotes'),
    url(r'^erdekessegek/$', web_views.latest_trivias, name='latest_trivias'),

    url(r'^user/(?P<id>\d+)/(?P<name_slug>[^/]*)/filmek/$', user_profile_views.user_films, name='user_films'),
    url(r'^user/(?P<id>\d+)/(?P<name_slug>[^/]*)/kommentek/$', user_profile_views.user_comments, name='user_comments'),
    url(r'^user/(?P<id>\d+)/(?P<name_slug>[^/]*)/kivansagok/$', user_profile_views.user_wishlist, name='user_wishlist'),
    url(r'^user/(?P<id>\d+)/(?P<name_slug>[^/]*)/toplistak/$', user_profile_views.user_toplists, name='user_toplists'),
    url(r'^user/(?P<id>\d+)/(?P<name_slug>[^/]*)/aktivitas/$', user_profile_views.user_activity, name='user_activity'),
    url(r'^user/(?P<id>\d+)/(?P<name_slug>[^/]*)/uzenetek/$', user_profile_views.user_messages, name='user_messages'),
    url(r'^user/(?P<id>\d+)/(?P<name_slug>[^/]*)$', user_profile_views.user_profile, name='user_profile'),

    url(r'^jelszo_modositasa$', user_views.change_password, name='change_password'),
    url(r'^bejelentkezes$', user_views.custom_login, name='login'),
    url(r'^kijelentkezes$', logout, name='logout'),
    url(r'^regisztracio$', user_views.registration, name='registration'),
    url(r'^email_ellenorzes/(?P<token>.*)$', user_views.verify_email, name='verify_email'),
    url(r'^jelszo_reset/(?P<token>.*)$', user_views.reset_password, name='reset_password'),

    url(r'^uzik/$', user_views.messages, name='messages'),
    url(r'^uj_uzenet$', user_views.new_message, name='new_message'),
    url(r'^torol_uzenet$', post_views.delete_message, name='delete_message'),

    url(r'^uj_kedvenc$', post_views.follow, name='follow'),
    url(r'^torol_kedvenc$', post_views.unfollow, name='unfollow'),

    # legacy redirects:
    url(r'^[^.]*.php$', web_views.old_url, name='old_url'),  # old php urls
    url(r'^tag/(?P<id>\d+)/(?P<name_slug>[^/]*)/filmek/$', RedirectView.as_view(pattern_name='user_films')),
    url(r'^tag/(?P<id>\d+)/(?P<name_slug>[^/]*)/kommentek/$', RedirectView.as_view(pattern_name='user_comments')),
    url(r'^tag/(?P<id>\d+)/(?P<name_slug>[^/]*)/kivansagok/$', RedirectView.as_view(pattern_name='user_wishlist')),
    url(r'^tag/(?P<id>\d+)/(?P<name_slug>[^/]*)/uzenetek/$', RedirectView.as_view(pattern_name='user_messages')),
    url(r'^tag/(?P<id>\d+)/(?P<name_slug>[^/]*)$', RedirectView.as_view(pattern_name='user_profile')),
)


# Static

if settings.DEBUG:  # in production webserver should serve these
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
