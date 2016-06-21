from django.test import TestCase
from planner.models import Specialty


class SpecialtyTests(TestCase):
    def setUp(self):
        self.general_specialty = Specialty.objects.create(
            name="General Pediatrics",
            abbreviation="PED",
            required_months=2,
            parent_specialty=None,
        )

        self.subspecialty = Specialty.objects.create(
            name="Pediatric Neurology",
            abbreviation="PED",
            required_months=0,
            parent_specialty=self.general_specialty,
        )

    def test_is_subspecialty(self):
        self.assertFalse(self.general_specialty.is_subspecialty())
        self.assertTrue(self.subspecialty.is_subspecialty())

    def test_get_general_specialty(self):
        self.assertEqual(self.general_specialty.get_general_specialty(),
                         self.general_specialty)
        self.assertEqual(self.subspecialty.get_general_specialty(),
                         self.general_specialty)


class DepartmentTests(TestCase):
    def setUp(self):
        pass

    def test_get_available_seats(self):
        pass

    def test_get_contact_details(self):
        pass


class InternshipTests(TestCase):
    def setUp(self):
        pass

    def test_clean(self):
        pass


class PlanRequestTests(TestCase):
    def setUp(self):
        pass

    def test_get_predicted_plan(self):
        pass

    def test_clean(self):
        pass

    def test_check_closure(self):
        pass

    def test_submit(self):
        pass


class RequestedDepartmentTests(TestCase):
    def setUp(self):
        pass

    def test_clean(self):
        pass

    def test_link_to_existing_department(self):
        pass

    def test_add_to_database(self):
        pass

    def test_get_department(self):  # Is it necessary?
        pass


class RotationRequestTests(TestCase):
    def setUp(self):
        pass

    def test_get_status(self):
        pass

    def test_get_details(self):
        pass

    def test_respond(self):
        pass

    def test_forward(self):
        pass


class RotationRequestForwardTests(TestCase):
    def setUp(self):
        pass

    def test_respond(self):
        pass
