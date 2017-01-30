from django.apps import apps
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from protractor.test import ProtractorTestCaseMixin

from accounts.factories import UserFactory
from hospitals.factories import HospitalFactory, SpecialtyFactory
from hospitals.models import Hospital, Specialty


class MigrationTestCase(TransactionTestCase):
    """
    Source: https://www.caktusgroup.com/blog/2016/02/02/writing-unit-tests-django-migrations/
    """

    @property
    def app(self):
        return apps.get_containing_app_config(type(self).__module__).name

    migrate_from = None
    migrate_to = None

    def setUp(self):
        assert self.migrate_from and self.migrate_to, \
            "TestCase '{}' must define migrate_from and migrate_to properties".format(type(self).__name__)
        self.migrate_from = [(self.app, self.migrate_from)]
        self.migrate_to = [(self.app, self.migrate_to)]
        executor = MigrationExecutor(connection)
        old_apps = executor.loader.project_state(self.migrate_from).apps

        # Reverse to the original migration
        executor.migrate(self.migrate_from)

        self.setUpBeforeMigration(old_apps)

        # Run the migration to test
        executor.migrate(self.migrate_to)

        self.apps = executor.loader.project_state(self.migrate_to).apps

    def setUpBeforeMigration(self, apps):
        pass


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