from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from protractor.test import ProtractorTestCaseMixin

from accounts.factories import UserFactory


class ProtractorTests(ProtractorTestCaseMixin, StaticLiveServerTestCase):
    protractor_conf = 'frontend/tests/protractor.conf.js'
    specs = [
        'frontend/tests/intern/specs.intern.rotations.js'
    ]

    def setUp(self):

        UserFactory.create_batch(10)

        super(ProtractorTests, self).setUp()
