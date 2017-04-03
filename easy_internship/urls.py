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

from accounts.views import SignupWrapper
from accounts.forms import EditInternProfileForm, ChangeInternEmailForm
from accounts.urls import api_urls as accounts_urls
from leaves.urls import api_urls as leaves_urls
from rotations.urls import api_urls as rotations_urls
from hospitals.urls import api_urls as hospitals_urls
from months.urls import api_urls as months_urls
from misc.urls import api_urls as misc_urls

from . import views

api_urls = (
    hospitals_urls,
    months_urls,
    rotations_urls,
    accounts_urls,
    leaves_urls,
    misc_urls,
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

    url(r'^planner/', include("rotations.urls")),  # FIXME: update url in front-end
    url(r'^leaves/', include("leaves.urls")),

    url(r'^accounts/activate/(?P<activation_key>\w+)/$', 'userena.views.activate', {'success_url': '/'}),
    url(r'^accounts/(?P<username>[\@\.\w-]+)/email/$', 'userena.views.email_change', {'email_form': ChangeInternEmailForm}),
    url(r'^accounts/(?P<username>[\@\.\w-]+)/edit/$', 'userena.views.profile_edit', {'edit_profile_form': EditInternProfileForm}),
    url(r'^accounts/signup/$', SignupWrapper.as_view()),
    url(r'^accounts/', include('userena.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    # media files (user-uploaded files)
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT})
    ]
