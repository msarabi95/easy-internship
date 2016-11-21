# coding=utf-8
from datetime import timedelta

from accounts.models import Profile, Intern
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.test import TestCase
from django.utils import timezone
from month import Month
from planner.models import Specialty, Department, SeatAvailability, Rotation, PlanRequest, \
    RotationRequest, RequestedDepartment, RotationRequestResponse, RotationRequestForward, \
    RotationRequestForwardResponse
from months.models import Internship
from hospitals.models import Hospital, Specialty
from planner.test_factories import InternshipFactory, HospitalFactory, DepartmentFactory, SpecialtyFactory, \
    RotationRequestFactory
from planner.views import PlannerAPI


class UnifiedSetUpMixin(object):
    def setUp(self):
        self.profile_details = {
            "ar_first_name"  : u"محمد",
            "ar_middle_name" : u"علي",
            "ar_last_name"   : u"كلاي",
            "en_first_name"  : "Mohamed",
            "en_middle_name" : "Ali",
            "en_last_name"   : "Clay",
        }

        self.intern_details = {
            "student_number"          : "123456789",
            "badge_number"            : "123456789",
            "phone_number"            : "123456789",
            "mobile_number"           : "123456789",
            "address"                 : "Rawdah, Riyadh, Saudi Arabia",
            "saudi_id_number"         : "1234567890",
            "passport_number"         : "12345678",
            "medical_record_number"   : "123456",
            "contact_person_name"     : "Khaled",
            "contact_person_relation" : "Friend",
            "contact_person_mobile"   : "123456789",
            "contact_person_email"    : "emergency@example.com",
            "gpa"                     : 5.0,
        }

        self.user1 = User.objects.create_user("testuser1", email="test1@example.com", password="12345678")
        Profile.objects.create(user=self.user1, role="intern", **self.profile_details)
        Intern.objects.create(profile=self.user1.profile, **self.intern_details)

        self.internship = Internship.objects.create(
            intern=self.user1.profile.intern,
            start_month=Month(2016, 7),
        )

        self.specialty1 = Specialty.objects.create(
            name="Internal Medicine",
            abbreviation="MED",
            required_months=2,
        )

        self.subspecialty1 = Specialty.objects.create(
            name="Pulmonology",
            abbreviation="MED",
            required_months=0,
            parent_specialty=self.specialty1,
        )

        self.specialty2 = Specialty.objects.create(
            name="Surgery",
            abbreviation="SUR",
            required_months=2,
        )

        self.hospital = Hospital.objects.create(
            name="King Abdulaziz Medical City",
            abbreviation="KAMC",
            is_kamc=True,
        )

        self.department1 = Department.objects.create(
            hospital=self.hospital,
            name="Department of Internal Medicine",
            specialty=self.specialty1,
            contact_name="Some name",
            email="medicine@example.com",
            phone="123456789",
            extension="12345",
        )

        self.section1 = Department.objects.create(
            hospital=self.hospital,
            parent_department=self.department1,
            name="Section of Pulmonology",
            specialty=self.subspecialty1,
            contact_name="",
            email="",
            phone="",
            extension="",
        )

        self.department2 = Department.objects.create(
            hospital=self.hospital,
            name="Department of Surgery",
            specialty=self.specialty2,
            contact_name="Some name",
            email="surgery@example.com",
            phone="123456789",
            extension="12345",
        )

        SeatAvailability.objects.create(
            department=self.department1,
            specialty=self.specialty1,
            month=Month(2016, 6),
            available_seat_count=10,
        )

        SeatAvailability.objects.create(
            department=self.department1,
            specialty=self.specialty1,
            month=Month(2016, 7),
            available_seat_count=15,
        )


class SpecialtyTests(UnifiedSetUpMixin, TestCase):
    def test_is_subspecialty(self):
        self.assertFalse(self.specialty1.is_subspecialty())
        self.assertTrue(self.subspecialty1.is_subspecialty())

    def test_get_general_specialty(self):
        self.assertEqual(self.specialty1.get_general_specialty(),
                         self.specialty1)
        self.assertEqual(self.subspecialty1.get_general_specialty(),
                         self.specialty1)


class DepartmentTests(UnifiedSetUpMixin, TestCase):
    def setUp(self):
        super(DepartmentTests, self).setUp()

        # Remove the parent_department details of section 1
        self.section1.parent_department = None
        self.section1.save()

    def test_get_available_seats(self):
        self.assertEqual(
            self.department1.get_available_seats(Month(2016, 6)),
            10
        )

        self.assertEqual(
            self.department1.get_available_seats(Month(2016, 7)),
            15
        )

        self.assertIsNone(
            self.department1.get_available_seats(Month(2016, 8))
        )

    def test_get_contact_details(self):
        contact_details = {
            "contact_name": "Some name",
            "email"       : "medicine@example.com",
            "phone"       : "123456789",
            "extension"   : "12345",
        }

        self.assertEqual(
            self.department1.get_contact_details(),
            contact_details
        )

        self.assertEqual(
            self.section1.get_contact_details(),
            None,
        )

        self.section1.parent_department = self.department1
        self.section1.save()

        self.assertEqual(
            self.section1.get_contact_details(),
            contact_details,
        )


class InternshipTests(UnifiedSetUpMixin, TestCase):
    def test_clean(self):
        # An empty internship should raise a ValidationError
        self.assertRaises(ValidationError, self.internship.clean)

        # Create 12 rotations of the same type
        self.internship.rotations.bulk_create(
            [Rotation(internship=self.internship,
                      month=Month(2016, idx),
                      specialty=self.specialty1,
                      department=self.department1)
             for idx in range(1, 13)]
        )

        # This should still raise an error
        self.assertRaises(ValidationError, self.internship.clean)

        # Delete 2 rotations and replace them by surgery rotations
        self.internship.rotations.last().delete()
        self.internship.rotations.last().delete()

        self.internship.rotations.bulk_create(
            [Rotation(internship=self.internship,
                      month=Month(2016, idx),
                      specialty=self.specialty2,
                      department=self.department2)
             for idx in range(11, 13)]
        )

        try:
            self.internship.clean()
        except ValidationError:
            raise AssertionError("Internship.clean() raised a `ValidationError` unexpectedly.")


# FIXME: Remove PlanRequest tests
class PlanRequestTests(UnifiedSetUpMixin, TestCase):
    def setUp(self):
        super(PlanRequestTests, self).setUp()

        self.internship.rotations.bulk_create([
            Rotation(internship=self.internship,
                     month=Month(2016, idx),
                     specialty=self.specialty1,
                     department=self.department1)
             for idx in range(1, 7)
        ] + [
            Rotation(internship=self.internship,
                     month=Month(2016, idx),
                     specialty=self.specialty2,
                     department=self.department2)
             for idx in range(7, 13)
        ])

        self.plan_request = PlanRequest.objects.create(internship=self.internship)

    def test_get_predicted_plan(self):

        self.plan_request.rotation_requests.bulk_create([
            RotationRequest(
                plan_request=self.plan_request,
                month=Month(2016, 3),
                specialty=self.specialty1,
                requested_department=RequestedDepartment.objects.create(department=self.department1, is_in_database=True),
                delete=True,
            ),
            RotationRequest(
                plan_request=self.plan_request,
                month=Month(2016, 3),
                specialty=self.subspecialty1,
                requested_department=RequestedDepartment.objects.create(department=self.section1, is_in_database=True),
            )
        ])

        predicted_plan = self.plan_request.get_predicted_plan()

        self.assertEqual(
            len(filter(lambda rotation: rotation.specialty == self.specialty1, predicted_plan.rotations.all())),
            5
        )
        self.assertEqual(
            len(filter(lambda rotation: rotation.specialty == self.subspecialty1, predicted_plan.rotations.all())),
            1
        )
        self.assertEqual(
            len(filter(lambda rotation: rotation.specialty == self.specialty2, predicted_plan.rotations.all())),
            6
        )

        print self.plan_request.rotation_requests.all()

        self.plan_request.rotation_requests.all().delete()

        self.plan_request.rotation_requests.bulk_create([
            RotationRequest(
                plan_request=self.plan_request,
                month=Month(2016, 12),
                specialty=self.specialty2,
                requested_department=RequestedDepartment.objects.create(department=self.department2, is_in_database=True),
                delete=True,
            ),
            RotationRequest(
                plan_request=self.plan_request,
                month=Month(2017, 1),
                specialty=self.specialty2,
                requested_department=RequestedDepartment.objects.create(department=self.department2, is_in_database=True)
            )
        ])

        predicted_plan = self.plan_request.get_predicted_plan()

        self.assertEqual(
            len(filter(lambda rotation: rotation.specialty == self.specialty1, predicted_plan.rotations.all())),
            6
        )
        self.assertEqual(
            len(filter(lambda rotation: rotation.specialty == self.subspecialty1, predicted_plan.rotations.all())),
            0
        )
        self.assertEqual(
            len(filter(lambda rotation: rotation.specialty == self.specialty2, predicted_plan.rotations.all())),
            6
        )

        self.assertNotIn(Month(2016, 12), predicted_plan.rotations.values_list("month", flat=True))

        self.internship.rotations.all().delete()
        self.plan_request.rotation_requests.all().delete()
        self.plan_request.rotation_requests.bulk_create([
            RotationRequest(
                plan_request=self.plan_request,
                month=Month(2016, idx),
                specialty=self.specialty1,
                requested_department=RequestedDepartment.objects.create(department=self.department1,
                                                                        is_in_database=True))
             for idx in range(1, 7)
        ] + [
            RotationRequest(
                plan_request=self.plan_request,
                month=Month(2016, idx),
                specialty=self.specialty2,
                requested_department=RequestedDepartment.objects.create(department=self.department2,
                                                                        is_in_database=True))
             for idx in range(7, 13)
        ])

        predicted_plan = self.plan_request.get_predicted_plan()
        self.assertEqual(predicted_plan.rotations.all().count(), 12)
        self.assertEqual(
            len(filter(lambda rot: rot.specialty == self.specialty1, predicted_plan.rotations.all())),
            6
        )
        self.assertEqual(
            len(filter(lambda rot: rot.specialty == self.specialty2, predicted_plan.rotations.all())),
            6
        )

    def test_clean(self):
        self.plan_request.rotation_requests.all().delete()
        # An empty plan should raise a `ValidationError`
        self.assertRaises(ValidationError, self.plan_request.clean)

        self.plan_request.rotation_requests.bulk_create([
            RotationRequest(
                plan_request=self.plan_request,
                month=Month(2016, idx),
                specialty=self.specialty2,
                requested_department=RequestedDepartment.objects.create(department=self.department2, is_in_database=True),
            ) for idx in range(1, 7)
        ] + [
            RotationRequest(
                plan_request=self.plan_request,
                month=Month(2016, idx),
                specialty=self.specialty1,
                requested_department=RequestedDepartment.objects.create(department=self.department1, is_in_database=True),
                delete=True,
            ) for idx in range(1, 7)
        ])

        # A plan request that doesn't makes the internship plan not satisfy the minimum required
        # months of each specialty should raise a `ValidationError`
        self.assertRaises(ValidationError, self.plan_request.clean)

        self.plan_request.rotation_requests.all().delete()

        self.plan_request.rotation_requests.create(
            month=Month(2017, 1),
            specialty=self.subspecialty1,
            requested_department=RequestedDepartment.objects.create(department=self.section1, is_in_database=True)
        )

        # A plan request that makes the internship plan unequal in length to 12 months
        # should raise a `ValidationError`
        self.assertRaises(ValidationError, self.plan_request.clean)

        self.plan_request.rotation_requests.create(
            month=Month(2016, 12),
            specialty=self.specialty2,
            requested_department=RequestedDepartment.objects.create(department=self.department2, is_in_database=True),
            delete=True,
        )

        # A valid plan request should raise any errors.
        try:
            self.plan_request.clean()
        except ValidationError as e:
            print e
            raise AssertionError("PlanRequest.clean() raised a `ValidationError` unexpectedly.")

    def test_check_closure(self):
        # If .clean() was to be called, the following plan request will not validate;
        # However, it's sufficient for our testing purposes here.
        self.plan_request.rotation_requests.bulk_create([
            RotationRequest(
                plan_request=self.plan_request,
                month=Month(2016, 6),
                specialty=self.specialty1,
                requested_department=RequestedDepartment.objects.create(department=self.department1, is_in_database=True),
            ),
            RotationRequest(
                plan_request=self.plan_request,
                month=Month(2016, 7),
                specialty=self.specialty2,
                requested_department=RequestedDepartment.objects.create(department=self.department2, is_in_database=True),
            ),
        ])

        # A plan request with no responses to any of its rotation requests should be "open"
        self.assertFalse(self.plan_request.check_closure())
        self.assertFalse(self.plan_request.is_closed)
        self.assertIsNone(self.plan_request.closure_datetime)

        # Create a response to one of the rotation requests
        response1 = RotationRequestResponse(
            rotation_request=self.plan_request.rotation_requests.first(),
            is_approved=True,
        )
        response1.save()

        # The plan request should still be "open"
        self.assertFalse(self.plan_request.check_closure())
        self.assertFalse(self.plan_request.is_closed)
        self.assertIsNone(self.plan_request.closure_datetime)

        # Create a response to the second rotation request
        response2 = RotationRequestResponse(
            rotation_request=self.plan_request.rotation_requests.last(),
            is_approved=True,
        )
        response2.save()

        # The plan request should now be closed
        self.assertTrue(self.plan_request.check_closure())
        self.assertTrue(self.plan_request.is_closed)
        self.assertEqual(self.plan_request.closure_datetime, response2.response_datetime)

    def test_submit(self):
        self.plan_request.rotation_requests.bulk_create([
            RotationRequest(
                plan_request=self.plan_request,
                month=Month(2016, 6),
                specialty=self.specialty1,
                requested_department=RequestedDepartment.objects.create(department=self.department1, is_in_database=True),
                delete=True,
            ),
            RotationRequest(
                plan_request=self.plan_request,
                month=Month(2016, 6),
                specialty=self.specialty2,
                requested_department=RequestedDepartment.objects.create(department=self.department2, is_in_database=True),
            ),
        ])

        self.plan_request.submit()

        self.assertTrue(self.plan_request.is_submitted)
        self.assertIsNotNone(self.plan_request.submission_datetime)
        self.assertGreaterEqual(timezone.now(), self.plan_request.submission_datetime)
        self.assertGreater(self.plan_request.submission_datetime, timezone.now() - timedelta(seconds=1))

        # An exception should be raised if there's an attempt to submit an already submitted plan request
        self.assertRaises(Exception, self.plan_request.submit)


class RequestedDepartmentTests(UnifiedSetUpMixin, TestCase):
    def setUp(self):
        super(RequestedDepartmentTests, self).setUp()
        
        self.requested_department1 = RequestedDepartment.objects.create(
            department=self.department1,
            is_in_database=True,
        )
        
        self.requested_department2 = RequestedDepartment.objects.create(
            is_in_database=False,
            department_hospital=self.hospital,
            department_name="Department of Pediatrics",
            department_specialty=Specialty.objects.create(
                name="Pediatrics",
                abbreviation="PED",
                required_months=2,
            ),
            department_contact_name="Some body",
            department_email="pediatrics@example.com",
            department_phone="123456789",
            department_extension="12345",
        )

        self.requested_department3 = RequestedDepartment.objects.create(
            is_in_database=True,
        )

    def test_clean(self):
        # Test a RequestedDepartment that has the `department` field filled only.
        # This shouldn't raise any errors.
        try:
            self.requested_department1.clean()
        except ValidationError:
            raise AssertionError("RequestedDepartment.clean() raised a `ValidationError` unexpectedly.")
        
        # Do the same test but with an incorrect `is_in_database` flag
        self.requested_department1.is_in_database = False
        self.assertRaises(ValidationError, self.requested_department1.clean)
        
        # Test a RequestedDepartment that has the department_* details fields filled only.
        # This shouldn't raise any errors.
        try:
            self.requested_department2.clean()
        except ValidationError:
            raise AssertionError("RequestedDepartment.clean() raised a `ValidationError` unexpectedly.")
    
        # Do the same test but with an incorrect `is_in_database` flag
        self.requested_department2.is_in_database = True
        self.assertRaises(ValidationError, self.requested_department2.clean)
        
        # Test a RequestedDepartment that has both `department` field and department_* details 
        # fields filled.
        # This should raise a ValidationError.
        self.requested_department1.__dict__.update({
            "department_hospital": self.hospital,
            "department_name": "Department of Internal Medicine",
            "department_specialty": self.specialty1,
            "department_contact_name":"Some body",
            "department_email": "medicine@example.com",
            "department_phone": "123456789",
            "department_extension": "12345",
        })
        self.assertRaises(ValidationError, self.requested_department1.clean)

        # Test a RequestedDepartment that has both `department` field and department_* details
        # fields empty.
        # This should raise a ValidationError.
        self.assertRaises(ValidationError, self.requested_department3.clean)

    def test_link_to_existing_department(self):
        # Try linking to a Department object that doesn't exist in the database.
        # This should raise a ValidationError.
        self.assertRaises(ObjectDoesNotExist,
                          self.requested_department2.link_to_existing_department,
                          Department())

        # Try linking to a Department object from the database.
        try:
            self.requested_department2.link_to_existing_department(self.department2)
        except ObjectDoesNotExist:
            raise AssertionError("RequestedDepartment.link_to_existing_department() "
                                 "raised an `ObjectDoesNotExist` unexpectedly.")

        # Assert that the `is_in_database` flag is updated
        self.assertTrue(self.requested_department2.is_in_database)

        # Assert that the `department` field is set to self.department2
        self.assertEqual(self.requested_department2.department, self.department2)

        # Assert that the department_* details fields have been emptied
        department_details_empty = all([
            self.requested_department2.department_hospital is None,
            self.requested_department2.department_name == "",
            self.requested_department2.department_specialty is None,
            self.requested_department2.department_contact_name == "",
            self.requested_department2.department_email == "",
            self.requested_department2.department_phone == "",
            self.requested_department2.department_extension == "",
        ])
        self.assertTrue(department_details_empty)

    def test_add_to_database(self):
        # Test with a RequestedDepartment that's already linked to a database Department
        self.assertRaises(Exception, self.requested_department1.add_to_database)

        # Test with a RequestedDepartment that contains information of a new department
        try:
            self.requested_department2.add_to_database()
        except Exception:
            raise AssertionError("RequestedDepartment.add_to_database() raised an `Exception` unexpectedly.")

        # Assert that a new department has been added to the database
        self.assertEqual(Department.objects.all().count(), 4)
        self.assertEqual(Department.objects.last().name, "Department of Pediatrics")

        # Assert the newly created department is linked to the RequestedDepartment object
        self.assertEqual(Department.objects.last(), self.requested_department2.department)


class RotationRequestTests(UnifiedSetUpMixin, TestCase):
    def setUp(self):
        super(RotationRequestTests, self).setUp()
        self.plan_request = PlanRequest.objects.create(
            internship=self.internship,
        )

        self.rotation_request1 = self.plan_request.rotation_requests.create(
            month=Month(2016, 6),
            specialty=self.specialty1,
            requested_department=RequestedDepartment.objects.create(department=self.department1, is_in_database=True)
        )

        self.rotation_request2 = self.plan_request.rotation_requests.create(
            month=Month(2016, 7),
            specialty=self.specialty2,
            requested_department=RequestedDepartment.objects.create(department=self.department2, is_in_database=True)
        )

    def test_get_status(self):
        # Status should be pending if the request hasn't received a response a forward yet
        self.assertEqual(self.rotation_request1.get_status(), RotationRequest.PENDING_STATUS)

        # Status should be forwarded if the request has been forwarded
        self.forward1 = RotationRequestForward.objects.create(rotation_request=self.rotation_request1)
        self.assertEqual(self.rotation_request1.get_status(), RotationRequest.FORWARDED_STATUS)

        # Status should be reviewed if either:
        # (1) the request received a response
        # (2) the request has been forwarded and the forward received a response
        self.rotation_request1response = RotationRequestResponse.objects.create(
            rotation_request=self.rotation_request2,
            is_approved=True,
        )
        self.assertEqual(self.rotation_request2.get_status(), RotationRequest.REVIEWED_STATUS)

        self.forward1response = RotationRequestForwardResponse(
            forward=self.forward1,
            is_approved=True,
            response_memo="",
            respondent_name="Patricia Johnson",
        )
        self.assertEqual(self.rotation_request1.get_status(), RotationRequest.REVIEWED_STATUS)

    def test_respond(self):
        # respond should create a response object and associate it with the RotationRequest
        self.rotation_request1.respond(True)
        self.assertIsNotNone(self.rotation_request1.response)
        self.assertTrue(self.rotation_request1.response.is_approved)

        # An error should be raised if responding is attempted for a request that's already been responded to
        self.assertRaises(Exception, self.rotation_request1.respond, True)

    def test_forward_request(self):
        # forward_request should create a forward object and associate it with the RotationRequest
        self.rotation_request1.forward_request()
        self.assertIsNotNone(self.rotation_request1.forward)

        # An error should be raised if forwarding is attempted for an already forwarded request
        self.assertRaises(Exception, self.rotation_request1.forward_request)


class RotationRequestForwardTests(UnifiedSetUpMixin, TestCase):
    def setUp(self):
        super(RotationRequestForwardTests, self).setUp()
        self.plan_request = PlanRequest.objects.create(
            internship=self.internship,
        )

        self.rotation_request1 = self.plan_request.rotation_requests.create(
            month=Month(2016, 6),
            specialty=self.specialty1,
            requested_department=RequestedDepartment.objects.create(department=self.department1, is_in_database=True)
        )

        self.rotation_request1.forward_request()
        self.forward1 = self.rotation_request1.forward

    def test_respond(self):
        # respond should create a response object and associate it with the RotationRequestForward
        self.forward1.respond(True, response_memo="", respondent_name="Julian Brown")
        self.assertIsNotNone(self.forward1.response)
        self.assertTrue(self.forward1.response.is_approved)
        self.assertEqual(self.forward1.response.respondent_name, "Julian Brown")

        # An error should be raised if responding is attempted for a forward that's already been responded to
        self.assertRaises(Exception, self.forward1.respond, True)


class PlannerAPITests(TestCase):
    def setUp(self):
        DepartmentFactory()  # Create a department, a hospital, and a specialty
        self.internship = InternshipFactory()
        self.api = PlannerAPI()

        class MockRequest:
            def __init__(self, user=None):
                self.user = user

        self.api.request = MockRequest(user=self.internship.intern.profile.user)

    def test_create_request(self):
        month = int(Month(2016, 9))
        request_data = {
            'specialtyID': 1,
            'requested_department': {
                'departmentID': 1,
                'department_hospitalID': None,
                'department_name': "",
                'department_specialtyID': None,
                'department_contact_name': "",
                'department_email': "",
                'department_phone': "",
                'department_extension': "",
            },
            'delete': False,
        }

        self.api.create_request(month, request_data)

        self.assertTrue(self.internship.plan_requests.exists())
        self.assertTrue(self.internship.plan_requests.last().rotation_requests.filter(month=Month.from_int(month)).exists())

        month2 = int(Month(2016, 10))
        request_data2 = {
            'specialtyID': 1,
            'requested_department': {
                'departmentID': None,
                'department_hospitalID': 1,
                'department_name': "Department of Whatever",
                'department_specialtyID': 1,
                'department_contact_name': "Whoever",
                'department_email': "dept@example.com",
                'department_phone': "123",
                'department_extension': "123",
            },
            'delete': False,
        }

        self.api.create_request(month2, request_data2)

        self.assertEqual(self.internship.plan_requests.count(), 1)
        self.assertTrue(self.internship.plan_requests.last().rotation_requests.filter(
            month=Month.from_int(month2)
        ).exists())

        rr = self.internship.plan_requests.last().rotation_requests.get(month=Month.from_int(month2))
        self.assertEqual(rr.requested_department.get_department().name, "Department of Whatever")

    def test_update_request(self):
        raw_month = Month(2016, 11)
        month = int(raw_month)
        self.rr = RotationRequestFactory(plan_request__internship=self.internship, month=raw_month)

        request_data = {
            'specialtyID': 1,
            'requested_department': {
                'departmentID': 1,
                'department_hospitalID': None,
                'department_name': "",
                'department_specialtyID': None,
                'department_contact_name': "",
                'department_email': "",
                'department_phone': "",
                'department_extension': "",
            },
            'delete': True,
        }

        self.api.update_request(month, request_data)

        self.rr.refresh_from_db()
        self.assertTrue(self.rr.delete)

    def test_delete_request(self):
        raw_month = Month(2016, 12)
        month = int(raw_month)
        self.rr = RotationRequestFactory(plan_request__internship=self.internship, month=raw_month)

        self.assertIn(self.rr, RotationRequest.objects.all())

        self.api.delete_request(month)

        self.assertNotIn(self.rr, RotationRequest.objects.all())
