from django.conf.urls import url

from rotations import views

api_urls = (
    (r'rotations', views.RotationViewSet),
    (r'requested_departments', views.RequestedDepartmentViewSet),
    (r'rotation_requests', views.RotationRequestViewSet),
    (r'rotation_requests/(?P<department_id>\d+)/(?P<month_id>\d+)', views.RotationRequestByDepartmentAndMonth, 'rotationrequest-by-d-and-m'),
    (r'rotation_request_responses', views.RotationRequestResponseViewSet),
    (r'rotation_request_forwards', views.RotationRequestForwardViewSet),
    (r'acceptance_lists', views.AcceptanceListViewSet, 'acceptancelist'),
)
