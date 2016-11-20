"""easy_internship URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django_nyt.urls import get_pattern as get_nyt_pattern
from rest_framework import routers

from accounts.forms import InternSignupForm, EditInternProfileForm
from accounts.urls import urls as accounts_urls
from leaves.urls import urls as leaves_urls
from planner.urls import urls as planner_urls

from . import views

api_urls = (
    planner_urls,
    accounts_urls,
    leaves_urls,
)

router = routers.DefaultRouter()
for app in api_urls:
    for urlconf in app:
        router.register(*urlconf)


urlpatterns = [
    url(r'^$', views.index, name="index"),

    url(r'^api/', include(router.urls)),
    url(r'^messages/$', views.GetMessages.as_view()),
    url(r'^notifications/', get_nyt_pattern()),

    url(r'^planner/', include("planner.urls")),
    url(r'^leaves/', include("leaves.urls")),

    url(r'^accounts/(?P<username>[\@\.\w-]+)/edit/$', 'userena.views.profile_edit', {'edit_profile_form': EditInternProfileForm}),
    url(r'^accounts/signup/$', 'userena.views.signup', {'signup_form': InternSignupForm}),
    url(r'^accounts/', include('userena.urls')),

    url(r'^admin/', include(admin.site.urls)),
]

if settings.DEBUG:
    # media files (user-uploaded files)
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT})
    ]
