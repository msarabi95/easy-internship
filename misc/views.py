from rest_framework import viewsets, permissions
from misc.models import Announcement
from misc.serializers import AnnouncementSerializer
from rest_framework.response import Response
from rest_framework.decorators import list_route
from accounts.permissions import IsStaffOrReadOnly,IsStaff
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.utils import timezone


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = (permissions.IsAuthenticated,IsStaffOrReadOnly)


    @list_route(methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def published(self, request, *args, **kwargs):
        announcement = Announcement.objects.published.all()
        serialized = self.get_serializer(announcement, many=True)
        return Response(serialized.data)

    @list_route(methods=['get'], permission_classes=[permissions.IsAuthenticated,IsStaff])
    def draft(self, request, *args, **kwargs):
        announcement = Announcement.objects.draft.all()
        serialized = self.get_serializer(announcement, many=True)
        return Response(serialized.data)

