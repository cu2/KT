from django.conf.urls import patterns, url
from django.contrib.auth.views import login, logout

from ktapp import views


urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^film/(?P<id>\d+)/(?P<orig_title>.*)$', views.film_main, name='film_main'),
    url(r'^vote$', views.vote, name='vote'),
    url(r'^accounts/login/$', login, name='login', kwargs={'template_name': 'ktapp/login.html'}),
    url(r'^accounts/profile/$', login, name='user_profile', kwargs={'template_name': 'ktapp/user_profile.html'}),
    url(r'^accounts/logout/$', logout, name='logout', kwargs={'next_page': '/'}),
)
