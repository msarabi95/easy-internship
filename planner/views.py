from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import View
from djng.views.mixins import allow_remote_invocation, JSONResponseMixin
from month import Month
from planner.models import Hospital, RequestedDepartment, Department, Specialty


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

    @allow_remote_invocation
    def create_request(self, month, request_data):
        """
        NOTE: This method assumes that no intern will submit more than one plan request at a time.
        """
        # FIXME: Creating multiple requests for the same month should be prevented (at db level)
        # Get or create a plan request
        internship = self.request.user.profile.intern.internship
        plan_request = internship.plan_requests.unsubmitted().last() or internship.plan_requests.create()

        _dept_data = request_data['requested_department']

        if _dept_data['departmentID'] is not None:
            requested_dept_data = {
                'is_in_database': True,
                'department': Department.objects.get(pk=_dept_data['departmentID'])
            }
        else:
            requested_dept_data = {
                'is_in_database': False,
            }
            for key in _dept_data:
                if key.startswith("department_"):
                    requested_dept_data[key] = _dept_data[key]

            requested_dept_data['department_hospital'] = Hospital.objects.get(pk=_dept_data['department_hospitalID'])
            requested_dept_data['department_specialty'] = Specialty.objects.get(pk=_dept_data['department_specialtyID'])
            del requested_dept_data['department_hospitalID']
            del requested_dept_data['department_specialtyID']

        plan_request.rotation_requests.create(
            month=Month.from_int(month),
            specialty=Specialty.objects.get(pk=request_data['specialtyID']),
            requested_department=RequestedDepartment.objects.create(**requested_dept_data),
            delete=request_data['delete'],
        )

        return True

    @allow_remote_invocation
    def update_request(self, month, request_data):
        """
        NOTE: This method assumes that no intern will submit more than one plan request at a time.
        """
        # Get last plan request
        internship = self.request.user.profile.intern.internship
        plan_request = internship.plan_requests.unsubmitted().last()

        rotation_request = plan_request.rotation_requests.get(month=Month.from_int(month))

        _dept_data = request_data['requested_department']

        if _dept_data['departmentID'] is not None:
            requested_dept_data = {
                'is_in_database': True,
                'department': Department.objects.get(pk=_dept_data['departmentID'])
            }
        else:
            requested_dept_data = {
                'is_in_database': False,
            }
            for key in _dept_data:
                if key.startswith("department_"):
                    requested_dept_data[key] = _dept_data[key]

            requested_dept_data['department_hospital'] = Hospital.objects.get(pk=_dept_data['department_hospitalID'])
            requested_dept_data['department_specialty'] = Specialty.objects.get(pk=_dept_data['department_specialtyID'])
            del requested_dept_data['department_hospitalID']
            del requested_dept_data['department_specialtyID']

        rotation_request.specialty = Specialty.objects.get(pk=request_data['specialtyID'])
        rotation_request.delete = request_data['delete']
        rotation_request.save()

        rotation_request.requested_department.__dict__.update(**requested_dept_data)
        rotation_request.requested_department.save()

        return True

    @allow_remote_invocation
    def delete_request(self, month):
        """
        NOTE: This method assumes that no intern will submit more than one plan request at a time.
        """
        # Get last plan request
        internship = self.request.user.profile.intern.internship
        plan_request = internship.plan_requests.unsubmitted().last()

        # rotation_request = plan_request.rotation_requests.get(month=month)
        # rotation_request.delete()
        # FIXME: The following is a workaround to the fact that `delete` field conflicts with the API method `delete()`

        plan_request.rotation_requests.filter(month=Month.from_int(month)).delete()

        return True

    # def _dispatch_super(self, request, *args, **kwargs):
    #     return HttpResponseRedirect(reverse("redirect_to_index", args=("planner/", )))  # FIXME: harcoded url
