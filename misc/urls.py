from misc import views
api_urls = (
    (r'^announcements/$', views.AnnouncementsViewSet,'announcements'),
    (r'^users/$', views.UserViewSet),
)