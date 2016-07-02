from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from month import Month
from planner.test_factories import UserFactory, ProfileFactory, InternFactory, InternshipFactory, RotationFactory, \
    RotationRequestFactory
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class SeleniumTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(SeleniumTestCase, cls).setUpClass()
        cls.browser = webdriver.Firefox()

    def setUp(self):
        self.internship1 = InternshipFactory()

        self.user1 = self.internship1.intern.profile.user

        self.user1.is_staff = True
        # self.user1.is_active = True
        self.user1.set_password("12345678")
        self.user1.save()

        self.browser.get(self.live_server_url + '/admin/')
        self.browser.find_element_by_css_selector("[name=username]").send_keys(self.user1.get_username())
        self.browser.find_element_by_css_selector("[name=password]").send_keys("12345678")
        self.browser.find_element_by_css_selector("[type=submit]").click()

        self.browser.get(self.live_server_url)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(SeleniumTestCase, cls).tearDownClass()

    def test_box_appearance(self):

        # Prepare 5 states
        # (1) Unoccupied month
        #     <-- Nothing. Will use 2016, 8 as testing month. -->

        # (2) Occupied month
        r2 = RotationFactory(internship=self.internship1, month=Month(2016, 9))

        # (3) Requested Unoccupied month
        rr3 = RotationRequestFactory(plan_request__internship=self.internship1, month=Month(2016, 11))
        pr = rr3.plan_request

        # (4.a) Requested Occupied month (update request)
        r4a = RotationFactory(internship=self.internship1, month=Month(2016, 12))
        rr4a = RotationRequestFactory(plan_request=pr, month=Month(2016, 12))

        # (4.b) Requested Occupied month (cancellation request)
        r4b = RotationFactory(internship=self.internship1, month=Month(2017, 2))
        rr4b = RotationRequestFactory(plan_request=pr, month=Month(2017, 2), delete=True)

        self.browser.get("%s%s" % (self.live_server_url, "/#/planner/"))
        self.browser.implicitly_wait(0.5)

        months = self.browser.find_elements_by_css_selector(".internship-month")

        # Test 5 states
        # ####################
        # (1) Unoccupied month
        # ####################
        month1 = months[1]  # August 2016
        self.assertIn("box-default", month1.get_attribute("class"))
        self.assertIn("btn-default", month1.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn("No current rotation.", month1.text)

        # ##################
        # (2) Occupied month
        # ##################
        month2 = months[2]  # September 2016
        self.assertIn("box-primary", month2.get_attribute("class"))
        self.assertIn("btn-primary", month2.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn(r2.department.hospital.name, month2.text)
        self.assertIn(r2.department.name, month2.text)

        # ##############################
        # (3) Requested Unoccupied month
        # ##############################
        month3 = months[4]  # November 2016
        self.assertIn("box-default", month3.get_attribute("class"))
        self.assertIn("btn-default", month3.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn("No current rotation.", month3.text)

        try:
            req_btn = month3.find_element_by_tag_name("a")
        except NoSuchElementException:
            raise AssertionError("Show requested rotation button not found.")

        self.assertIn("Show Requested", req_btn.text)
        self.assertIn("bg-yellow", req_btn.find_element_by_tag_name("span").get_attribute("class"))

        # Click the `Show Requested` button
        req_btn.click()
        self.assertIn("box-warning", month3.get_attribute("class"))
        self.assertIn("btn-warning", month3.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn(rr3.requested_department.get_department().hospital.name, month3.text)
        self.assertIn(rr3.requested_department.get_department().name, month3.text)

        try:
            current_btn = month3.find_element_by_tag_name("a")
        except NoSuchElementException:
            raise AssertionError("Show current rotation button not found.")

        self.assertIn("Show Current", current_btn.text)
        self.assertIn("bg-gray", current_btn.find_element_by_tag_name("span").get_attribute("class"))

        # Click the `Show Current` button to return to original view
        current_btn.click()
        self.assertIn("box-default", month3.get_attribute("class"))
        self.assertIn("btn-default", month3.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn("No current rotation.", month3.text)

        # ###############################################
        # (4.a) Requested Occupied month (update request)
        # ###############################################
        month4a = months[5]  # December 2016
        self.assertIn("box-primary", month4a.get_attribute("class"))
        self.assertIn("btn-primary", month4a.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn(r4a.department.hospital.name, month4a.text)
        self.assertIn(r4a.department.name, month4a.text)

        try:
            req_btn = month4a.find_element_by_tag_name("a")
        except NoSuchElementException:
            raise AssertionError("Show requested rotation button not found.")

        self.assertIn("Show Requested", req_btn.text)
        self.assertIn("bg-yellow", req_btn.find_element_by_tag_name("span").get_attribute("class"))

        # Click the `Show Requested` button
        req_btn.click()
        self.assertIn("box-warning", month4a.get_attribute("class"))
        self.assertIn("btn-warning", month4a.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn(rr4a.requested_department.get_department().hospital.name, month4a.text)
        self.assertIn(rr4a.requested_department.get_department().name, month4a.text)

        try:
            current_btn = month4a.find_element_by_tag_name("a")
        except NoSuchElementException:
            raise AssertionError("Show current rotation button not found.")

        self.assertIn("Show Current", current_btn.text)
        self.assertIn("bg-blue", current_btn.find_element_by_tag_name("span").get_attribute("class"))

        # Click the `Show Current` button to return to original view
        current_btn.click()
        self.assertIn("box-primary", month4a.get_attribute("class"))
        self.assertIn("btn-primary", month4a.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn(r4a.department.hospital.name, month4a.text)
        self.assertIn(r4a.department.name, month4a.text)

        # #####################################################
        # (4.b) Requested Occupied month (cancellation request)
        # #####################################################
        month4b = months[7]  # February 2017
        self.assertIn("box-primary", month4b.get_attribute("class"))
        self.assertIn("btn-primary", month4b.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn(r4b.department.hospital.name, month4b.text)
        self.assertIn(r4b.department.name, month4b.text)

        try:
            req_btn = month4b.find_element_by_tag_name("a")
        except NoSuchElementException:
            raise AssertionError("Show requested rotation button not found.")

        self.assertIn("Show Requested", req_btn.text)
        self.assertIn("bg-yellow", req_btn.find_element_by_tag_name("span").get_attribute("class"))

        # Click the `Show Requested` button
        req_btn.click()
        self.assertIn("box-danger", month4b.get_attribute("class"))
        self.assertIn("btn-danger", month4b.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn("You have requested cancellation of this rotation.", month4b.text)

        try:
            current_btn = month4b.find_element_by_tag_name("a")
        except NoSuchElementException:
            raise AssertionError("Show current rotation button not found.")

        self.assertIn("Show Current", current_btn.text)
        self.assertIn("bg-blue", current_btn.find_element_by_tag_name("span").get_attribute("class"))

        # Click the `Show Current` button to return to original view
        current_btn.click()
        self.assertIn("box-primary", month4b.get_attribute("class"))
        self.assertIn("btn-primary", month4b.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn(r4b.department.hospital.name, month4b.text)
        self.assertIn(r4b.department.name, month4b.text)
