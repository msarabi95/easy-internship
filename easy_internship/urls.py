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

from accounts.forms import InternSignupForm, EditInternProfileForm
from main import views as main_views
from planner import views
from planner.urls import router as planner_router, custom_departments_view_url, custom_internship_months_view_url, \
    acceptance_settings_by_department_and_month_id
from accounts.urls import router as accounts_router

urlpatterns = [
    url(r'^forwards/$', views.list_forwards, name="list_forwards"),  # Temporary, for testing only!
    url(r'^rotation_request_responses/$', views.rotation_request_responses, name="rotation_request_responses"),

    custom_departments_view_url,
    custom_internship_months_view_url,
    acceptance_settings_by_department_and_month_id,
    url(r'^api/', include(planner_router.urls)),
    url(r'^api/', include(accounts_router.urls)),

    url(r'^partials/(?P<template_name>.*\.html)$', "main.views.load_partial", name="load_partial"),

    url(r'^planner/', include("planner.urls")),

    url(r'^accounts/(?P<username>[\@\.\w-]+)/edit/$', 'userena.views.profile_edit', {'edit_profile_form': EditInternProfileForm}),
    url(r'^accounts/signup/$', 'userena.views.signup', {'signup_form': InternSignupForm}),
    url(r'^accounts/', include('userena.urls')),

    url(r'^messages/$', main_views.GetMessages.as_view()),
    url(r'^notifications/', get_nyt_pattern()),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', "main.views.index", name="index"),
    # url(r'^(?P<url>.*)', "main.views.redirect_to_index", name="redirect_to_index")
]

if settings.DEBUG:
    # media files (user-uploaded files)
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT})
    ]
