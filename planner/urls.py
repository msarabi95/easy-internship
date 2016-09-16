from django.conf.urls import url
from planner import views
from planner.views import RotationRequestFormView
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'hospitals', views.HospitalViewSet)
router.register(r'specialties', views.SpecialtyViewSet)
router.register(r'departments', views.DepartmentViewSet)
router.register(r'seat_availabilities', views.SeatAvailabilityViewSet)
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

urlpatterns = [
    url(r'^rotation-request-form/$', RotationRequestFormView.as_view()),
]
