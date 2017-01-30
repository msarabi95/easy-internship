from django.conf.urls import url

from rotations import views

api_urls = (
    (r'rotations', views.RotationViewSet),
    (r'rotation_requests', views.RotationRequestViewSet),
    (r'rotation_request_responses', views.RotationRequestResponseViewSet),
    (r'rotation_request_forwards', views.RotationRequestForwardViewSet),
    (r'acceptance_lists', views.AcceptanceListViewSet, 'acceptancelist'),
)

urlpatterns = [
    # url(r'^rotation-request-form/$', views.RotationRequestFormView.as_view()),
]
