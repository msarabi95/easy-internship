from accounts import views

urls = (
    (r'users', views.UserViewSet),
    (r'profiles', views.ProfileViewSet),
    (r'interns', views.InternViewSet),
)
