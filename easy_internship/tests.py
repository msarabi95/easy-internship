from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from protractor.test import ProtractorTestCaseMixin

from accounts.factories import UserFactory
from hospitals.factories import HospitalFactory, SpecialtyFactory
from hospitals.models import Hospital, Department, Specialty


class ProtractorTests(ProtractorTestCaseMixin, StaticLiveServerTestCase):
    protractor_conf = 'frontend/tests/protractor.conf.js'
    specs = [
        'frontend/tests/intern/specs.intern.rotations.js'
    ]

    def setUp(self):

        HospitalFactory.create_batch(5)
        Hospital.objects.filter(id=1).update(is_kamc=True)

        SpecialtyFactory.create_batch(5)

        Department.objects.create(
            hospital=Hospital.objects.first(),
            specialty=Specialty.objects.first(),
            contact_name="",
            contact_position="",
            email="",
            phone="",
            extension="",
        )

        UserFactory.create_batch(10)

        super(ProtractorTests, self).setUp()

    def test_run(self):
        self.assertEqual(Hospital.objects.count(), 5)

        super(ProtractorTests, self).test_run()

        self.assertEqual(Hospital.objects.count(), 7)