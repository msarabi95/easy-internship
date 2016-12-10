import json

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError, NON_FIELD_ERRORS
from django.http import Http404, HttpResponse

# Create your views here.
from django.views import generic as django_generics
from django_nyt.utils import subscribe, notify
from month import Month
from rest_framework import viewsets, permissions
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from accounts.permissions import IsStaff
from rotations.exceptions import ResponseExists, ForwardExists
from rotations.forms import RotationRequestForm
from rotations.models import Rotation, RequestedDepartment, RotationRequest, RotationRequestResponse, \
    RotationRequestForward
from hospitals.models import Department, AcceptanceSetting
from rotations.serializers import RotationSerializer, RequestedDepartmentSerializer, RotationRequestSerializer, \
    RotationRequestResponseSerializer, RotationRequestForwardSerializer


class RotationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RotationSerializer
    queryset = Rotation.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("rotations.rotation.view_all"):
            return self.queryset.all()
        return self.queryset.filter(internship__intern__profile__user=self.request.user)


class RequestedDepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RequestedDepartmentSerializer
    queryset = RequestedDepartment.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class RotationRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RotationRequestSerializer
    queryset = RotationRequest.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("rotations.rotation_request.view_all"):
            return self.queryset.all()
        return self.queryset.filter(internship__intern__profile__user=self.request.user)

    @detail_route(methods=["post"])
    def respond(self, request, pk=None):
        """
        Respond to rotation request.
        """
        rotation_request = self.get_queryset().get(pk=pk)
        is_approved = bool(int(request.query_params.get("is_approved")))
        comments = request.query_params.get("comments", "")

        if hasattr(rotation_request, 'response'):
            raise ResponseExists("This rotation request has already been responded to.")
        
        # If forward expected and not present, raise exception
        
        RotationRequestResponse.objects.create(
            rotation_request=rotation_request,
            is_approved=is_approved,
            comments=comments,
        )
        
        if is_approved:
            # Remove any previous rotation in the request's month
            rotation_request.internship.rotations.filter(month=rotation_request.month).delete()

            # Unless this is a delete, request, add a new rotation object for the current month
            if not rotation_request.is_delete:
                # If the requested department is not in the database, add it.
                # FIXME: This shouldn't be default behavior
                if not rotation_request.requested_department.is_in_database:
                    rotation_request.requested_department.add_to_database()

                rotation_request.internship.rotations.create(
                    month=rotation_request.month,
                    specialty=rotation_request.specialty,
                    department=rotation_request.requested_department.get_department(),
                    is_elective=rotation_request.is_elective,
                    rotation_request=rotation_request,
                )
                
                # --notifications--

                notify(
                    "Rotation request %d for %s has been approved." % (rotation_request.id, rotation_request.month.first_day().strftime("%B %Y")),
                    "rotation_request_approved",
                    target_object=rotation_request,
                    url="/planner/%d/" % int(rotation_request.month),
                )
            else:

                # --notifications--
                notify(
                    "Rotation request %d for %s has been declined." % (rotation_request.id, rotation_request.month.first_day().strftime("%B %Y")),
                    "rotation_request_declined",
                    target_object=rotation_request,
                    url="/planner/%d/history/" % int(rotation_request.month),
                )
        
        if not request.query_params.get("suppress_message"):
            messages.success(request._request, "Your response has been recorded.")

        return Response({"status": RotationRequest.REVIEWED_STATUS, "is_approved": request.data.get("is_approved")})

    @detail_route(methods=["post"])
    def forward(self, request, pk=None):
        """
        Forward the rotation request.
        """
        rotation_request = self.get_queryset().get(pk=pk)

        if hasattr(rotation_request, 'forward'):
            raise ForwardExists("This rotation request has already been forwarded.")

        RotationRequestForward.objects.create(
            rotation_request=rotation_request,
        )

        if not request.query_params.get("suppress_message"):
            messages.success(request._request, "Your response has been recorded.")

        return Response({"status": RotationRequest.FORWARDED_STATUS})


class RotationRequestByDepartmentAndMonth(viewsets.ViewSet):
    serializer_class = RotationRequestSerializer
    queryset = RotationRequest.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsStaff]

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
    template_name = "rotations/intern/rotation-request-create.html"
    form_class = RotationRequestForm
    # TODO: permissions?

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

        # TODO: Check that month is not frozen or disabled

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
                rr = RotationRequest(
                    internship=internship,
                    month=month,
                    specialty=requested_department.department_specialty,
                    requested_department=requested_department,
                    is_elective=form.cleaned_data['is_elective'],
                )
                rr.validate_request()
                rr.save()
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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("rotations.rotation_request_response.view_all"):
            return self.queryset.all()
        return self.queryset.filter(rotation_request__internship__intern__profile__user=self.request.user)


class RotationRequestForwardViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RotationRequestForwardSerializer
    queryset = RotationRequestForward.objects.all()
    lookup_field = 'key'
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("rotations.rotation_request_forward.view_all"):
            return self.queryset.all()
        return self.queryset.filter(rotation_request__internship__intern__profile__user=self.request.user)

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
