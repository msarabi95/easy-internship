from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from month import Month
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from accounts.factories import UserFactory

from functional_tests.intern.page_objects.months import MonthListPage, MonthDetailPage
from functional_tests.po_accounts import SigninPage
from hospitals.factories import LocationFactory
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
        self.internship = self.intern.profile.intern.internship

        self.month = Month(2017, 7)

        # Login
        login_page = SigninPage(self.browser, self.live_server_url)
        login_page.navigate()
        login_page.login(
            self.intern.username,
            "123",
        )

        # Set-up month list page
        self.page = MonthListPage(browser=self.browser, base_url=self.live_server_url)

    def test_empty_month_box(self):
        # Create nothing

        self.page.navigate()
        self.month_boxes = self.page.month_boxes

        month_box = self.month_boxes[0]
        self.assertEqual(month_box.month_label, "July 2017")
        self.assertFalse(month_box.is_occupied)
        self.assertFalse(month_box.has_rotation_request)
        self.assertEqual(month_box.primary_button_text, "Request a rotation")

        month_box.toggle_dropdown()
        self.assertEqual(month_box.extra_buttons_text_list, [
            "Request a freeze",
            "See previous requests for this month"
        ])

    def test_empty_month_box_with_rotation_request(self):
        # Create a rotation request
        RotationRequestFactory(
            internship=self.internship,
            month=self.month,
            specialty__name="Internal Medicine",
            hospital__name="King Abdulaziz Medical City",
        )

        self.page.navigate()
        self.month_boxes = self.page.month_boxes

        month_box = self.month_boxes[0]
        self.assertEqual(month_box.month_label, "July 2017")
        self.assertFalse(month_box.is_occupied)
        self.assertTrue(month_box.has_rotation_request)

        self.assertEqual(month_box.requested_specialty, "Internal Medicine")
        self.assertEqual(month_box.requested_hospital, "King Abdulaziz Medical City")

        self.assertEqual(month_box.primary_button_text, "Get more info")

        month_box.toggle_dropdown()
        self.assertEqual(month_box.extra_buttons_text_list, [
            "See previous requests for this month"
        ])

    def test_empty_month_box_with_rotation_request_with_location(self):
        # Create a rotation request
        RotationRequestFactory(
            internship=self.internship,
            month=self.month,
            specialty__name="Family Medicine",
            hospital__name="King Abdulaziz Medical City",
            location=LocationFactory(name="Employee Health Clinic")
        )

        self.page.navigate()
        self.month_boxes = self.page.month_boxes

        month_box = self.month_boxes[0]
        self.assertEqual(month_box.month_label, "July 2017")
        self.assertFalse(month_box.is_occupied)
        self.assertTrue(month_box.has_rotation_request)

        self.assertEqual(month_box.requested_specialty, "Family Medicine")
        self.assertEqual(month_box.requested_hospital, "King Abdulaziz Medical City")
        self.assertEqual(month_box.requested_location, "(Employee Health Clinic)")

        self.assertEqual(month_box.primary_button_text, "Get more info")

        month_box.toggle_dropdown()
        self.assertEqual(month_box.extra_buttons_text_list, [
            "See previous requests for this month"
        ])

    def test_empty_month_box_with_rotation_request_for_an_elective(self):
        # Create a rotation request
        RotationRequestFactory(
            internship=self.internship,
            month=self.month,
            specialty__name="Internal Medicine",
            hospital__name="King Abdulaziz Medical City",
            is_elective=True,
        )

        self.page.navigate()
        self.month_boxes = self.page.month_boxes

        month_box = self.month_boxes[0]
        self.assertEqual(month_box.month_label, "July 2017")
        self.assertFalse(month_box.is_occupied)
        self.assertTrue(month_box.has_rotation_request)

        self.assertEqual(month_box.requested_specialty, "Internal Medicine")
        self.assertEqual(month_box.requested_hospital, "King Abdulaziz Medical City")
        self.assertTrue(month_box.requested_is_elective)

        self.assertEqual(month_box.primary_button_text, "Get more info")

        month_box.toggle_dropdown()
        self.assertEqual(month_box.extra_buttons_text_list, [
            "See previous requests for this month"
        ])

    def test_occupied_month_box(self):
        # Create a rotation
        RotationFactory(
            internship=self.internship,
            month=self.month,
            specialty__name="Internal Medicine",
            hospital__name="King Abdulaziz Medical City",
            rotation_request__month=self.month,
        )

        self.page.navigate()
        self.month_boxes = self.page.month_boxes

        month_box = self.month_boxes[0]
        self.assertEqual(month_box.month_label, "July 2017")
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

    def test_occupied_month_box_with_location(self):
        # Create a rotation
        RotationFactory(
            internship=self.internship,
            month=self.month,
            specialty__name="Family Medicine",
            hospital__name="King Abdulaziz Medical City",
            location=LocationFactory(name="Employee Health Clinic"),
            rotation_request__month=self.month,
        )

        self.page.navigate()
        self.month_boxes = self.page.month_boxes

        month_box = self.month_boxes[0]
        self.assertEqual(month_box.month_label, "July 2017")
        self.assertTrue(month_box.is_occupied)
        self.assertFalse(month_box.has_rotation_request)

        self.assertEqual(month_box.current_specialty, "Family Medicine")
        self.assertEqual(month_box.current_hospital, "King Abdulaziz Medical City")
        self.assertEqual(month_box.current_location, "(Employee Health Clinic)")

        self.assertEqual(month_box.primary_button_text, "Get more info")

        month_box.toggle_dropdown()
        self.assertEqual(month_box.extra_buttons_text_list, [
            "Request a different rotation",
            "Cancel this rotation",
            "See previous requests for this month",
        ])

    def test_occupied_month_box_that_is_an_elective(self):
        # Create a rotation
        RotationFactory(
            internship=self.internship,
            month=self.month,
            specialty__name="Internal Medicine",
            hospital__name="King Abdulaziz Medical City",
            is_elective=True,
            rotation_request__month=self.month,
        )

        self.page.navigate()
        self.month_boxes = self.page.month_boxes

        month_box = self.month_boxes[0]
        self.assertEqual(month_box.month_label, "July 2017")
        self.assertTrue(month_box.is_occupied)
        self.assertFalse(month_box.has_rotation_request)

        self.assertEqual(month_box.current_specialty, "Internal Medicine")
        self.assertEqual(month_box.current_hospital, "King Abdulaziz Medical City")
        self.assertTrue(month_box.current_is_elective)

        self.assertEqual(month_box.primary_button_text, "Get more info")

        month_box.toggle_dropdown()
        self.assertEqual(month_box.extra_buttons_text_list, [
            "Request a different rotation",
            "Cancel this rotation",
            "See previous requests for this month",
        ])

    def test_occupied_month_box_with_rotation_request(self):
        # Create a rotation request and a rotation for October 2017
        RotationRequestFactory(
            internship=self.internship,
            month=self.month,
            specialty__name="Pediatrics",
            hospital__name="King Fahad Medical City",
        )
        RotationFactory(
            internship=self.internship,
            month=self.month,
            rotation_request__month=self.month,
            specialty__name="Pediatrics",
            hospital__name="King Abdulaziz Medical City",
        )

        self.page.navigate()
        self.month_boxes = self.page.month_boxes

        month_box = self.month_boxes[0]
        self.assertEqual(month_box.month_label, "July 2017")
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

    def test_occupied_month_box_with_location_and_rotation_request_with_location(self):
        # Create a rotation request and a rotation for October 2017
        RotationRequestFactory(
            internship=self.internship,
            month=self.month,
            specialty__name="Family Medicine",
            hospital__name="King Abdulaziz Medical City",
            location=LocationFactory(name="NGCSC"),
        )
        RotationFactory(
            internship=self.internship,
            month=self.month,
            rotation_request__month=self.month,
            specialty__name="Family Medicine",
            hospital__name="King Abdulaziz Medical City",
            location=LocationFactory(name="HCSC"),
        )

        self.page.navigate()
        self.month_boxes = self.page.month_boxes

        month_box = self.month_boxes[0]
        self.assertEqual(month_box.month_label, "July 2017")
        self.assertTrue(month_box.is_occupied)
        self.assertTrue(month_box.has_rotation_request)

        self.assertEqual(month_box.current_specialty, "Family Medicine")
        self.assertEqual(month_box.current_hospital, "King Abdulaziz Medical City")
        self.assertEqual(month_box.current_location, "(HCSC)")

        self.assertEqual(month_box.requested_specialty, "Family Medicine")
        self.assertEqual(month_box.requested_hospital, "King Abdulaziz Medical City")
        self.assertEqual(month_box.requested_location, "(NGCSC)")

        self.assertEqual(month_box.primary_button_text, "Get more info")

        month_box.toggle_dropdown()
        self.assertEqual(month_box.extra_buttons_text_list, [
            "See previous requests for this month",
        ])

    def test_occupied_month_box_that_is_an_elective_with_rotation_request_for_an_elective(self):
        # Create a rotation request and a rotation for October 2017
        RotationRequestFactory(
            internship=self.internship,
            month=self.month,
            specialty__name="Family Medicine",
            hospital__name="King Abdulaziz Medical City",
            is_elective=True,
        )
        RotationFactory(
            internship=self.internship,
            month=self.month,
            rotation_request__month=self.month,
            specialty__name="General Surgery",
            hospital__name="King Abdulaziz Medical City",
            is_elective=True,
        )

        self.page.navigate()
        self.month_boxes = self.page.month_boxes

        month_box = self.month_boxes[0]
        self.assertEqual(month_box.month_label, "July 2017")
        self.assertTrue(month_box.is_occupied)
        self.assertTrue(month_box.has_rotation_request)

        self.assertEqual(month_box.current_specialty, "General Surgery")
        self.assertEqual(month_box.current_hospital, "King Abdulaziz Medical City")
        self.assertTrue(month_box.current_is_elective)

        self.assertEqual(month_box.requested_specialty, "Family Medicine")
        self.assertEqual(month_box.requested_hospital, "King Abdulaziz Medical City")
        self.assertTrue(month_box.requested_is_elective)

        self.assertEqual(month_box.primary_button_text, "Get more info")

        month_box.toggle_dropdown()
        self.assertEqual(month_box.extra_buttons_text_list, [
            "See previous requests for this month",
        ])

    def test_occupied_month_box_with_rotation_cancellation_request(self):
        # Create a rotation and a rotation cancellation request
        RotationFactory(
            internship=self.internship,
            month=self.month,
            rotation_request__month=self.month,
            specialty__name="Pediatrics",
            hospital__name="King Abdulaziz Medical City",
        )
        RotationRequestFactory(
            internship=self.internship,
            month=self.month,
            is_delete=True,
        )

        self.page.navigate()
        self.month_boxes = self.page.month_boxes

        month_box = self.month_boxes[0]
        self.assertEqual(month_box.month_label, "July 2017")
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
        # Create a freeze request
        FreezeRequestFactory(
            intern=self.intern,
            month=self.month,
        )

        self.page.navigate()
        self.month_boxes = self.page.month_boxes

        month_box = self.month_boxes[0]
        self.assertEqual(month_box.month_label, "July 2017")
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
        # Create a freeze for January 2018
        FreezeFactory(
            intern=self.intern,
            month=self.month,
            freeze_request__month=self.month,
        )

        self.page.navigate()
        self.month_boxes = self.page.month_boxes

        month_box = self.month_boxes[0]
        self.assertEqual(month_box.month_label, "July 2017")
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
        self.assertTrue(self.month_boxes[13].is_disabled)
        self.assertTrue(self.month_boxes[14].is_disabled)

    def test_frozen_month_box_with_freeze_cancellation_request(self):
        # Create a freeze with a freeze cancellation request
        FreezeFactory(
            intern=self.intern,
            month=self.month,
            freeze_request__month=self.month,
        )
        FreezeCancelRequestFactory(
            intern=self.intern,
            month=self.month,
        )

        self.page.navigate()
        self.month_boxes = self.page.month_boxes

        month_box = self.month_boxes[0]
        self.assertEqual(month_box.month_label, "July 2017")
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

        self.assertFalse(self.month_boxes[12].is_disabled)
        self.assertTrue(self.month_boxes[13].is_disabled)
        self.assertTrue(self.month_boxes[14].is_disabled)

    def test_disabled_month_box(self):
        self.page.navigate()
        self.month_boxes = self.page.month_boxes

        # Test that the last 3 months are disabled by default
        for idx in range(12, 15):
            month_box = self.month_boxes[idx]
            self.assertFalse(month_box.is_occupied)
            self.assertFalse(month_box.has_rotation_request)
            self.assertFalse(month_box.is_frozen)
            self.assertTrue(month_box.is_disabled)

            self.assertEqual(
                month_box.disabled_month_description,
                "This month will be available when you have an approved freeze."
            )


class InternshipMonthDetailTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(InternshipMonthDetailTests, cls).setUpClass()
        cls.browser = webdriver.Chrome(executable_path="/Users/MSArabi/Downloads/chromedriver")
        cls.browser.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(InternshipMonthDetailTests, cls).tearDownClass()

    def setUp(self):
        # Set up database
        self.intern = UserFactory()

        # By default, internships start at July 2017
        self.internship = self.intern.profile.intern.internship

        self.month = Month(2017, 7)

        # Login
        login_page = SigninPage(self.browser, self.live_server_url)
        login_page.navigate()
        login_page.login(
            self.intern.username,
            "123",
        )

        # Set-up month list page
        self.page = MonthDetailPage(browser=self.browser, base_url=self.live_server_url, month=self.month)

    def test_empty_month(self):
        # Create nothing

        self.page.navigate()

        self.assertEqual(self.page.month_label, "July 2017")
        self.assertFalse(self.page.is_occupied)
        self.assertFalse(self.page.is_frozen)
        self.assertFalse(self.page.has_rotation_request)
        self.assertFalse(self.page.has_rotation_cancel_request)
        self.assertFalse(self.page.has_freeze_request)
        self.assertFalse(self.page.has_freeze_cancel_request)

        self.assertEqual(
            self.page.summary,
            "You don't have any active rotation, freeze, or pending request for this month.",
        )

    def test_empty_month_with_rotation_request(self):
        # Create a rotation request
        request = RotationRequestFactory(
            internship=self.internship,
            month=self.month,
            specialty__name="Internal Medicine",
            hospital__name="King Abdulaziz Medical City",
        )

        self.page.navigate()

        self.assertEqual(self.page.month_label, "July 2017")
        self.assertFalse(self.page.is_occupied)
        self.assertTrue(self.page.has_rotation_request)

        self.assertEqual(self.page.rotation_request_specialty, "Internal Medicine")
        self.assertEqual(self.page.rotation_request_hospital, "King Abdulaziz Medical City")
        self.assertFalse(self.page.rotation_request_is_elective)
        self.assertEqual(
            self.page.rotation_request_submission_datetime,
            request.submission_datetime.strftime("%A, %-d %B %Y, %-I:%M ") + request.submission_datetime.strftime("%p").lower()
        )

    # def test_empty_month_box_with_rotation_request_with_location(self):
    #     # Create a rotation request
    #     RotationRequestFactory(
    #         internship=self.internship,
    #         month=self.month,
    #         specialty__name="Family Medicine",
    #         hospital__name="King Abdulaziz Medical City",
    #         location=LocationFactory(name="Employee Health Clinic")
    #     )
    #
    #     self.page.navigate()
    #     self.month_boxes = self.page.month_boxes
    #
    #     month_box = self.month_boxes[0]
    #     self.assertEqual(month_box.month_label, "July 2017")
    #     self.assertFalse(month_box.is_occupied)
    #     self.assertTrue(month_box.has_rotation_request)
    #
    #     self.assertEqual(month_box.requested_specialty, "Family Medicine")
    #     self.assertEqual(month_box.requested_hospital, "King Abdulaziz Medical City")
    #     self.assertEqual(month_box.requested_location, "(Employee Health Clinic)")
    #
    #     self.assertEqual(month_box.primary_button_text, "Get more info")
    #
    #     month_box.toggle_dropdown()
    #     self.assertEqual(month_box.extra_buttons_text_list, [
    #         "See previous requests for this month"
    #     ])
    #
    # def test_empty_month_box_with_rotation_request_for_an_elective(self):
    #     # Create a rotation request
    #     RotationRequestFactory(
    #         internship=self.internship,
    #         month=self.month,
    #         specialty__name="Internal Medicine",
    #         hospital__name="King Abdulaziz Medical City",
    #         is_elective=True,
    #     )
    #
    #     self.page.navigate()
    #     self.month_boxes = self.page.month_boxes
    #
    #     month_box = self.month_boxes[0]
    #     self.assertEqual(month_box.month_label, "July 2017")
    #     self.assertFalse(month_box.is_occupied)
    #     self.assertTrue(month_box.has_rotation_request)
    #
    #     self.assertEqual(month_box.requested_specialty, "Internal Medicine")
    #     self.assertEqual(month_box.requested_hospital, "King Abdulaziz Medical City")
    #     self.assertTrue(month_box.requested_is_elective)
    #
    #     self.assertEqual(month_box.primary_button_text, "Get more info")
    #
    #     month_box.toggle_dropdown()
    #     self.assertEqual(month_box.extra_buttons_text_list, [
    #         "See previous requests for this month"
    #     ])
    #
    # def test_occupied_month_box(self):
    #     # Create a rotation
    #     RotationFactory(
    #         internship=self.internship,
    #         month=self.month,
    #         specialty__name="Internal Medicine",
    #         hospital__name="King Abdulaziz Medical City",
    #         rotation_request__month=self.month,
    #     )
    #
    #     self.page.navigate()
    #     self.month_boxes = self.page.month_boxes
    #
    #     month_box = self.month_boxes[0]
    #     self.assertEqual(month_box.month_label, "July 2017")
    #     self.assertTrue(month_box.is_occupied)
    #     self.assertFalse(month_box.has_rotation_request)
    #
    #     self.assertEqual(month_box.current_specialty, "Internal Medicine")
    #     self.assertEqual(month_box.current_hospital, "King Abdulaziz Medical City")
    #
    #     self.assertEqual(month_box.primary_button_text, "Get more info")
    #
    #     month_box.toggle_dropdown()
    #     self.assertEqual(month_box.extra_buttons_text_list, [
    #         "Request a different rotation",
    #         "Cancel this rotation",
    #         "See previous requests for this month",
    #     ])
    #
    # def test_occupied_month_box_with_location(self):
    #     # Create a rotation
    #     RotationFactory(
    #         internship=self.internship,
    #         month=self.month,
    #         specialty__name="Family Medicine",
    #         hospital__name="King Abdulaziz Medical City",
    #         location=LocationFactory(name="Employee Health Clinic"),
    #         rotation_request__month=self.month,
    #     )
    #
    #     self.page.navigate()
    #     self.month_boxes = self.page.month_boxes
    #
    #     month_box = self.month_boxes[0]
    #     self.assertEqual(month_box.month_label, "July 2017")
    #     self.assertTrue(month_box.is_occupied)
    #     self.assertFalse(month_box.has_rotation_request)
    #
    #     self.assertEqual(month_box.current_specialty, "Family Medicine")
    #     self.assertEqual(month_box.current_hospital, "King Abdulaziz Medical City")
    #     self.assertEqual(month_box.current_location, "(Employee Health Clinic)")
    #
    #     self.assertEqual(month_box.primary_button_text, "Get more info")
    #
    #     month_box.toggle_dropdown()
    #     self.assertEqual(month_box.extra_buttons_text_list, [
    #         "Request a different rotation",
    #         "Cancel this rotation",
    #         "See previous requests for this month",
    #     ])
    #
    # def test_occupied_month_box_that_is_an_elective(self):
    #     # Create a rotation
    #     RotationFactory(
    #         internship=self.internship,
    #         month=self.month,
    #         specialty__name="Internal Medicine",
    #         hospital__name="King Abdulaziz Medical City",
    #         is_elective=True,
    #         rotation_request__month=self.month,
    #     )
    #
    #     self.page.navigate()
    #     self.month_boxes = self.page.month_boxes
    #
    #     month_box = self.month_boxes[0]
    #     self.assertEqual(month_box.month_label, "July 2017")
    #     self.assertTrue(month_box.is_occupied)
    #     self.assertFalse(month_box.has_rotation_request)
    #
    #     self.assertEqual(month_box.current_specialty, "Internal Medicine")
    #     self.assertEqual(month_box.current_hospital, "King Abdulaziz Medical City")
    #     self.assertTrue(month_box.current_is_elective)
    #
    #     self.assertEqual(month_box.primary_button_text, "Get more info")
    #
    #     month_box.toggle_dropdown()
    #     self.assertEqual(month_box.extra_buttons_text_list, [
    #         "Request a different rotation",
    #         "Cancel this rotation",
    #         "See previous requests for this month",
    #     ])
    #
    # def test_occupied_month_box_with_rotation_request(self):
    #     # Create a rotation request and a rotation for October 2017
    #     RotationRequestFactory(
    #         internship=self.internship,
    #         month=self.month,
    #         specialty__name="Pediatrics",
    #         hospital__name="King Fahad Medical City",
    #     )
    #     RotationFactory(
    #         internship=self.internship,
    #         month=self.month,
    #         rotation_request__month=self.month,
    #         specialty__name="Pediatrics",
    #         hospital__name="King Abdulaziz Medical City",
    #     )
    #
    #     self.page.navigate()
    #     self.month_boxes = self.page.month_boxes
    #
    #     month_box = self.month_boxes[0]
    #     self.assertEqual(month_box.month_label, "July 2017")
    #     self.assertTrue(month_box.is_occupied)
    #     self.assertTrue(month_box.has_rotation_request)
    #
    #     self.assertEqual(month_box.current_specialty, "Pediatrics")
    #     self.assertEqual(month_box.current_hospital, "King Abdulaziz Medical City")
    #
    #     self.assertEqual(month_box.requested_specialty, "Pediatrics")
    #     self.assertEqual(month_box.requested_hospital, "King Fahad Medical City")
    #
    #     self.assertEqual(month_box.primary_button_text, "Get more info")
    #
    #     month_box.toggle_dropdown()
    #     self.assertEqual(month_box.extra_buttons_text_list, [
    #         "See previous requests for this month",
    #     ])
    #
    # def test_occupied_month_box_with_location_and_rotation_request_with_location(self):
    #     # Create a rotation request and a rotation for October 2017
    #     RotationRequestFactory(
    #         internship=self.internship,
    #         month=self.month,
    #         specialty__name="Family Medicine",
    #         hospital__name="King Abdulaziz Medical City",
    #         location=LocationFactory(name="NGCSC"),
    #     )
    #     RotationFactory(
    #         internship=self.internship,
    #         month=self.month,
    #         rotation_request__month=self.month,
    #         specialty__name="Family Medicine",
    #         hospital__name="King Abdulaziz Medical City",
    #         location=LocationFactory(name="HCSC"),
    #     )
    #
    #     self.page.navigate()
    #     self.month_boxes = self.page.month_boxes
    #
    #     month_box = self.month_boxes[0]
    #     self.assertEqual(month_box.month_label, "July 2017")
    #     self.assertTrue(month_box.is_occupied)
    #     self.assertTrue(month_box.has_rotation_request)
    #
    #     self.assertEqual(month_box.current_specialty, "Family Medicine")
    #     self.assertEqual(month_box.current_hospital, "King Abdulaziz Medical City")
    #     self.assertEqual(month_box.current_location, "(HCSC)")
    #
    #     self.assertEqual(month_box.requested_specialty, "Family Medicine")
    #     self.assertEqual(month_box.requested_hospital, "King Abdulaziz Medical City")
    #     self.assertEqual(month_box.requested_location, "(NGCSC)")
    #
    #     self.assertEqual(month_box.primary_button_text, "Get more info")
    #
    #     month_box.toggle_dropdown()
    #     self.assertEqual(month_box.extra_buttons_text_list, [
    #         "See previous requests for this month",
    #     ])
    #
    # def test_occupied_month_box_that_is_an_elective_with_rotation_request_for_an_elective(self):
    #     # Create a rotation request and a rotation for October 2017
    #     RotationRequestFactory(
    #         internship=self.internship,
    #         month=self.month,
    #         specialty__name="Family Medicine",
    #         hospital__name="King Abdulaziz Medical City",
    #         is_elective=True,
    #     )
    #     RotationFactory(
    #         internship=self.internship,
    #         month=self.month,
    #         rotation_request__month=self.month,
    #         specialty__name="General Surgery",
    #         hospital__name="King Abdulaziz Medical City",
    #         is_elective=True,
    #     )
    #
    #     self.page.navigate()
    #     self.month_boxes = self.page.month_boxes
    #
    #     month_box = self.month_boxes[0]
    #     self.assertEqual(month_box.month_label, "July 2017")
    #     self.assertTrue(month_box.is_occupied)
    #     self.assertTrue(month_box.has_rotation_request)
    #
    #     self.assertEqual(month_box.current_specialty, "General Surgery")
    #     self.assertEqual(month_box.current_hospital, "King Abdulaziz Medical City")
    #     self.assertTrue(month_box.current_is_elective)
    #
    #     self.assertEqual(month_box.requested_specialty, "Family Medicine")
    #     self.assertEqual(month_box.requested_hospital, "King Abdulaziz Medical City")
    #     self.assertTrue(month_box.requested_is_elective)
    #
    #     self.assertEqual(month_box.primary_button_text, "Get more info")
    #
    #     month_box.toggle_dropdown()
    #     self.assertEqual(month_box.extra_buttons_text_list, [
    #         "See previous requests for this month",
    #     ])
    #
    # def test_occupied_month_box_with_rotation_cancellation_request(self):
    #     # Create a rotation and a rotation cancellation request
    #     RotationFactory(
    #         internship=self.internship,
    #         month=self.month,
    #         rotation_request__month=self.month,
    #         specialty__name="Pediatrics",
    #         hospital__name="King Abdulaziz Medical City",
    #     )
    #     RotationRequestFactory(
    #         internship=self.internship,
    #         month=self.month,
    #         is_delete=True,
    #     )
    #
    #     self.page.navigate()
    #     self.month_boxes = self.page.month_boxes
    #
    #     month_box = self.month_boxes[0]
    #     self.assertEqual(month_box.month_label, "July 2017")
    #     self.assertTrue(month_box.is_occupied)
    #     self.assertTrue(month_box.has_rotation_cancel_request)
    #
    #     self.assertEqual(month_box.current_specialty, "Pediatrics")
    #     self.assertEqual(month_box.current_hospital, "King Abdulaziz Medical City")
    #
    #     self.assertEqual(month_box.rotation_cancel_request_description, "Rotation to be cancelled")
    #
    #     self.assertEqual(month_box.primary_button_text, "Get more info")
    #
    #     month_box.toggle_dropdown()
    #     self.assertEqual(month_box.extra_buttons_text_list, [
    #         "See previous requests for this month",
    #     ])
    #
    # def test_empty_month_box_with_freeze_request(self):
    #     # Create a freeze request
    #     FreezeRequestFactory(
    #         intern=self.intern,
    #         month=self.month,
    #     )
    #
    #     self.page.navigate()
    #     self.month_boxes = self.page.month_boxes
    #
    #     month_box = self.month_boxes[0]
    #     self.assertEqual(month_box.month_label, "July 2017")
    #     self.assertFalse(month_box.is_occupied)
    #     self.assertFalse(month_box.has_rotation_request)
    #     self.assertFalse(month_box.is_frozen)
    #
    #     self.assertTrue(month_box.has_freeze_request)
    #
    #     self.assertEqual(month_box.primary_button_text, "Get more info")
    #
    #     month_box.toggle_dropdown()
    #     self.assertEqual(month_box.extra_buttons_text_list, [
    #         "See previous requests for this month",
    #     ])
    #
    # def test_frozen_month_box(self):
    #     # Create a freeze for January 2018
    #     FreezeFactory(
    #         intern=self.intern,
    #         month=self.month,
    #         freeze_request__month=self.month,
    #     )
    #
    #     self.page.navigate()
    #     self.month_boxes = self.page.month_boxes
    #
    #     month_box = self.month_boxes[0]
    #     self.assertEqual(month_box.month_label, "July 2017")
    #     self.assertFalse(month_box.is_occupied)
    #     self.assertFalse(month_box.has_rotation_request)
    #     self.assertTrue(month_box.is_frozen)
    #
    #     self.assertFalse(month_box.has_freeze_request)
    #
    #     self.assertEqual(month_box.primary_button_text, "Get more info")
    #
    #     month_box.toggle_dropdown()
    #     self.assertEqual(month_box.extra_buttons_text_list, [
    #         "Cancel this freeze",
    #         "See previous requests for this month",
    #     ])
    #
    #     self.assertFalse(self.month_boxes[12].is_disabled)
    #     self.assertTrue(self.month_boxes[13].is_disabled)
    #     self.assertTrue(self.month_boxes[14].is_disabled)
    #
    # def test_frozen_month_box_with_freeze_cancellation_request(self):
    #     # Create a freeze with a freeze cancellation request
    #     FreezeFactory(
    #         intern=self.intern,
    #         month=self.month,
    #         freeze_request__month=self.month,
    #     )
    #     FreezeCancelRequestFactory(
    #         intern=self.intern,
    #         month=self.month,
    #     )
    #
    #     self.page.navigate()
    #     self.month_boxes = self.page.month_boxes
    #
    #     month_box = self.month_boxes[0]
    #     self.assertEqual(month_box.month_label, "July 2017")
    #     self.assertFalse(month_box.is_occupied)
    #     self.assertFalse(month_box.has_rotation_request)
    #     self.assertTrue(month_box.is_frozen)
    #
    #     self.assertFalse(month_box.has_freeze_request)
    #     self.assertTrue(month_box.has_freeze_cancel_request)
    #
    #     self.assertEqual(month_box.primary_button_text, "Get more info")
    #
    #     month_box.toggle_dropdown()
    #     self.assertEqual(month_box.extra_buttons_text_list, [
    #         "See previous requests for this month",
    #     ])
    #
    #     self.assertFalse(self.month_boxes[12].is_disabled)
    #     self.assertTrue(self.month_boxes[13].is_disabled)
    #     self.assertTrue(self.month_boxes[14].is_disabled)
    #
    # def test_disabled_month_box(self):
    #     self.page.navigate()
    #     self.month_boxes = self.page.month_boxes
    #
    #     # Test that the last 3 months are disabled by default
    #     for idx in range(12, 15):
    #         month_box = self.month_boxes[idx]
    #         self.assertFalse(month_box.is_occupied)
    #         self.assertFalse(month_box.has_rotation_request)
    #         self.assertFalse(month_box.is_frozen)
    #         self.assertTrue(month_box.is_disabled)
    #
    #         self.assertEqual(
    #             month_box.disabled_month_description,
    #             "This month will be available when you have an approved freeze."
    #         )
