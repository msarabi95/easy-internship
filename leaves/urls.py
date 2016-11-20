from django.conf.urls import url
from leaves import views
from leaves.views import LeaveRequestFormView

api_urls = (
    (r'leave_types', views.LeaveTypeViewSet),
    (r'leave_settings', views.LeaveSettingViewSet),
    (r'leave_requests', views.LeaveRequestViewSet),
    (r'leave_request_responses', views.LeaveRequestResponseViewSet),
    (r'leaves', views.LeaveViewSet),
    (r'leave_cancel_requests', views.LeaveCancelRequestViewSet),
    (r'leave_cancel_request_responses', views.LeaveCancelRequestResponseViewSet),
)

urlpatterns = [
    url(r'^leave-request-form/$', LeaveRequestFormView.as_view()),
]
