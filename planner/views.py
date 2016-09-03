from accounts.models import Profile
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from planner.serializers import RotationRequestSerializer, RotationRequestForwardSerializer, \
    InternshipMonthSerializer, HospitalSerializer, SpecialtySerializer, DepartmentSerializer, SeatAvailabilitySerializer, \
    InternshipSerializer, RotationSerializer, RequestedDepartmentSerializer, RotationRequestResponseSerializer, \
    RotationRequestForwardResponseSerializer
from rest_framework import viewsets, generics
from month import Month
from planner.models import Hospital, RequestedDepartment, Department, Specialty, \
    RotationRequest, RotationRequestForward, SeatAvailability, Internship, Rotation, RotationRequestResponse, \
    RotationRequestForwardResponse
from rest_framework.decorators import list_route
from rest_framework.response import Response

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
