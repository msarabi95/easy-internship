from accounts.models import Profile
from django.contrib import messages
from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View
from planner.serializers import RotationRequestSerializer, RotationRequestForwardSerializer, \
    InternshipMonthSerializer, HospitalSerializer, SpecialtySerializer, DepartmentSerializer, SeatAvailabilitySerializer, \
    InternshipSerializer, RotationSerializer, RequestedDepartmentSerializer, RotationRequestResponseSerializer, \
    RotationRequestForwardResponseSerializer
from rest_framework import viewsets, generics
from djng.views.mixins import allow_remote_invocation, JSONResponseMixin
from month import Month
from planner.models import Hospital, RequestedDepartment, Department, Specialty, \
    RotationRequest, RotationRequestForward, SeatAvailability, Internship, Rotation, RotationRequestResponse, \
    RotationRequestForwardResponse
from rest_framework.decorators import list_route, detail_route
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


# For testing purposes only
def list_forwards(request):
    context = {"forwards": RotationRequestForward.objects.all()}
    return render(request, "planner/list_forwards.html", context)


class HospitalViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HospitalSerializer
    queryset = Hospital.objects.all()


class SpecialtyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SpecialtySerializer
    queryset = Specialty.objects.all()


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()


class DepartmentBySpecialtyAndHospital(generics.RetrieveAPIView):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()

    def get_object(self):
        specialty = Specialty.objects.get(id=self.kwargs['specialty'])
        hospital = Hospital.objects.get(id=self.kwargs['hospital'])
        return get_object_or_404(Department, specialty=specialty, hospital=hospital)


class SeatAvailabilityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SeatAvailabilitySerializer
    queryset = SeatAvailability.objects.all()


class InternshipMonthViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InternshipMonthSerializer
    lookup_field = 'month'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated() and user.profile.role == Profile.INTERN:
            internship = user.profile.intern.internship
            return internship.months
        else:
            return []

    def get_object(self):
        queryset = self.get_queryset()
        month = Month.from_int(int(self.kwargs[self.lookup_field]))
        return filter(lambda m: m.month == month, queryset)[0]


class InternshipViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InternshipSerializer
    queryset = Internship.objects.all()


class RotationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RotationSerializer
    queryset = Rotation.objects.all()


class RequestedDepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = RequestedDepartmentSerializer
    queryset = RequestedDepartment.objects.all()


class RotationRequestViewSet(viewsets.ModelViewSet):
    serializer_class = RotationRequestSerializer
    queryset = RotationRequest.objects.all()

    @list_route(methods=["post"])
    def submit(self, request):
        request.data['month'] = str(Month.from_int(request.data['month']).first_day())
        request.data['internship'] = request.user.profile.intern.internship.id
        del request.data['specialty'] # Just for testing
        serialized = self.serializer_class(data=request.data)

        # TODO: How are the errors handled on the client side?
        if serialized.is_valid(raise_exception=True):
            instance = serialized.save()
            messages.success(request._request, "Your request has been submitted successfully.")

            # TODO: Notify internship unit.

            return Response(serialized.data)

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
        rr.forward_request()
        return Response({"status": RotationRequest.FORWARDED_STATUS})


class RotationRequestResponseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RotationRequestResponseSerializer
    queryset = RotationRequestResponse.objects.all()


class RotationRequestForwardViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RotationRequestForwardSerializer
    queryset = RotationRequestForward.objects.all()
    lookup_field = 'key'

    @list_route(methods=["post"])
    def respond(self, request):
        key = request.data.get("key")
        f = RotationRequestForward.objects.get(key=key)
        f.respond(
            is_approved=bool(int(request.data.get("is_approved"))),
            response_memo=request.data.get("response_memo"),
            respondent_name=request.data.get("respondent_name"),
            comments=request.data.get("comments", ""),
        )
        return Response({"status": RotationRequest.REVIEWED_STATUS, "is_approved": request.data.get("is_approved")})


class RotationRequestForwardResponseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RotationRequestForwardResponseSerializer
    queryset = RotationRequestForwardResponse.objects.all()
