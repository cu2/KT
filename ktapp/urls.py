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

urlpatterns = patterns('',
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)


# Web urls (should be Hungarian SEO compliant)

urlpatterns += patterns('',
    url(r'^$', web_views.index, name='index'),
    
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
    url(r'^kommentel$', web_views.new_comment, name='new_comment'),
    url(r'^uj_idezet$', web_views.new_quote, name='new_quote'),
    url(r'^uj_erdekesseg$', web_views.new_trivia, name='new_trivia'),
    url(r'^uj_elemzes$', web_views.new_review, name='new_review'),
    url(r'^uj_kep$', web_views.new_picture, name='new_picture'),
    
    url(r'^muvesz/(?P<id>\d+)/(?P<name_slug>.*)$', web_views.artist, name='artist'),
    url(r'^szereplo/(?P<id>\d+)/(?P<name_slug>.*)$', web_views.role, name='role'),
    
    url(r'^forum/(?P<id>\d+)/(?P<title_slug>.*)$', web_views.forum, name='forum'),
    url(r'^forum$', web_views.list_of_topics, name='list_of_topics'),
    url(r'^uj_topik$', web_views.new_topic, name='new_topic'),
    url(r'^legfrissebb_kommentek$', web_views.latest_comments, name='latest_comments'),
    
    url(r'^tag/(?P<id>\d+)/(?P<name_slug>.*)$', web_views.user_profile, name='user_profile'),
    url(r'^en/$', login, name='user_profile_own', kwargs={'template_name': 'ktapp/user_profile_own.html'}),
    url(r'^bejelentkezes/$', login, name='login', kwargs={'template_name': 'ktapp/login.html'}),
    url(r'^kijelentkezes/$', logout, name='logout', kwargs={'next_page': '/'}),
    url(r'^regisztracio/$', web_views.registration, name='registration'),
)


# Static

if settings.DEBUG:  # in production webserver should serve these
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
