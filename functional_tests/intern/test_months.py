from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from month import Month
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from accounts.factories import UserFactory

from functional_tests.intern.page_objects.months import MonthListPage
from functional_tests.po_accounts import SigninPage
from months.factories import FreezeRequestFactory, FreezeFactory, FreezeCancelRequestFactory
from rotations.factories import RotationRequestFactory, RotationFactory


class InternshipMonthListTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(InternshipMonthListTests, cls).setUpClass()
        cls.browser = webdriver.Chrome(executable_path="/Users/MSArabi/Downloads/chromedriver")
        cls.browser.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(InternshipMonthListTests, cls).tearDownClass()

    def setUp(self):
        # Set up database
        self.intern = UserFactory()

        # By default, internships start at July 2017
        internship = self.intern.profile.intern.internship

        # Create a rotation request for August 2017
        RotationRequestFactory(
            internship=internship,
            month=Month(2017, 8),
            specialty__name="Internal Medicine",
            hospital__name="King Abdulaziz Medical City",
        )

        # Create a rotation for September 2017
        RotationFactory(
            internship=internship,
            month=Month(2017, 9),
            specialty__name="Internal Medicine",
            hospital__name="King Abdulaziz Medical City",
            rotation_request__month=Month(2017, 9),
        )

        # Create a rotation request and a rotation for October 2017
        RotationRequestFactory(
            internship=internship,
            month=Month(2017, 10),
            specialty__name="Pediatrics",
            hospital__name="King Fahad Medical City",
        )
        RotationFactory(
            internship=internship,
            month=Month(2017, 10),
            rotation_request__month=Month(2017, 10),
            specialty__name="Pediatrics",
            hospital__name="King Abdulaziz Medical City",
        )

        # Create a rotation for November 2017 with a rotation cancellation request
        RotationFactory(
            internship=internship,
            month=Month(2017, 11),
            rotation_request__month=Month(2017, 11),
            specialty__name="Pediatrics",
            hospital__name="King Abdulaziz Medical City",
        )
        RotationRequestFactory(
            internship=internship,
            month=Month(2017, 11),
            is_delete=True,
        )

        # Create a freeze request for December 2017
        FreezeRequestFactory(
            intern=self.intern,
            month=Month(2017, 12),
        )

        # Create a freeze for January 2018
        FreezeFactory(
            intern=self.intern,
            month=Month(2018, 1),
            freeze_request__month=Month(2018, 1),
        )

        # Create a freeze for February 2018 with a freeze cancellation request
        FreezeFactory(
            intern=self.intern,
            month=Month(2018, 2),
            freeze_request__month=Month(2018, 2),
        )
        FreezeCancelRequestFactory(
            intern=self.intern,
            month=Month(2018, 2),
        )

        # Login
        login_page = SigninPage(self.browser, self.live_server_url)
        login_page.navigate()
        login_page.login(
            self.intern.username,
            "123",
        )

        # Set-up and navigate to page
        self.page = MonthListPage(browser=self.browser, base_url=self.live_server_url)
        self.page.navigate()

        self.month_boxes = self.page.month_boxes

    def test_empty_month_box(self):
        first_month_box = self.month_boxes[0]
        self.assertEqual(first_month_box.month_label, "July 2017")
        self.assertFalse(first_month_box.is_occupied)
        self.assertFalse(first_month_box.has_rotation_request)
        self.assertEqual(first_month_box.primary_button_text, "Request a rotation")

        first_month_box.toggle_dropdown()
        self.assertEqual(first_month_box.extra_buttons_text_list, [
            "Request a freeze",
            "See previous requests for this month"
        ])

    def test_empty_month_box_with_rotation_request(self):
        second_month_box = self.month_boxes[1]
        self.assertEqual(second_month_box.month_label, "August 2017")
        self.assertFalse(second_month_box.is_occupied)
        self.assertTrue(second_month_box.has_rotation_request)

        self.assertEqual(second_month_box.requested_specialty, "Internal Medicine")
        self.assertEqual(second_month_box.requested_hospital, "King Abdulaziz Medical City")

        self.assertEqual(second_month_box.primary_button_text, "Get more info")

        second_month_box.toggle_dropdown()
        self.assertEqual(second_month_box.extra_buttons_text_list, [
            "See previous requests for this month"
        ])

    def test_occupied_month_box(self):
        month_box = self.month_boxes[2]
        self.assertEqual(month_box.month_label, "September 2017")
        self.assertTrue(month_box.is_occupied)
        self.assertFalse(month_box.has_rotation_request)

        self.assertEqual(month_box.current_specialty, "Internal Medicine")
        self.assertEqual(month_box.current_hospital, "King Abdulaziz Medical City")

        self.assertEqual(month_box.primary_button_text, "Get more info")

        month_box.toggle_dropdown()
        self.assertEqual(month_box.extra_buttons_text_list, [
            "Request a different rotation",
            "Cancel this rotation",
            "See previous requests for this month",
        ])

    def test_occupied_month_box_with_rotation_request(self):
        month_box = self.month_boxes[3]
        self.assertEqual(month_box.month_label, "October 2017")
        self.assertTrue(month_box.is_occupied)
        self.assertTrue(month_box.has_rotation_request)

        self.assertEqual(month_box.current_specialty, "Pediatrics")
        self.assertEqual(month_box.current_hospital, "King Abdulaziz Medical City")

        self.assertEqual(month_box.requested_specialty, "Pediatrics")
        self.assertEqual(month_box.requested_hospital, "King Fahad Medical City")

        self.assertEqual(month_box.primary_button_text, "Get more info")

        month_box.toggle_dropdown()
        self.assertEqual(month_box.extra_buttons_text_list, [
            "See previous requests for this month",
        ])

    def test_occupied_month_box_with_rotation_cancellation_request(self):
        month_box = self.month_boxes[4]
        self.assertEqual(month_box.month_label, "November 2017")
        self.assertTrue(month_box.is_occupied)
        self.assertTrue(month_box.has_rotation_cancel_request)

        self.assertEqual(month_box.current_specialty, "Pediatrics")
        self.assertEqual(month_box.current_hospital, "King Abdulaziz Medical City")

        self.assertEqual(month_box.rotation_cancel_request_description, "Rotation to be cancelled")

        self.assertEqual(month_box.primary_button_text, "Get more info")

        month_box.toggle_dropdown()
        self.assertEqual(month_box.extra_buttons_text_list, [
            "See previous requests for this month",
        ])

    def test_empty_month_box_with_freeze_request(self):
        month_box = self.month_boxes[5]
        self.assertEqual(month_box.month_label, "December 2017")
        self.assertFalse(month_box.is_occupied)
        self.assertFalse(month_box.has_rotation_request)
        self.assertFalse(month_box.is_frozen)

        self.assertTrue(month_box.has_freeze_request)

        self.assertEqual(month_box.primary_button_text, "Get more info")

        month_box.toggle_dropdown()
        self.assertEqual(month_box.extra_buttons_text_list, [
            "See previous requests for this month",
        ])

    def test_frozen_month_box(self):
        month_box = self.month_boxes[6]
        self.assertEqual(month_box.month_label, "January 2018")
        self.assertFalse(month_box.is_occupied)
        self.assertFalse(month_box.has_rotation_request)
        self.assertTrue(month_box.is_frozen)

        self.assertFalse(month_box.has_freeze_request)

        self.assertEqual(month_box.primary_button_text, "Get more info")

        month_box.toggle_dropdown()
        self.assertEqual(month_box.extra_buttons_text_list, [
            "Cancel this freeze",
            "See previous requests for this month",
        ])

        self.assertFalse(self.month_boxes[12].is_disabled)

    def test_frozen_month_box_with_freeze_cancellation_request(self):
        month_box = self.month_boxes[7]
        self.assertEqual(month_box.month_label, "February 2018")
        self.assertFalse(month_box.is_occupied)
        self.assertFalse(month_box.has_rotation_request)
        self.assertTrue(month_box.is_frozen)

        self.assertFalse(month_box.has_freeze_request)
        self.assertTrue(month_box.has_freeze_cancel_request)

        self.assertEqual(month_box.primary_button_text, "Get more info")

        month_box.toggle_dropdown()
        self.assertEqual(month_box.extra_buttons_text_list, [
            "See previous requests for this month",
        ])

        self.assertFalse(self.month_boxes[13].is_disabled)

    def test_disabled_month_box(self):
        month_box = self.month_boxes[14]
        self.assertFalse(month_box.is_occupied)
        self.assertFalse(month_box.has_rotation_request)
        self.assertFalse(month_box.is_frozen)
        self.assertTrue(month_box.is_disabled)

        self.assertEqual(
            month_box.disabled_month_description,
            "This month will be available when you have an approved freeze."
        )

    def test_occupied_month_box_with_location(self):
        pass  # TODO

    def test_empty_month_box_with_rotation_request_with_location(self):
        pass  # TODO

    def test_occupied_month_box_with_location_and_rotation_request_with_location(self):
        pass  # TODO

    def test_occupied_month_box_that_is_an_elective(self):
        pass  # TODO

    def test_empty_month_box_with_rotation_request_for_an_elective(self):
        pass  # TODO

    def test_occupied_month_box_that_is_an_elective_with_rotation_request_for_an_elective(self):
        pass  # TODO

