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
from django.conf.urls import include, url
from django.contrib import admin
from planner import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'plan_requests', views.PlanRequestViewSet)
router.register(r'rotation_requests', views.RotationRequestViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^planner/', include("planner.urls", namespace="planner")),
    url(r'^partials/(?P<template_name>.*\.html)$', "main.views.load_partial", name="load_partial"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', "main.views.index", name="index"),
    # url(r'^(?P<url>.*)', "main.views.redirect_to_index", name="redirect_to_index")
]
