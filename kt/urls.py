from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('ktapp.urls')),
    url(r'^m/', include('mobileapp.urls')),
]
