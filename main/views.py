from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render


def index(request):
    """
    Loads the main page.
    """
    return render(request, "starter.html")


def redirect_to_index(request, url):
    """
    Redirects all non-ajax requests to the index view, so that urls can be handled by
    Angular.js
    """
    if not request.is_ajax():
        return HttpResponseRedirect("%s#/%s" % (reverse("index"), url))