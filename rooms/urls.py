from django.conf.urls import patterns, url

from rooms import views

urlpatterns = patterns('',
    # ex: /rooms/
    url(r'^$', views.index, name='index'),
    # ex: /polls/English/results/
    url(r'^(?P<room_id>\d+)/results/$', views.results, name='results'),
    # ex: /rooms/5/
    url(r'^(?P<room_id>\d+)/$', views.detail, name='detail'),
    # matches every string
    url(r'^(?P<room_name>[^/]+)/$', views.detail2, name='detail2'),
    url(r'^(?P<room_id>\d+)/book_a_room/$', views.book_a_room, name='book_a_room'),

)

