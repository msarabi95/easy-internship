from rest_framework import viewsets, permissions
from misc.models import Announcement
from misc.serializers import AnnouncementSerializer
from rest_framework.response import Response
from rest_framework.decorators import list_route
from accounts.permissions import IsStaffOrReadOnly,IsStaff
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = (permissions.IsAuthenticated,IsStaffOrReadOnly)

#    def create(self, request, *args, **kwargs):
#    supoosed to overwrite author

    def update(self, request, *args, **kwargs):
        instance=Announcement(pk=request.pk)
        published=request.query_params['published']
        if request.data['published'] == False and instance.published == True:
            raise PermissionDenied (' did not know what to write here ')

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


#overwrite author in creat last updated by in update
# overwrite create and update for the date time and puplished
#list routs for puplished and drafts
#custom permission
