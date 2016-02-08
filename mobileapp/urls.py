from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from mobileapp import views


urlpatterns = [
    url(r'^$', views.index, name='mobile_index'),
    url(r'^api/$', views.api, name='mobile_api'),
]


# Static

if settings.DEBUG:  # in production webserver should serve these
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
