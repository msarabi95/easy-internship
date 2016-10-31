from django.conf.urls import url
from planner import views
from planner.views import RotationRequestFormView
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'hospitals', views.HospitalViewSet)
router.register(r'specialties', views.SpecialtyViewSet)
router.register(r'departments', views.DepartmentViewSet)
router.register(r'global_settings', views.GlobalSettingsViewSet, base_name='globalsetting')
router.register(r'month_settings', views.MonthSettingsViewSet)
router.register(r'department_settings', views.DepartmentSettingsViewSet)
router.register(r'department_month_settings', views.DepartmentMonthSettingsViewSet)
router.register(r'internship_months', views.InternshipMonthViewSet, base_name='internshipmonth')
router.register(r'internships', views.InternshipViewSet)
router.register(r'rotations', views.RotationViewSet)
router.register(r'requested_departments', views.RequestedDepartmentViewSet)
router.register(r'rotation_requests', views.RotationRequestViewSet)
router.register(r'rotation_request_responses', views.RotationRequestResponseViewSet)
router.register(r'rotation_request_forwards', views.RotationRequestForwardViewSet)
router.register(r'rotation_request_forward_responses', views.RotationRequestForwardResponseViewSet)

custom_departments_view_url = url(r'^api/departments/(?P<specialty>\d+)/(?P<hospital>\d+)/$',
                                  views.DepartmentBySpecialtyAndHospital.as_view())

custom_internship_months_view_url = url(r'^api/internship_months/(?P<internship_id>\d+)/(?P<month_id>\d+)/$',
                                        views.InternshipMonthByInternshipAndId.as_view())

acceptance_settings_by_department_and_month_id = url(r'^api/acceptance_settings/(?P<department_id>\d+)/(?P<month_id>\d+)/$',
                                                        views.AcceptanceSettingsByDepartmentAndMonth.as_view())

urlpatterns = [
    url(r'^rotation-request-form/$', RotationRequestFormView.as_view()),
]
