from months import views

api_urls = (
    (r'internship_months', views.InternshipMonthViewSet, 'internshipmonth'),
    (r'internship_months/(?P<internship_id>\d+)/(?P<month_id>\d+)', views.InternshipMonthByInternshipAndId, 'internshipmonth-by-i-and-id'),
    (r'internships', views.InternshipViewSet),
)