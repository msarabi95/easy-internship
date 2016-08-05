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
from accounts.forms import InternSignupForm, EditInternProfileForm
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from planner import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'plan_requests', views.PlanRequestViewSet)
router.register(r'rotation_requests', views.RotationRequestViewSet)
router.register(r'rotation_request_forwards', views.RotationRequestForwardViewSet)

urlpatterns = [
    url(r'forwards/$', views.list_forwards, name="list_forwards"),  # Temporary, for testing only!
    url(r'^api/', include(router.urls)),
    url(r'^planner/', include("planner.urls", namespace="planner")),
    url(r'^partials/(?P<template_name>.*\.html)$', "main.views.load_partial", name="load_partial"),

    url(r'^accounts/(?P<username>[\@\.\w-]+)/edit/$', 'userena.views.profile_edit', {'edit_profile_form': EditInternProfileForm}),
    url(r'^accounts/signup/$', 'userena.views.signup', {'signup_form': InternSignupForm}),
    url(r'^accounts/', include('userena.urls')),

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
