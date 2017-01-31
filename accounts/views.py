from rest_framework.decorators import list_route
from rest_framework.response import Response

from accounts.models import Profile, Intern
from accounts.permissions import IsStaff
from accounts.serializers import ProfileSerializer, InternSerializer, UserSerializer, InternTableSerializer
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("accounts.user.view_all"):
            return self.queryset.all()
        return self.queryset.filter(username=self.request.user.username)


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("accounts.profile.view_all"):
            return self.queryset.all()
        return self.queryset.filter(user=self.request.user)


class InternViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InternSerializer
    queryset = Intern.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("accounts.intern.view_all"):
            return self.queryset.all()
        return self.queryset.filter(profile__user=self.request.user)

    @list_route(methods=['get'], permission_classes=[permissions.IsAuthenticated, IsStaff])
    def as_table(self, request, *args, **kwargs):
        interns = self.queryset.all().prefetch_related('profile__user', 'internship')
        serialized = InternTableSerializer(interns, many=True)
        return Response(serialized.data)

