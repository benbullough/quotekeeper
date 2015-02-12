from django.conf.urls import patterns, url

from quotes import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^add/$', views.add, name='add'),
    url(r'^new/$', views.new, name='new'),
    url(r'^(?P<quote_id>\d+)/$', views.detail, name='detail'),
    url(r'^(?P<quote_id>\d+)/edit/$', views.edit, name='edit'),
    url(r'^(?P<quote_id>\d+)/delete/$', views.delete, name='delete'),
)


