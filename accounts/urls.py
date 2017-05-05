from accounts import views

api_urls = (
    (r'users', views.UserViewSet),
    (r'profiles', views.ProfileViewSet),
    (r'interns', views.InternViewSet),
    (r'batches', views.BatchViewSet),
)
