from accounts.models import Profile, Intern
from accounts.serializers import ProfileSerializer, InternSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework import viewsets


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()


class InternViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InternSerializer
    queryset = Intern.objects.all()
