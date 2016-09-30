from rest_framework import routers
from accounts import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'profiles', views.ProfileViewSet)
router.register(r'interns', views.InternViewSet)