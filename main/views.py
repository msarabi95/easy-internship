from accounts.models import Profile
from django.contrib.messages.api import get_messages
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.template.exceptions import TemplateDoesNotExist
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


def load_partial(request, template_name):
    """
    Renders and returns the specified template. Raises 404 if the template is not found.
    """
    try:
        return render(request, template_name)
    except TemplateDoesNotExist:
        raise Http404


def redirect_to_index(request, url):
    """
    Redirects all non-ajax requests to the index view, so that urls can be handled by
    Angular.js
    """
    if not request.is_ajax():
        return HttpResponseRedirect("%s#/%s" % (reverse("index"), url))


class GetMessages(views.APIView):
    def get(self, request):
        messages = list(get_messages(request))
        serialized = MessageSerializer(messages, many=True)
        return Response(serialized.data)

