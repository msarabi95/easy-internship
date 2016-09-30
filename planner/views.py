import json

from accounts.models import Profile
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, ValidationError, NON_FIELD_ERRORS
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import generic as django_generics
from planner.forms import RotationRequestForm
from planner.serializers import RotationRequestSerializer, RotationRequestForwardSerializer, \
    InternshipMonthSerializer, HospitalSerializer, SpecialtySerializer, DepartmentSerializer, SeatAvailabilitySerializer, \
    InternshipSerializer, RotationSerializer, RequestedDepartmentSerializer, RotationRequestResponseSerializer, \
    RotationRequestForwardResponseSerializer
from rest_framework import viewsets, generics
from month import Month
from planner.models import Hospital, RequestedDepartment, Department, Specialty, \
    RotationRequest, RotationRequestForward, SeatAvailability, Internship, Rotation, RotationRequestResponse, \
    RotationRequestForwardResponse
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response

# For testing purposes only
from rest_framework.status import HTTP_201_CREATED


def list_forwards(request):
    context = {"forwards": RotationRequestForward.objects.all()}
    return render(request, "planner/list_forwards.html", context)


def rotation_request_responses(request):
    if request.method == "POST":
        import random
        if request.POST.get("response") == "approveall":
            for request in RotationRequest.objects.open():
                request.respond(True, random.choice(["This is a random comment", ""]))

        elif request.POST.get("response") == "declineall":
            for request in RotationRequest.objects.open():
                request.respond(False, random.choice(["This is a random comment", ""]))

        return HttpResponseRedirect(reverse("rotation_request_responses"))

    context = {'count': RotationRequest.objects.open().count()}
    return render(request, "planner/rotation_request_responses.html", context)


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

    @detail_route(methods=["post"])
    def cancel_rotation(self, request, month=None):
        internship = request.user.profile.intern.internship
        month = Month.from_int(int(month))
        current_rotation = internship.rotations.current_for_month(month)

        if not current_rotation:
            raise ObjectDoesNotExist("This month has no rotation to cancel.")

        if internship.rotation_requests.current_for_month(month):
            raise PermissionDenied("There is a pending rotation request for this month already.")

        requested_department = current_rotation.rotation_request.requested_department
        requested_department.id = None
        requested_department.save()

        internship.rotation_requests.create(
            month=month,
            specialty=requested_department.department_specialty,
            requested_department=requested_department,
            delete=True,
        )

        messages.success(request._request, "Your cancellation request has been submitted successfully.")

        # TODO: Notify internship unit

        return Response(status=HTTP_201_CREATED)


class InternshipMonthByInternshipAndId(generics.RetrieveAPIView):
    serializer_class = InternshipMonthSerializer

    def get_object(self):
        internship = get_object_or_404(Internship, pk=int(self.kwargs['internship_id']))
        month_id = int(self.kwargs['month_id'])
        return filter(lambda month: int(month.month) == month_id, internship.months)[0]


class InternshipViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InternshipSerializer
    queryset = Internship.objects.all()

    @list_route(methods=['get'])
    def with_unreviewed_requests(self, request):
        internships = Internship.objects.all()
        unreviewed_requests = RotationRequest.objects.unreviewed()
        filtered = filter(lambda i: any([r in unreviewed_requests for r in i.rotation_requests.all()]), internships)
        return Response(self.get_serializer(filtered, many=True).data)


class RotationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RotationSerializer
    queryset = Rotation.objects.all()


class RequestedDepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = RequestedDepartmentSerializer
    queryset = RequestedDepartment.objects.all()


class RotationRequestViewSet(viewsets.ModelViewSet):
    serializer_class = RotationRequestSerializer
    queryset = RotationRequest.objects.all()

    @detail_route(methods=["post"])
    def respond(self, request, pk=None):
        rr = RotationRequest.objects.get(pk=pk)
        rr.respond(bool(int(request.query_params.get("is_approved"))), request.query_params.get("comments", ""))

        messages.success(request._request, "Your response has been recorded.")

        return Response({"status": RotationRequest.REVIEWED_STATUS, "is_approved": request.data.get("is_approved")})

    @detail_route(methods=["post"])
    def forward(self, request, pk=None):
        rr = RotationRequest.objects.get(pk=pk)
        rr.forward_request()
        return Response({"status": RotationRequest.FORWARDED_STATUS})


class RotationRequestFormView(django_generics.FormView):
    template_name = "planner/intern/rotation-request-create.html"
    form_class = RotationRequestForm

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            return self.ajax(request)
        raise

    def ajax(self, request):
        data = json.loads(request.body)
        month = Month.from_int(int(data['month']))
        internship = self.request.user.profile.intern.internship

        if internship.rotation_requests.current_for_month(month):
            raise PermissionDenied("There is a rotation request for this month already.")

        form = self.form_class(data=data)
        if form.is_valid():
            requested_department = form.save()
            try:
                internship.rotation_requests.create(
                    month=month,
                    specialty=requested_department.department_specialty,
                    requested_department=requested_department,
                    is_elective=form.cleaned_data['is_elective'],
                )
            except ValidationError as e:
                for error in e.message_dict[NON_FIELD_ERRORS]:
                    form.add_error(None, error)

            else:

                # TODO: Notify internship unit (take care not to send a lot of simultaneous notifications though!)
                messages.success(request, "Your request has been submitted successfully.")

        response_data = {'errors': form.errors}
        return HttpResponse(json.dumps(response_data), content_type="application/json")


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
