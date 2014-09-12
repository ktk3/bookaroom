from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bookaroom.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', views.rooms, name='rooms'),
    url(r'^login', views.signin, name='login'),
    url(r'^logout', views.signout, name='logout'),
    url(r'^rooms/', include('rooms.urls')),
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
