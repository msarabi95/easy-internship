from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.template.exceptions import TemplateDoesNotExist


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
