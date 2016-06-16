from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render


def index(request):
    """
    Loads the main page.
    """
    role = request.GET.get("role") or "intern"
    context = {"role": role}
    return render(request, "index.html", context)


def load_partial(request, template_name):
    """
    Renders and returns the specified template. Raises 404 if the template is not found.
    """
    return render(request, "partials/test-partial.html")


def redirect_to_index(request, url):
    """
    Redirects all non-ajax requests to the index view, so that urls can be handled by
    Angular.js
    """
    if not request.is_ajax():
        return HttpResponseRedirect("%s#/%s" % (reverse("index"), url))
