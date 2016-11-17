import json

from django.contrib import messages
from django.http import HttpResponse
from django_nyt.utils import subscribe, notify
from leaves.forms import LeaveRequestForm
from leaves.models import LeaveType, LeaveSetting, LeaveRequest, LeaveRequestResponse, LeaveCancelRequest, \
    LeaveCancelRequestResponse, Leave
from leaves.serializers import LeaveTypeSerializer, LeaveSettingSerializer, LeaveRequestSerializer, \
    LeaveRequestResponseSerializer, LeaveCancelRequestSerializer, LeaveCancelRequestResponseSerializer, LeaveSerializer
from django.views import generic as django_generics
from month import Month
from rest_framework import viewsets


class LeaveTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveTypeSerializer
    queryset = LeaveType.objects.all()


class LeaveSettingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveSettingSerializer
    queryset = LeaveSetting.objects.all()


class LeaveRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveRequestSerializer
    queryset = LeaveRequest.objects.all()


class LeaveRequestResponseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveRequestResponseSerializer
    queryset = LeaveRequestResponse.objects.all()


class LeaveViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveSerializer
    queryset = Leave.objects.all()


class LeaveCancelRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveCancelRequestSerializer
    queryset = LeaveCancelRequest.objects.all()


class LeaveCancelRequestResponseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveCancelRequestResponseSerializer
    queryset = LeaveCancelRequestResponse.objects.all()


class LeaveRequestFormView(django_generics.FormView):
    template_name = "leaves/intern/leave-request-create.html"
    form_class = LeaveRequestForm

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            return self.ajax(request)
        raise

    def ajax(self, request):
        data = json.loads(request.body)
        month = Month.from_int(int(data['month']))
        intern = self.request.user

        form = self.form_class(data=data, instance=LeaveRequest(intern=intern, month=month))

        if form.is_valid():

            leave_request = form.save()

            # Subscribe user to receive update notifications on the request
            subscribe(intern.settings_set.first(), "leave_request_approved", object_id=leave_request.id)
            subscribe(intern.settings_set.first(), "leave_request_declined", object_id=leave_request.id)

            # Notify medical internship unit of the request
            notify(
                "A new leave request has been submitted by %s" % (request.user.profile.get_en_full_name()),
                "leave_request_submitted",
                url="/planner/%d/" % leave_request.intern.profile.intern.internship.id,
            )

            # Display success message to user
            messages.success(request, "Your leave request has been submitted successfully.")

        response_data = {'errors': form.errors}
        return HttpResponse(json.dumps(response_data), content_type="application/json")

