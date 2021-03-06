from datetime import datetime

from django.contrib import messages
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils import timezone

from month import Month
from rest_framework import viewsets, permissions
from rest_framework.decorators import list_route
from rest_framework.exceptions import ParseError, MethodNotAllowed
from rest_framework.response import Response

from hospitals.models import Hospital, Specialty, Department, MonthSettings, DepartmentSettings, \
    DepartmentMonthSettings, AcceptanceSetting, SeatSetting
from hospitals.serializers import HospitalSerializer, SpecialtySerializer, DepartmentSerializer, \
    MonthSettingsSerializer, DepartmentSettingsSerializer, DepartmentMonthSettingsSerializer, \
    AcceptanceSettingSerializer, SeatSettingSerializer, ExtendedHospitalSerializer
from hospitals.utils import get_global_acceptance_criterion, set_global_acceptance_criterion, \
    get_global_acceptance_start_date_interval, set_global_acceptance_start_date_interval, \
    get_global_acceptance_end_date_interval, set_global_acceptance_end_date_interval


class HospitalViewSet(viewsets.ModelViewSet):
    serializer_class = HospitalSerializer
    queryset = Hospital.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user.profile, 'intern') and self.request.user.profile.intern.is_outside_intern:
            return self.queryset.filter(is_kamc=True)
        return self.queryset.all()

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed

    @list_route(methods=['get'], url_path=r'with_acceptance_details/(?P<month_id>\d+)/(?P<specialty_id>\d+)')
    def with_specialty_details(self, request, month_id, specialty_id):
        month = Month.from_int(int(month_id))
        specialty = get_object_or_404(Specialty, id=specialty_id)
        hospitals = self.get_queryset().prefetch_related('departments')
        for hospital in hospitals:
            hospital.specialty_departments = \
                filter(lambda dep: dep.specialty == specialty, hospital.departments.all())

            for dep in hospital.specialty_departments:
                dep.acceptance_setting = AcceptanceSetting(
                    dep,
                    month,
                )

        serialized = ExtendedHospitalSerializer(hospitals, many=True)
        return Response(serialized.data)


class SpecialtyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SpecialtySerializer
    queryset = Specialty.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class GlobalSettingsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated]


class DepartmentSettingsViewSet(SettingsMessagesMixin, viewsets.ModelViewSet):
    serializer_class = DepartmentSettingsSerializer
    queryset = DepartmentSettings.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class DepartmentMonthSettingsViewSet(SettingsMessagesMixin, viewsets.ModelViewSet):
    serializer_class = DepartmentMonthSettingsSerializer
    queryset = DepartmentMonthSettings.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @list_route(methods=['get'], url_path='starting_month')
    def get_display_starting_month(self, request):
        return Response({'id': int(Month.from_date(datetime(timezone.now().year, 1, 1)))})


class AcceptanceSettingViewSet(viewsets.ViewSet):
    serializer_class = AcceptanceSettingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @list_route(methods=['get'])
    def as_table(self, request, *args, **kwargs):

        if len(request.query_params.keys()) == 0:
            raise ParseError(detail="No query parameters were specified.")  # FIXME: Is this the most accurate error?

        year = request.query_params.get('year')
        hospital = request.query_params.get('hospital')

        if year is None or hospital is None:
            raise ParseError(detail="Both `year` and `hospital` query parameters should be specified.")

        months = [Month(int(year), month) for month in range(1, 13)]
        departments = Department.objects.filter(hospital__id=hospital)

        settings = []

        for department in departments:
            dept_settings = []
            for month in months:
                dept_settings.append(
                    self.serializer_class(AcceptanceSetting(department, month)).data
                )
            settings.append(dept_settings)

        return Response(settings)


class AcceptanceSettingsByDepartmentAndMonth(viewsets.ViewSet):
    serializer_class = AcceptanceSettingSerializer
    permission_classes = [permissions.IsAuthenticated]

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


class SeatSettingViewSet(viewsets.ViewSet):
    serializer_class = SeatSettingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @list_route(methods=['get'])
    def as_table(self, request, *args, **kwargs):

        if len(request.query_params.keys()) == 0:
            raise ParseError(detail="No query parameters were specified.")  # FIXME: Is this the most accurate error?

        year = request.query_params.get('year')
        hospital = request.query_params.get('hospital')

        if year is None or hospital is None:
            raise ParseError(detail="Both `year` and `hospital` query parameters should be specified.")

        months = [Month(int(year), month) for month in range(1, 13)]
        departments = Department.objects.filter(hospital__id=hospital).prefetch_related(
            'monthly_settings',
            'rotations',
            'department_requests__rotationrequest__response',
        )

        settings = []

        for department in departments:
            dept_settings = []
            for month in months:
                ss = SeatSetting(department, month)
                dept_settings.append(
                    self.serializer_class(ss).data
                )
            settings.append(dept_settings)

        return Response(settings)