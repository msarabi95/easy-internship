from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import View
from djng.views.mixins import allow_remote_invocation, JSONResponseMixin
from planner.models import Hospital


class PlannerAPI(JSONResponseMixin, View):

    def get(self, request, *args, **kwargs):
        self.request = request
        return super(PlannerAPI, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.request = request
        return super(PlannerAPI, self).post(request, *args, **kwargs)

    @allow_remote_invocation
    def get_internship_info(self):
        return self.request.user.profile.intern.internship.get_internship_info()

    @allow_remote_invocation
    def get_possible_months(self):
        return self.request.user.profile.intern.internship.get_internship_months()

    @allow_remote_invocation
    def get_hospitals_list(self):

        def get_departments_dict(hospital):
            departments = []
            for department in hospital.departments.all():
                departments.append({
                    "id": department.id,
                    "name": department.name,
                })
            return departments

        hospitals = []
        for hospital in Hospital.objects.all():
            hospitals.append({
                "id": hospital.id,
                "name": hospital.name,
                "abbreviation": hospital.abbreviation,
                "departments": get_departments_dict(hospital),
            })
        return hospitals

    # def _dispatch_super(self, request, *args, **kwargs):
    #     return HttpResponseRedirect(reverse("redirect_to_index", args=("planner/", )))  # FIXME: harcoded url
