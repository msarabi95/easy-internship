from months import views

api_urls = (
    (r'internship_months', views.InternshipMonthViewSet, 'internshipmonth'),
    (r'internship_months/(?P<internship_id>\d+)/(?P<month_id>\d+)', views.InternshipMonthByInternshipAndId, 'internshipmonth-by-i-and-id'),
    (r'internships', views.InternshipViewSet),
    (r'freezes', views.FreezeViewSet),
    (r'freeze_requests', views.FreezeRequestViewSet),
    (r'freeze_request_responses', views.FreezeRequestResponseViewSet),
    (r'freeze_cancel_requests', views.FreezeCancelRequestViewSet),
    (r'freeze_cancel_request_responses', views.FreezeCancelRequestResponseViewSet),
)
