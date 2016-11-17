import json

from datetime import datetime

from accounts.models import Profile
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, ValidationError, NON_FIELD_ERRORS
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views import generic as django_generics
from django_nyt.utils import subscribe, notify
from planner.forms import RotationRequestForm
from planner.serializers import RotationRequestSerializer, RotationRequestForwardSerializer, \
    InternshipMonthSerializer, HospitalSerializer, SpecialtySerializer, DepartmentSerializer, DepartmentMonthSettingsSerializer, \
    InternshipSerializer, RotationSerializer, RequestedDepartmentSerializer, RotationRequestResponseSerializer, \
    RotationRequestForwardResponseSerializer, MonthSettingsSerializer, \
    DepartmentSettingsSerializer, AcceptanceSettingSerializer
from planner.utils import set_global_acceptance_criterion, get_global_acceptance_criterion, \
    get_global_acceptance_start_date_interval, set_global_acceptance_start_date_interval, \
    get_global_acceptance_end_date_interval, set_global_acceptance_end_date_interval, get_global_settings
from rest_framework import viewsets, generics
from month import Month
from planner.models import Hospital, RequestedDepartment, Department, Specialty, \
    RotationRequest, RotationRequestForward, DepartmentMonthSettings, Internship, Rotation, RotationRequestResponse, \
    RotationRequestForwardResponse, MonthSettings, DepartmentSettings, AcceptanceSetting
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


class DepartmentBySpecialtyAndHospital(viewsets.ViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_object(self):
        specialty = Specialty.objects.get(id=self.kwargs['specialty'])
        hospital = Hospital.objects.get(id=self.kwargs['hospital'])
        return get_object_or_404(Department, specialty=specialty, hospital=hospital)


class GlobalSettingsViewSet(viewsets.ViewSet):
    @list_route(methods=["get", "post"])
    def acceptance_criterion(self, request):
        if request.method == 'GET':
            return Response({'acceptance_criterion': get_global_acceptance_criterion()})
        elif request.method == 'POST':
            old_value = get_global_acceptance_criterion()
            new_value = request.data.get('acceptance_criterion')
            if old_value != new_value:
                try:
                    set_global_acceptance_criterion(new_value)
                except ValidationError as e:
                    messages.error(request._request, e)
                else:
                    messages.success(request._request, "Global acceptance criterion updated.")

            return Response({'acceptance_criterion': get_global_acceptance_criterion()})

    @list_route(methods=["get", "post"])
    def acceptance_start_date_interval(self, request):
        if request.method == 'GET':
            return Response({'acceptance_start_date_interval': get_global_acceptance_start_date_interval()})
        elif request.method == 'POST':
            old_value = get_global_acceptance_start_date_interval()
            new_value = request.data.get('acceptance_start_date_interval')
            if old_value != new_value:
                try:
                    set_global_acceptance_start_date_interval(new_value)
                except ValidationError as e:
                    messages.error(request._request, e)
                else:
                    messages.success(request._request, "Global acceptance start date interval updated.")

            return Response({'acceptance_start_date_interval': get_global_acceptance_start_date_interval()})

    @list_route(methods=["get", "post"])
    def acceptance_end_date_interval(self, request):
        if request.method == 'GET':
            return Response({'acceptance_end_date_interval': get_global_acceptance_end_date_interval()})
        elif request.method == 'POST':
            old_value = get_global_acceptance_end_date_interval()
            new_value = request.data.get('acceptance_end_date_interval')
            if old_value != new_value:
                try:
                    set_global_acceptance_end_date_interval(new_value)
                except ValidationError as e:
                    messages.error(request._request, e)
                else:
                    messages.success(request._request, "Global acceptance end date interval updated.")

            return Response({'acceptance_end_date_interval': get_global_acceptance_end_date_interval()})


class SettingsMessagesMixin(object):
    def create(self, request, *args, **kwargs):
        response = super(SettingsMessagesMixin, self).create(request, *args, **kwargs)
        messages.success(request._request, "Created!")
        return response

    def update(self, request, *args, **kwargs):
        response = super(SettingsMessagesMixin, self).update(request, *args, **kwargs)
        messages.success(request._request, "Updated!")
        return response

    def destroy(self, request, *args, **kwargs):
        response = super(SettingsMessagesMixin, self).destroy(request, *args, **kwargs)
        messages.success(request._request, "Destroyed!")
        return response


class MonthSettingsViewSet(SettingsMessagesMixin, viewsets.ModelViewSet):
    serializer_class = MonthSettingsSerializer
    queryset = MonthSettings.objects.all()


class DepartmentSettingsViewSet(SettingsMessagesMixin, viewsets.ModelViewSet):
    serializer_class = DepartmentSettingsSerializer
    queryset = DepartmentSettings.objects.all()


class DepartmentMonthSettingsViewSet(SettingsMessagesMixin, viewsets.ModelViewSet):
    serializer_class = DepartmentMonthSettingsSerializer
    queryset = DepartmentMonthSettings.objects.all()

    @list_route(methods=['get'], url_path='starting_month')
    def get_display_starting_month(self, request):
        return Response({'id': int(Month.from_date(datetime(timezone.now().year, 1, 1)))})


class AcceptanceSettingsByDepartmentAndMonth(viewsets.ViewSet):
    serializer_class = AcceptanceSettingSerializer

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_object(self):
        department = get_object_or_404(Department, id=self.kwargs['department_id'])
        month = Month.from_int(int(self.kwargs['month_id']))
        return AcceptanceSetting(department, month)


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

        rr = internship.rotation_requests.create(
            month=month,
            specialty=requested_department.department_specialty,
            requested_department=requested_department,
            delete=True,
        )

        # --notifications--

        # Subscribe user to receive update notifications on the request
        subscribe(request.user.settings_set.first(), "rotation_request_approved", object_id=rr.id)
        subscribe(request.user.settings_set.first(), "rotation_request_declined", object_id=rr.id)

        # Notify medical internship unit of the request
        notify(
            "A cancellation request has been submitted by %s" % (request.user.profile.get_en_full_name()),
            "rotation_request_submitted",
            url="/planner/%d/" % rr.internship.id,
            )  # FIXME: avoid sending a lot of simultaneous notifications

        messages.success(request._request, "Your cancellation request has been submitted successfully.")

        return Response(status=HTTP_201_CREATED)


class InternshipMonthByInternshipAndId(viewsets.ViewSet):
    serializer_class = InternshipMonthSerializer

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

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

        if not request.query_params.get("suppress_message"):
            messages.success(request._request, "Your response has been recorded.")

        return Response({"status": RotationRequest.REVIEWED_STATUS, "is_approved": request.data.get("is_approved")})

    @detail_route(methods=["post"])
    def forward(self, request, pk=None):
        rr = RotationRequest.objects.get(pk=pk)
        rr.forward_request()
        return Response({"status": RotationRequest.FORWARDED_STATUS})


class RotationRequestByDepartmentAndMonth(viewsets.ViewSet):
    serializer_class = RotationRequestSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            raise Http404

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_queryset(self):
        department = Department.objects.get(id=self.kwargs['department_id'])
        month = Month.from_int(int(self.kwargs['month_id']))
        return RotationRequest.objects.unreviewed().filter(month=month, requested_department__department=department)


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

            if form.cleaned_data['is_in_database']:
                department = form.cleaned_data['department']
                settings = AcceptanceSetting(department, month)
                if not settings.can_submit_requests():
                    form.add_error(None, "Submission is closed for %s during %s." % (department.name, month.first_day().strftime("%B %Y")))
                    response_data = {'errors': form.errors}
                    return HttpResponse(json.dumps(response_data), content_type="application/json")

            requested_department = form.save()
            try:
                rr = internship.rotation_requests.create(
                    month=month,
                    specialty=requested_department.department_specialty,
                    requested_department=requested_department,
                    is_elective=form.cleaned_data['is_elective'],
                )
            except ValidationError as e:
                for error in e.message_dict[NON_FIELD_ERRORS]:
                    form.add_error(None, error)

            else:
                # --notifications--

                # Subscribe user to receive update notifications on the request
                subscribe(request.user.settings_set.first(), "rotation_request_approved", object_id=rr.id)
                subscribe(request.user.settings_set.first(), "rotation_request_declined", object_id=rr.id)

                # Notify medical internship unit of the request
                notify(
                    "A new rotation request has been submitted by %s" % (request.user.profile.get_en_full_name()),
                    "rotation_request_submitted",
                    url="/planner/%d/" % rr.internship.id,
                )  # FIXME: avoid sending a lot of simultaneous notifications

                # Display success message to user
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
