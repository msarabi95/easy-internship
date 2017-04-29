import json
import cStringIO as StringIO
from wsgiref.util import FileWrapper

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError, NON_FIELD_ERRORS
from django.http import Http404, HttpResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.views import generic as django_generics
from django_nyt.utils import subscribe, notify
from docxtpl import DocxTemplate
from month import Month
from rest_framework import viewsets, permissions
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import ParseError, MethodNotAllowed
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_201_CREATED

from accounts.permissions import IsStaff
from misc.models import DocumentTemplate
from rotations.exceptions import ResponseExists, ForwardExists, ForwardExpected, ForwardNotExpected
from rotations.forms import RotationRequestForm
from rotations.models import Rotation, RequestedDepartment, RotationRequest, RotationRequestResponse, \
    RotationRequestForward, AcceptanceList
from hospitals.models import Department, AcceptanceSetting, Hospital, Specialty, DepartmentMonthSettings, MonthSettings, \
    DepartmentSettings, GlobalSettings
from rotations.serializers import RotationSerializer, RequestedDepartmentSerializer, RotationRequestSerializer, \
    RotationRequestResponseSerializer, RotationRequestForwardSerializer, AcceptanceListSerializer, \
    ShortRotationRequestForwardSerializer, ShortRotationRequestSerializer, FullRotationSerializer, \
    UpdatedRotationRequestSerializer


class RotationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RotationSerializer
    queryset = Rotation.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("rotations.rotation.view_all"):
            return self.queryset.all()
        return self.queryset.filter(internship__intern__profile__user=self.request.user)

    @list_route(methods=['get'], permission_classes=[permissions.IsAuthenticated, IsStaff])
    def master_rota(self, request):
        if len(request.query_params.keys()) == 0:
            raise ParseError(detail="No query parameters were specified.")  # FIXME: Is this the most accurate error?

        year = request.query_params.get('year')
        hospital = request.query_params.get('hospital')

        if year is None or hospital is None:
            raise ParseError(detail="Both `year` and `hospital` query parameters should be specified.")

        months = [Month(int(year), month) for month in range(1, 13)]
        departments = Department.objects.filter(hospital__id=hospital).prefetch_related(
            'rotations',
        )

        rotation_counts = []

        for department in departments:
            dept_counts = []
            for month in months:
                dept_counts.append({
                    "department": department.id,
                    "month": int(month),
                    "count": len(filter(lambda rotation: rotation.month == month, department.rotations.all())),
                })
            rotation_counts.append(dept_counts)

        return Response(rotation_counts)

    @list_route(methods=['get'], permission_classes=[permissions.IsAuthenticated, IsStaff])
    def monthly_list(self, request):
        """
        Return the list of rotations for a given month and department
        """
        if len(request.query_params.keys()) == 0:
            raise ParseError(detail="No query parameters were specified.")  # FIXME: Is this the most accurate error?

        department = request.query_params.get('department')
        month = request.query_params.get('month')

        if department is None or month is None:
            raise ParseError(detail="Both `department` and `month` query parameters should be specified.")

        month = Month.from_int(int(month))
        rotations = Rotation.objects.filter(
            department=department,
            month=month,
        ).prefetch_related(
            'internship__intern__profile',
        )

        serialized = FullRotationSerializer(rotations, many=True)

        return Response(serialized.data)


class RequestedDepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RequestedDepartmentSerializer
    queryset = RequestedDepartment.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class RotationRequestViewSet(viewsets.ModelViewSet):
    serializer_class = RotationRequestSerializer
    queryset = RotationRequest.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("rotations.rotation_request.view_all"):
            return self.queryset.all()
        return self.queryset.filter(internship__intern__profile__user=self.request.user)

    def create(self, request, *args, **kwargs):

        # TODO: Do some permission checks first

        serializer = UpdatedRotationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # TODO: Notifications

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed

    @list_route(methods=['get'], permission_classes=[permissions.IsAuthenticated, IsStaff])
    def kamc_memo(self, request):
        requests = self.get_queryset().unreviewed().filter(is_delete=False)\
            .filter(requested_department__department__hospital__is_kamc=True)\
            .filter(requested_department__department__requires_memo=True)

        if request.query_params.get('university') == 'agu':
            kw = {'internship__intern__batch__is_agu': True}
        elif request.query_params.get('university') == 'outside':
            kw = {'internship__intern__batch__is_ksauhs': False, 'internship__intern__batch__is_agu': False}
        else:
            kw = {'internship__intern__batch__is_ksauhs': True}
        requests = requests.filter(**kw)

        serialized = ShortRotationRequestSerializer(requests, many=True)
        return Response(serialized.data)

    @list_route(methods=['get'], permission_classes=[permissions.IsAuthenticated, IsStaff])
    def non_kamc(self, request):
        requests = self.get_queryset().unreviewed().filter(is_delete=False)\
            .filter(requested_department__department__hospital__is_kamc=False)\
            .filter(requested_department__department__requires_memo=True)

        if request.query_params.get('university') == 'agu':
            kw = {'internship__intern__batch__is_agu': True}
        elif request.query_params.get('university') == 'outside':
            kw = {'internship__intern__batch__is_ksauhs': False, 'internship__intern__batch__is_agu': False}
        else:
            kw = {'internship__intern__batch__is_ksauhs': True}
        requests = requests.filter(**kw)

        serialized = ShortRotationRequestSerializer(requests, many=True)
        return Response(serialized.data)

    @list_route(methods=['get'], permission_classes=[permissions.IsAuthenticated, IsStaff])
    def cancellation(self, request):
        requests = self.get_queryset().unreviewed().filter(is_delete=True)
        serialized = ShortRotationRequestSerializer(requests, many=True)

        if request.query_params.get('university') == 'agu':
            kw = {'internship__intern__batch__is_agu': True}
        elif request.query_params.get('university') == 'outside':
            kw = {'internship__intern__batch__is_ksauhs': False, 'internship__intern__batch__is_agu': False}
        else:
            kw = {'internship__intern__batch__is_ksauhs': True}
        requests = requests.filter(**kw)

        return Response(serialized.data)

    @detail_route(methods=['get'], permission_classes=[permissions.IsAuthenticated, IsStaff])
    def memo_docx(self, request, pk=None):
        rotation_request = get_object_or_404(RotationRequest, pk=pk)
        department = rotation_request.requested_department.get_department()
        intern = rotation_request.internship.intern

        # Check if memo is expected
        department_requires_memo = department.requires_memo
        if not department_requires_memo:
            raise ForwardNotExpected("This rotation request does not require a forward.")

        template_name = "inside_request" if department.hospital.is_kamc else "outside_request"
        template = DocumentTemplate.objects.get(codename=template_name)

        docx = DocxTemplate(template.template_file)
        context = {
            'now': timezone.now(),
            'contact_name': department.contact_name,
            'contact_position': department.contact_position,
            'hospital': department.hospital.name,
            'intern_name': intern.profile.get_en_full_name(),
            'specialty': rotation_request.specialty.name,
            'month': rotation_request.month.first_day().strftime("%B"),
            'year': rotation_request.month.year,
            'badge_number': intern.badge_number,
            'mobile_number': intern.mobile_number,
            'email': intern.profile.user.email,
        }
        docx.render(context)
        docx_file = StringIO.StringIO()
        docx.save(docx_file)
        docx_file.flush()
        docx_file.seek(0)

        file_name = "Memo - %s - %s %s" % (
            intern.profile.get_en_full_name(),
            rotation_request.month.first_day().strftime("%B"),
            rotation_request.month.year,
        )

        response = HttpResponse(
            FileWrapper(docx_file),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        response['Content-Disposition'] = 'attachment; filename=%s.docx' % file_name
        return response

    @detail_route(methods=["post"])
    def respond(self, request, pk=None):
        """
        Respond to rotation request.
        """
        rotation_request = self.get_queryset().get(pk=pk)
        is_approved = bool(int(request.query_params.get("is_approved")))
        comments = request.query_params.get("comments", "")

        # Checks

        if hasattr(rotation_request, 'response'):
            raise ResponseExists("This rotation request has already been responded to.")
        
        department_requires_memo = rotation_request.requested_department.get_department().requires_memo
        memo_handed_by_intern = rotation_request.requested_department.get_department().memo_handed_by_intern
        if department_requires_memo and not hasattr(rotation_request, 'forward') and is_approved and not rotation_request.is_delete:
            raise ForwardExpected("This rotation request can't be approved without forwarding it first.")

        # TODO: Check that the appropriate person is recording the response
        if department_requires_memo and memo_handed_by_intern:
            pass

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
        print request.data

        rotation_request = self.get_queryset().get(pk=pk)

        # Checks

        if hasattr(rotation_request, 'forward'):
            raise ForwardExists("This rotation request has already been forwarded.")

        department_requires_memo = rotation_request.requested_department.get_department().requires_memo
        if not department_requires_memo:
            raise ForwardNotExpected("This rotation request does not require a forward.")

        data = request.data
        data['rotation_request'] = pk
        serialized = RotationRequestForwardSerializer(
            data=request.data,
        )

        serialized.is_valid(raise_exception=True)
        serialized.save()

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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("rotations.rotation_request_forward.view_all"):
            return self.queryset.all()
        return self.queryset.filter(rotation_request__internship__intern__profile__user=self.request.user)

    @list_route(methods=['get'], permission_classes=[permissions.IsAuthenticated, IsStaff])
    def intern_memos_as_table(self, request, *args, **kwargs):
        forwards = self.get_queryset()\
            .filter(rotation_request__response__isnull=True)\
            .filter(rotation_request__requested_department__department__memo_handed_by_intern=True)
        serialized = ShortRotationRequestForwardSerializer(forwards, many=True)
        return Response(serialized.data)

    @list_route(methods=['get'], permission_classes=[permissions.IsAuthenticated, IsStaff])
    def staff_memos_as_table(self, request, *args, **kwargs):
        forwards = self.get_queryset()\
            .filter(rotation_request__response__isnull=True)\
            .filter(rotation_request__requested_department__department__memo_handed_by_intern=False)
        serialized = ShortRotationRequestForwardSerializer(forwards, many=True)
        return Response(serialized.data)

    @list_route(methods=['get'], permission_classes=[permissions.IsAuthenticated, IsStaff])
    def memos_archive_as_table(self, request, *args, **kwargs):
        forwards = self.get_queryset()\
            .filter(rotation_request__response__isnull=False)
        serialized = ShortRotationRequestForwardSerializer(forwards, many=True)
        return Response(serialized.data)


class AcceptanceListViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def acceptance_list_factory(self, departments_and_months, rotation_requests, acceptance_settings, departments_cache):
        # FIXME: A better way to get the department
        return [AcceptanceList(filter(lambda d: d.id == department_id, departments_cache)[0], month, rotation_requests_cache=rotation_requests,
                               acceptance_settings_cache=acceptance_settings) for department_id, month in set(departments_and_months)]

    def acceptance_setting_factory(self, departments, months,
                                   department_month_settings=None, month_settings=None,
                                   department_settings=None, global_settings=None):
        return [AcceptanceSetting(department, month,
                                  department_month_settings, month_settings,
                                  department_settings, global_settings) for department in departments for month in set(months)]

    def list(self, request, *args, **kwargs):
        rotation_requests = RotationRequest.objects.unreviewed()\
            .filter(is_delete=False)\
            .filter(requested_department__department__hospital__is_kamc=True)\
            .filter(requested_department__department__requires_memo=False)

        if request.query_params.get('university') == 'agu':
            kw = {'internship__intern__batch__is_agu': True}
        elif request.query_params.get('university') == 'outside':
            kw = {'internship__intern__batch__is_ksauhs': False, 'internship__intern__batch__is_agu': False}
        else:
            kw = {'internship__intern__batch__is_ksauhs': True}
        rotation_requests = rotation_requests.filter(**kw)

        departments_and_months = rotation_requests.values_list('requested_department__department', 'month')
        department_ids = rotation_requests.values_list('requested_department__department', flat=True)
        departments = Department.objects.filter(id__in=department_ids)
        months = rotation_requests.values_list('month', flat=True)

        dms = DepartmentMonthSettings.objects.filter(department__in=departments, month__in=months)
        ms = MonthSettings.objects.filter(month__in=months)
        ds = DepartmentSettings.objects.filter(department__in=departments)

        from hospitals.utils import get_global_settings
        gs = get_global_settings()

        acceptance_settings = self.acceptance_setting_factory(departments, months, dms, ms, ds, gs)

        acceptance_lists = self.acceptance_list_factory(departments_and_months, rotation_requests\
            .prefetch_related('internship__intern'), acceptance_settings, departments_cache=departments)

        sorted_acceptance_lists = sorted(acceptance_lists, key=lambda al: (al.month, al.department.name))

        return Response(AcceptanceListSerializer(sorted_acceptance_lists, many=True).data)

    @list_route(methods=['get'], url_path=r'(?P<department_id>\d+)/(?P<month_id>\d+)', permission_classes=[permissions.IsAuthenticated, IsStaff])
    def retrieve_list(self, request, department_id=None, month_id=None, *args, **kwargs):
        department = get_object_or_404(Department, id=department_id)
        month = Month.from_int(int(month_id))

        acceptance_list = AcceptanceList(department, month)
        return Response(AcceptanceListSerializer(acceptance_list).data)

    @list_route(methods=['post'], url_path=r'(?P<department_id>\d+)/(?P<month_id>\d+)/respond', permission_classes=[permissions.IsAuthenticated, IsStaff])
    def respond(self, request, department_id=None, month_id=None, *args, **kwargs):
        department = get_object_or_404(Department, id=department_id)
        month = Month.from_int(int(month_id))

        serialized = AcceptanceListSerializer(
            data=request.data,
            instance=AcceptanceList(department=department, month=month)
        )
        serialized.is_valid(raise_exception=True)
        acceptance_list = serialized.save()

        acceptance_list.respond_all()

        return Response(status=HTTP_200_OK)