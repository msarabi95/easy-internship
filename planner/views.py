from django.contrib import messages
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import View
from planner.serializers import PlanRequestSerializer, RotationRequestSerializer
from rest_framework import viewsets, permissions
from djng.views.mixins import allow_remote_invocation, JSONResponseMixin
from month import Month
from planner.models import Hospital, RequestedDepartment, Department, Specialty, PlanRequest, Internship, \
    RotationRequest
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response


class PlannerAPI(JSONResponseMixin, View):

    def get(self, request, *args, **kwargs):
        self.request = request
        return super(PlannerAPI, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.request = request
        return super(PlannerAPI, self).post(request, *args, **kwargs)

    @allow_remote_invocation
    def get_messages(self):
        return [{
            'message': message.message,
            'level': message.level,
            'tags': message.tags,
            'extra_tags': message.extra_tags,
            'level_tag': message.level_tag,
        } for message in messages.get_messages(self.request)]

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
    def get_specialties_list(self):
        return [{
            "id": specialty.id,
            "name": specialty.name,
        } for specialty in Specialty.objects.all()]

    @allow_remote_invocation
    def create_request(self, request_data):
        """
        NOTE: This method assumes that no intern will submit more than one plan request at a time.
        """
        print request_data
        # FIXME: Creating multiple requests for the same month should be prevented (at db level)
        # Get or create a plan request
        internship = self.request.user.profile.intern.internship
        plan_request = internship.plan_requests.current() or internship.plan_requests.create()

        if plan_request.is_submitted:
            raise PermissionDenied

        month = request_data.pop("month")

        try:
            _dept_data = request_data['requested_department']
        except KeyError:
            # The following assumes that the current month has a rotation (and only one rotation)
            current_dept = internship.rotations.filter(month=Month.from_int(month)).last().department
            request_data['departmentID'] = current_dept.id

        if int(request_data['departmentID']) != -1:
            requested_dept_data = {
                'is_in_database': True,
                'department': Department.objects.get(pk=request_data['departmentID'])
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
            specialty=requested_dept_data['department'].specialty
                        if 'department' in requested_dept_data
                        else requested_dept_data['department_specialty'],
            requested_department=RequestedDepartment.objects.create(**requested_dept_data),
            delete=request_data['delete'],
        )

        return True

    @allow_remote_invocation
    def update_request(self, request_data):
        """
        NOTE: This method assumes that no intern will submit more than one plan request at a time.
        """
        print request_data
        # Get last plan request
        internship = self.request.user.profile.intern.internship
        plan_request = internship.plan_requests.current()

        if plan_request.is_submitted:
            raise PermissionDenied

        month = request_data.pop("month")
        rotation_request = plan_request.rotation_requests.get(month=Month.from_int(month))

        print rotation_request.requested_department.get_department()

        try:
            _dept_data = request_data['requested_department']
        except KeyError:
            # The following assumes that the current month has a rotation (and only one rotation)
            current_dept = internship.rotations.filter(month=Month.from_int(month)).last().department
            request_data['departmentID'] = current_dept.id

        if int(request_data['departmentID']) != -1:
            requested_dept_data = {
                'is_in_database': True,
                'department': Department.objects.get(pk=request_data['departmentID'])
            }

            print requested_dept_data['department']
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

        rotation_request.specialty = requested_dept_data['department'].specialty\
                                     if 'department' in requested_dept_data\
                                     else requested_dept_data['department_specialty']
        rotation_request.delete = request_data['delete']
        rotation_request.save()

        requested_dept = rotation_request.requested_department
        for (attr, value) in requested_dept_data.items():
            setattr(requested_dept, attr, value)
        requested_dept.save()

        print requested_dept.get_department()

        print rotation_request.requested_department.get_department()

        return True

    @allow_remote_invocation
    def delete_request(self, request_data):
        """
        NOTE: This method assumes that no intern will submit more than one plan request at a time.
        """
        # Get last plan request
        internship = self.request.user.profile.intern.internship
        plan_request = internship.plan_requests.current()

        if plan_request.is_submitted:
            raise PermissionDenied

        month = request_data.pop("month")

        # rotation_request = plan_request.rotation_requests.get(month=month)
        # rotation_request.delete()
        # FIXME: The following is a workaround to the fact that `delete` field conflicts with the API method `delete()`

        plan_request.rotation_requests.filter(month=Month.from_int(month)).delete()

        return True

    @allow_remote_invocation
    def submit_plan_request(self):
        # Get last plan request
        internship = self.request.user.profile.intern.internship
        plan_request = internship.plan_requests.current()

        try:
            plan_request.submit()
            messages.success(self.request, "Your plan request has been successfully submitted.")
        except (ValidationError, Exception) as e:
            if isinstance(e, ValidationError):
                for error in e.messages:
                    messages.error(self.request, error)
            else:
                messages.error(self.request, str(e))

        return True

    # def _dispatch_super(self, request, *args, **kwargs):
    #     return HttpResponseRedirect(reverse("redirect_to_index", args=("planner/", )))  # FIXME: harcoded url


class PlanRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PlanRequestSerializer
    queryset = PlanRequest.objects.filter(is_submitted=True)
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class RotationRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RotationRequestSerializer
    queryset = RotationRequest.objects.all()

    @list_route(methods=["post"])
    def respond(self, request):
        pk = request.data.get("id")
        rr = RotationRequest.objects.get(pk=pk)
        rr.respond(request.data.get("is_approved"), request.data.get("comments", ""))
        return Response({"status": RotationRequest.REVIEWED_STATUS, "is_approved": request.data.get("is_approved")})

    @list_route(methods=["post"])
    def forward(self, request):
        pk = request.data.get("id")
        rr = RotationRequest.objects.get(pk=pk)
        rr.forward()
        return Response({"status": RotationRequest.FORWARDED_STATUS})
