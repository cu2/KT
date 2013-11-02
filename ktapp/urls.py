from django.conf.urls import patterns, url
from django.contrib.auth.views import login, logout

from ktapp import views


# urls should be Hungarian SEO compliant
urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    
    url(r'^film/(?P<id>\d+)/(?P<orig_title>.*)/velemenyek$', views.film_comments, name='film_comments'),
    url(r'^film/(?P<id>\d+)/(?P<orig_title>.*)/idezetek$', views.film_quotes, name='film_quotes'),
    url(r'^film/(?P<id>\d+)/(?P<orig_title>.*)/erdekessegek$', views.film_trivias, name='film_trivias'),
    url(r'^film/(?P<id>\d+)/(?P<orig_title>.*)/kulcsszavak$', views.film_keywords, name='film_keywords'),
    url(r'^film/(?P<id>\d+)/(?P<orig_title>.*)$', views.film_main, name='film_main'),
    
    url(r'^szavaz$', views.vote, name='vote'),
    url(r'^kommentel$', views.new_comment, name='new_comment'),
    url(r'^uj_idezet$', views.new_quote, name='new_quote'),
    url(r'^uj_erdekesseg$', views.new_trivia, name='new_trivia'),
    
    url(r'^muvesz/(?P<id>\d+)/(?P<name>.*)$', views.artist, name='artist'),
    url(r'^szereplo/(?P<id>\d+)/(?P<name>.*)$', views.role, name='role'),
    
    url(r'^forum/(?P<id>\d+)/(?P<title>.*)$', views.forum, name='forum'),
    
    url(r'^bejelentkezes/$', login, name='login', kwargs={'template_name': 'ktapp/login.html'}),
    url(r'^tag/$', login, name='user_profile', kwargs={'template_name': 'ktapp/user_profile.html'}),  # TODO: separate own profile and others
    url(r'^kijelentkezes/$', logout, name='logout', kwargs={'next_page': '/'}),
    url(r'^regisztracio/$', views.registration, name='registration'),
)
