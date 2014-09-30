from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

import views

urlpatterns = patterns('',
    url(r'^$', views.rooms, name='rooms'),
    url(r'^login', views.signin, name='login'),
    url(r'^logout', views.signout, name='logout'),
    url(r'^rooms/', include('rooms.urls')),
    url(r'^admin/', include(admin.site.urls)),    
    url(r'^find_rooms/$', views.find_rooms, name='find_rooms'),
    url(r'^confirm_book/$', views.confirm_book, name='confirm_book'),
    url(r'^book/$', views.book, name='book'),
    url(r'^book_form/$', views.book_form, name='book_form'),
    url(r'^find_slots/$', views.find_slots, name='find_slots'),
    url(r'^slots/$', views.slots, name='slots'),
    url(r'^slots/(?P<slot_id>\d+)/$', views.slot_detail, name='slot_detail'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
