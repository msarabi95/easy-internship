from hospitals import views

api_urls = (
    (r'hospitals', views.HospitalViewSet),
    (r'specialties', views.SpecialtyViewSet),
    (r'departments', views.DepartmentViewSet),
    (r'departments/(?P<specialty>\d+)/(?P<hospital>\d+)', views.DepartmentBySpecialtyAndHospital, 'department-by-s-and-h'),
    (r'global_settings', views.GlobalSettingsViewSet, 'globalsetting'),
    (r'month_settings', views.MonthSettingsViewSet),
    (r'department_settings', views.DepartmentSettingsViewSet),
    (r'department_month_settings', views.DepartmentMonthSettingsViewSet),
    (r'acceptance_settings', views.AcceptanceSettingViewSet, 'acceptancesetting'),
    (r'acceptance_settings/(?P<department_id>\d+)/(?P<month_id>\d+)',
     views.AcceptanceSettingsByDepartmentAndMonth, 'acceptancesetting-by-d-and-m'),
)