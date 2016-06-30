from django.conf.urls import url
from planner import views

urlpatterns = [
    url(r'^$', views.PlannerAPI.as_view(), name="planner_api"),
]