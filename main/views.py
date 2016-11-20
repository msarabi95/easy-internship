from accounts.models import Profile
from django.contrib.messages.api import get_messages
from django.shortcuts import render
from main.serializers import MessageSerializer
from rest_framework import views
from rest_framework.response import Response


def index(request):
    """
    Loads the main page.
    """
    if request.GET.get("role") and request.user.is_superuser:
        role = request.GET.get("role")
    else:
        if request.user.has_perm("planner.view_intern_site"):
            role = Profile.INTERN
        elif request.user.has_perm("planner.view_staff_site"):
            role = Profile.STAFF
        else:
            role = "outsider"
    # role = request.GET.get("role") or "intern"
    context = {"role": role}
    return render(request, "index.html", context)


class GetMessages(views.APIView):
    def get(self, request):
        messages = list(get_messages(request))
        serialized = MessageSerializer(messages, many=True)
        return Response(serialized.data)

