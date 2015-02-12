from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'quotekeeper.views.home', name='home'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout/$', 'quotekeeper.views.logout_view', name='logout'),
    url(r'^accounts/register/', CreateView.as_view(template_name='registration/register.html', form_class=UserCreationForm, success_url='/quotes/'), name='register'),
    url(r'^accounts/password_change/', 'django.contrib.auth.views.password_change', {'post_change_redirect': 'password_change_done'},  name='password_change'),
    url(r'^accounts/password_change_done/', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
    url(r'^quotes/', include('quotes.urls', namespace="quotes")),
    url(r'^admin/', include(admin.site.urls)),
)
