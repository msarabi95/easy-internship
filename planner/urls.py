from django.conf.urls import url
from planner import views
from planner.views import RotationRequestFormView

urls = (
    (r'hospitals', views.HospitalViewSet),
    (r'specialties', views.SpecialtyViewSet),
    (r'departments', views.DepartmentViewSet),
    (r'departments/(?P<specialty>\d+)/(?P<hospital>\d+)', views.DepartmentBySpecialtyAndHospital, 'department-by-s-and-h'),
    (r'global_settings', views.GlobalSettingsViewSet, 'globalsetting'),
    (r'month_settings', views.MonthSettingsViewSet),
    (r'department_settings', views.DepartmentSettingsViewSet),
    (r'department_month_settings', views.DepartmentMonthSettingsViewSet),
    (r'acceptance_settings/(?P<department_id>\d+)/(?P<month_id>\d+)', views.AcceptanceSettingsByDepartmentAndMonth, 'acceptancesetting-by-d-and-m'),
    (r'internship_months', views.InternshipMonthViewSet, 'internshipmonth'),
    (r'internship_months/(?P<internship_id>\d+)/(?P<month_id>\d+)', views.InternshipMonthByInternshipAndId, 'internshipmonth-by-i-and-id'),
    (r'internships', views.InternshipViewSet),
    (r'rotations', views.RotationViewSet),
    (r'requested_departments', views.RequestedDepartmentViewSet),
    (r'rotation_requests', views.RotationRequestViewSet),
    (r'rotation_requests/(?P<department_id>\d+)/(?P<month_id>\d+)', views.RotationRequestByDepartmentAndMonth, 'rotationrequest-by-d-and-m'),
    (r'rotation_request_responses', views.RotationRequestResponseViewSet),
    (r'rotation_request_forwards', views.RotationRequestForwardViewSet),
    (r'rotation_request_forward_responses', views.RotationRequestForwardResponseViewSet),
)

urlpatterns = [
    url(r'^rotation-request-form/$', RotationRequestFormView.as_view()),
]
