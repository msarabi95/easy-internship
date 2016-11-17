from leaves import views

urls = (
    (r'leave_types', views.LeaveTypeViewSet),
    (r'leave_settings', views.LeaveSettingViewSet),
    (r'leave_requests', views.LeaveRequestViewSet),
    (r'leave_request_responses', views.LeaveRequestResponseViewSet),
    (r'leaves', views.LeaveViewSet),
    (r'leave_cancel_requests', views.LeaveCancelRequestViewSet),
    (r'leave_cancel_request_responses', views.LeaveCancelRequestResponseViewSet),
)
