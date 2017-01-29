from django.shortcuts import render
from rest_framework import viewsets, permissions
from misc.models import Announcements
from misc.serializers import AnnouncementsSerializer,UserSerializer
from rest_framework.decorators import detail_route , list_route
from rest_framework import generics

from django.contrib.auth.models import User
from accounts.permissions import IsIntern, IsStaff

class AnnouncementsViewSet(viewsets.ModelViewSet):
    queryset = Announcements.objects.all()
    serializer_class = AnnouncementsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,IsStaff,IsIntern)


@detail_route(methods=["get", "post" ,"put"],permission_classes=[permissions.IsAuthenticated, IsStaff])
@list_route(methods=["get"],permission_classes=[permissions.IsAuthenticated, IsIntern])


class AnnouncementsList(generics.ListCreateAPIView):
    queryset = Announcements.objects.all()
    serializer_class = AnnouncementsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class AnnouncementsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Announcements.objects.all()
    serializer_class = AnnouncementsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,IsStaff)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Create your views here.
# class AnnouncementsList (APIView):
#
#     def get(self, request, format=None):
#         announcements = Announcements.objects.all()
#         serializer = AnnouncementsSerializer(announcements, many=True)
#         return Response(serializer.data)
#
#     def post(self, request, format=None):
#         serializer = AnnouncementsSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
#
# class AnnouncementsDetails (APIView):
#
#     def get_object(self, pk):
#         try:
#             return Announcements.objects.get(pk=pk)
#         except Announcements.DoesNotExist:
#             raise Http404
#
#     def get(self, request, pk, format=None):
#         announcements= self.get_object(pk)
#         serializer = AnnouncementsSerializer(announcements)
#         return Response(serializer.data)
#
#     def put(self, request, pk, format=None):
#         announcements = self.get_object(pk)
#         serializer = AnnouncementsSerializer(announcements, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk, format=None):
#         announcements = self.get_object(pk)
#         announcements.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)