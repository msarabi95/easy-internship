from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import get_object_or_404
from django.views import generic as django_generics

from django_nyt.utils import subscribe, notify
from month import Month
from rest_framework import viewsets, permissions
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import MethodNotAllowed, ValidationError as RestValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from accounts.models import Profile
from accounts.permissions import IsIntern, IsStaff
from months.forms import FreezeRequestForm
from rotations.models import RotationRequest
from months.models import Internship, Freeze, FreezeRequest, FreezeRequestResponse, FreezeCancelRequest, \
    FreezeCancelRequestResponse
from months.serializers import InternshipMonthSerializer, InternshipSerializer, FreezeSerializer, \
    FreezeRequestSerializer, FreezeRequestResponseSerializer, FreezeCancelRequestSerializer, \
    FreezeCancelRequestResponseSerializer


class FreezeRequestFormView(django_generics.FormView):
    template_name = "months/intern/freeze-request-create.html"
    form_class = FreezeRequestForm


class InternshipMonthViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InternshipMonthSerializer
    lookup_field = 'month'
    permission_classes = [permissions.IsAuthenticated, IsIntern]

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
            is_delete=True,
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

    @detail_route(methods=["get", "post"])
    def request_freeze(self, request, month=None):
        if request.method == "POST":
            month = Month.from_int(int(month))
            intern = self.request.user

            # TODO: Check that month is not frozen or disabled or there is a freeze request
            # TODO: Check that month has not current rotation or rotation request

            form = FreezeRequestForm(data=request.data, instance=FreezeRequest(intern=intern, month=month))

            if form.is_valid():

                freeze_request = form.save()

                # Subscribe user to receive update notifications on the request
                subscribe(intern.settings_set.first(), "freeze_request_approved", object_id=freeze_request.id)
                subscribe(intern.settings_set.first(), "freeze_request_declined", object_id=freeze_request.id)

                # Notify medical internship unit of the request
                notify(
                    "A new freeze request has been submitted by %s" % (request.user.profile.get_en_full_name()),
                    "freeze_request_submitted",
                    url="/planner/%d/" % freeze_request.intern.profile.intern.internship.id,
                )

                # Display success message to user
                messages.success(request._request, "Your freeze request has been submitted successfully.")

            response_data = {'errors': form.errors}
            return Response(response_data)
        return FreezeRequestFormView.as_view()(request._request, month)

    @detail_route(methods=["post"])
    def request_freeze_cancel(self, request, month=None):
        intern = request.user
        month = Month.from_int(int(month))
        current_freeze = intern.freezes.current_for_month(month)

        if not current_freeze:
            raise ObjectDoesNotExist("This month has no freeze to cancel.")

        if intern.freeze_cancel_requests.current_for_month(month):
            raise PermissionDenied("There is a pending freeze cancel request for this month already.")

        # TODO: Check that there are no rotations, leaves, freezes, or related requests in the month to be disabled

        cancel_request = FreezeCancelRequest.objects.create(
            intern=intern,
            month=month,
        )

        # --notifications--

        # Subscribe user to receive update notifications on the request
        subscribe(request.user.settings_set.first(), "freeze_cancel_request_approved", object_id=cancel_request.id)
        subscribe(request.user.settings_set.first(), "freeze_cancel_request_declined", object_id=cancel_request.id)

        # Notify medical internship unit of the request
        notify(
            "A freeze cancellation request has been submitted by %s" % (request.user.profile.get_en_full_name()),
            "freeze_cancel_request_submitted",
            url="/planner/%d/" % cancel_request.intern.profile.intern.internship.id,
            )

        messages.success(request._request, "Your freeze cancellation request has been submitted successfully.")

        return Response(status=HTTP_201_CREATED)


class InternshipMonthByInternshipAndId(viewsets.ViewSet):
    serializer_class = InternshipMonthSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]

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
    queryset = Internship.objects.all().prefetch_related(
        'rotation_requests__requested_department__department__hospital',
        'rotation_requests__requested_department__department__specialty',
        'rotation_requests__response',
        'rotation_requests__forward',
        'rotations__department__specialty',
        'rotations__department__hospital',
        'intern__profile__user__freezes',
        'intern__profile__user__freeze_requests__response',
        'intern__profile__user__freeze_cancel_requests__response',
        'intern__profile__user__leaves',
        'intern__profile__user__leave_requests__response',
        'intern__profile__user__leave_cancel_requests__response',
        'intern__university',
        'intern__batch',
    )
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("months.internship.view_all"):
            return self.queryset.all()
        return self.queryset.filter(intern__profile__user=self.request.user)


class FreezeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FreezeSerializer
    queryset = Freeze.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("months.freeze.view_all"):
            return self.queryset.all()
        return self.queryset.filter(intern=self.request.user)


class FreezeRequestViewSet(viewsets.ModelViewSet):
    serializer_class = FreezeRequestSerializer
    queryset = FreezeRequest.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("months.freeze_request.view_all"):
            return self.queryset.all()
        return self.queryset.filter(intern=self.request.user)

    @list_route(methods=["get"], permission_classes=[permissions.IsAuthenticated, IsStaff])
    def open(self, request):
        requests = self.queryset.open()

        if request.query_params.get('university') == 'agu':
            kw = {'intern__profile__intern__batch__is_agu': True}
        elif request.query_params.get('university') == 'outside':
            kw = {'intern__profile__intern__batch__is_ksauhs': False, 'intern__profile__intern__batch__is_agu': False}
        else:
            kw = {'intern__profile__intern__batch__is_ksauhs': True}
        requests = requests.filter(**kw)

        serialized = self.serializer_class(requests, many=True)
        return Response(serialized.data)

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed('post')

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('put')

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('patch')

    def destroy(self, request, *args, **kwargs):
        freeze_request = get_object_or_404(FreezeRequest, id=kwargs.get('pk'))

        # Make sure request hasn't been responded to
        if hasattr(freeze_request, 'response'):
            raise RestValidationError('This request cannot be deleted since it already has a response.')

        # Delete request
        freeze_request.delete()

        # Display success message to user
        messages.success(request._request, "Your request has been deleted.")

        return Response(status=HTTP_204_NO_CONTENT)


class FreezeRequestResponseViewSet(viewsets.ModelViewSet):
    serializer_class = FreezeRequestResponseSerializer
    queryset = FreezeRequestResponse.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("months.freeze_request_response.view_all"):
            return self.queryset.all()
        return self.queryset.filter(request__intern=self.request.user)

    def create(self, request, *args, **kwargs):
        # Check that the responding user has sufficient permissions
        if not request.user.has_perm("months.freeze_request_response.create"):
            raise PermissionDenied

        # Check that freeze request exists
        freeze_request = get_object_or_404(FreezeRequest, id=int(request.data['request']))

        # Check that there is no response already
        if hasattr(freeze_request, 'response'):
            raise PermissionDenied

        response = super(FreezeRequestResponseViewSet, self).create(request, *args, **kwargs)

        # Create freeze (if approved) and notify intern
        if bool(request.data['is_approved']):

            Freeze.objects.create(
                intern=freeze_request.intern,
                month=freeze_request.month,
                freeze_request=freeze_request,
            )

            notify(
                "Freeze request %d for %s has been approved." % (freeze_request.id, freeze_request.month.first_day().strftime("%B %Y")),
                "freeze_request_approved",
                target_object=freeze_request,
                url="/planner/%d/" % int(freeze_request.month),
            )
        else:
            notify(
                "Freeze request %d for %s has been declined." % (freeze_request.id, freeze_request.month.first_day().strftime("%B %Y")),
                "freeze_request_declined",
                target_object=freeze_request,
                url="/planner/%d/" % int(freeze_request.month),
            )

        return response

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('put')

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('patch')

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('delete')


class FreezeCancelRequestViewSet(viewsets.ModelViewSet):
    serializer_class = FreezeCancelRequestSerializer
    queryset = FreezeCancelRequest.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("months.freeze_cancel_request.view_all"):
            return self.queryset.all()
        return self.queryset.filter(intern=self.request.user)

    @list_route(methods=["get"], permission_classes=[permissions.IsAuthenticated, IsStaff])
    def open(self, request):
        requests = self.queryset.open()

        if request.query_params.get('university') == 'agu':
            kw = {'intern__profile__intern__batch__is_agu': True}
        elif request.query_params.get('university') == 'outside':
            kw = {'intern__profile__intern__batch__is_ksauhs': False, 'intern__profile__intern__batch__is_agu': False}
        else:
            kw = {'intern__profile__intern__batch__is_ksauhs': True}
        requests = requests.filter(**kw)

        serialized = self.serializer_class(requests, many=True)
        return Response(serialized.data)

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed('post')

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('put')

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('patch')

    def destroy(self, request, *args, **kwargs):
        freeze_cancel_request = get_object_or_404(FreezeCancelRequest, id=kwargs.get('pk'))

        # Make sure request hasn't been responded to
        if hasattr(freeze_cancel_request, 'response'):
            raise RestValidationError('This request cannot be deleted since it already has a response.')

        # Delete request
        freeze_cancel_request.delete()

        # Display success message to user
        messages.success(request._request, "Your request has been deleted.")

        return Response(status=HTTP_204_NO_CONTENT)


class FreezeCancelRequestResponseViewSet(viewsets.ModelViewSet):
    serializer_class = FreezeCancelRequestResponseSerializer
    queryset = FreezeCancelRequestResponse.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("months.freeze_cancel_request_response.view_all"):
            return self.queryset.all()
        return self.queryset.filter(request__intern=self.request.user)
    
    def create(self, request, *args, **kwargs):
        # Check that the responding user has sufficient permissions
        if not request.user.has_perm("months.freeze_cancel_request_response.create"):
            raise PermissionDenied

        # Check that freeze cancellation request exists
        freeze_cancel_request = get_object_or_404(FreezeCancelRequest, id=int(request.data['request']))

        # Check that there is no response already
        if hasattr(freeze_cancel_request, 'response'):
            raise PermissionDenied

        response = super(FreezeCancelRequestResponseViewSet, self).create(request, *args, **kwargs)

        # Delete freeze (if approved) and notify intern
        if bool(request.data['is_approved']):
            
            freeze = Freeze.objects.get(
                intern=freeze_cancel_request.intern,
                month=freeze_cancel_request.month,
            )
            freeze.delete()

            notify(
                "Freeze cancellation request %d for %s has been approved." % (freeze_cancel_request.id, freeze_cancel_request.month.first_day().strftime("%B %Y")),
                "freeze_cancel_request_approved",
                target_object=freeze_cancel_request,
                url="/planner/%d/" % int(freeze_cancel_request.month),
            )
        else:
            notify(
                "Freeze cancellation request %d for %s has been declined." % (freeze_cancel_request.id, freeze_cancel_request.month.first_day().strftime("%B %Y")),
                "freeze_cancel_request_declined",
                target_object=freeze_cancel_request,
                url="/planner/%d/" % int(freeze_cancel_request.month),
            )

        return response

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('put')

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('patch')

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('delete')
