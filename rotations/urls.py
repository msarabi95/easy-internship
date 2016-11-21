from django.conf.urls import url

from rotations import views

api_urls = (
    (r'rotations', views.RotationViewSet),
    (r'requested_departments', views.RequestedDepartmentViewSet),
    (r'rotation_requests', views.RotationRequestViewSet),
    (r'rotation_requests/(?P<department_id>\d+)/(?P<month_id>\d+)', views.RotationRequestByDepartmentAndMonth, 'rotationrequest-by-d-and-m'),
    (r'rotation_request_responses', views.RotationRequestResponseViewSet),
    (r'rotation_request_forwards', views.RotationRequestForwardViewSet),
    (r'rotation_request_forward_responses', views.RotationRequestForwardResponseViewSet),
)

urlpatterns = [
    url(r'^rotation-request-form/$', views.RotationRequestFormView.as_view()),
]