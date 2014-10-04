from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'app.views.home', name = 'home'),
    url(r'^signin/$', 'app.views.signin', name = 'signin'),
    url(r'^signup/$', 'app.views.signup', name = 'signup'),
    url(r'^dashboard/$', 'app.views.dashboard', name = 'dashboard'),
    url(r'^browsetool/$', 'app.views.browsetool', name = 'browsetool'),
    url(r'^Borrow/$', 'app.views.Borrow', name = 'Borrow'),
)
