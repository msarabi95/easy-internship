from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from month import Month
from planner.test_factories import UserFactory, ProfileFactory, InternFactory, InternshipFactory, RotationFactory, \
    RotationRequestFactory
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


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

        # Prepare 5 states
        # (1) Unoccupied month
        #     <-- Nothing. Will use 2016, 8 as testing month. -->

        # (2) Occupied month
        self.r2 = RotationFactory(internship=self.internship1, month=Month(2016, 9))

        # (3) Requested Unoccupied month
        self.rr3 = RotationRequestFactory(plan_request__internship=self.internship1, month=Month(2016, 11))
        self.pr = self.rr3.plan_request

        # (4.a) Requested Occupied month (update request)
        self.r4a = RotationFactory(internship=self.internship1, month=Month(2016, 12))
        self.rr4a = RotationRequestFactory(plan_request=self.pr, month=Month(2016, 12))

        # (4.b) Requested Occupied month (cancellation request)
        self.r4b = RotationFactory(internship=self.internship1, month=Month(2017, 2))
        self.rr4b = RotationRequestFactory(plan_request=self.pr, month=Month(2017, 2), delete=True)

        # Login test user

        self.browser.get(self.live_server_url + '/admin/')
        self.browser.find_element_by_css_selector("[name=username]").send_keys(self.user1.get_username())
        self.browser.find_element_by_css_selector("[name=password]").send_keys("12345678")
        self.browser.find_element_by_css_selector("[type=submit]").click()

        # Navigate to home page

        self.browser.get(self.live_server_url)

        # Navigate to planner page

        self.browser.get("%s%s" % (self.live_server_url, "/#/planner/"))
        self.browser.implicitly_wait(0.5)

        self.months = self.browser.find_elements_by_css_selector(".internship-month")

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(SeleniumTestCase, cls).tearDownClass()

    def assertElementPresent(self, value, by=None, container=None):
        if container is None:
            container = self.browser

        if by is None:
            by = By.CSS_SELECTOR

        try:
            container.find_element(by, value)
        except NoSuchElementException:
            raise AssertionError("Element is not present.")  # FIXME: a more useful message

    def test_box_appearance(self):
        # Test 5 states
        # ####################
        # (1) Unoccupied month
        # ####################
        month1 = self.months[1]  # August 2016
        self.assertIn("box-default", month1.get_attribute("class"))
        self.assertIn("btn-default", month1.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn("No current rotation.", month1.text)

        # ##################
        # (2) Occupied month
        # ##################
        month2 = self.months[2]  # September 2016
        self.assertIn("box-primary", month2.get_attribute("class"))
        self.assertIn("btn-primary", month2.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn(self.r2.department.hospital.name, month2.text)
        self.assertIn(self.r2.department.name, month2.text)

        # ##############################
        # (3) Requested Unoccupied month
        # ##############################
        month3 = self.months[4]  # November 2016
        self.assertIn("box-default", month3.get_attribute("class"))
        self.assertIn("btn-default", month3.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn("No current rotation.", month3.text)

        self.assertElementPresent("a", container=month3)
        req_btn = month3.find_element_by_css_selector("a")

        self.assertIn("Show Requested", req_btn.text)
        self.assertIn("bg-yellow", req_btn.find_element_by_tag_name("span").get_attribute("class"))

        # Click the `Show Requested` button
        req_btn.click()
        self.assertIn("box-warning", month3.get_attribute("class"))
        self.assertIn("btn-warning", month3.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn(self.rr3.requested_department.get_department().hospital.name, month3.text)
        self.assertIn(self.rr3.requested_department.get_department().name, month3.text)

        self.assertElementPresent("a", container=month3)
        current_btn = month3.find_element_by_css_selector("a")

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
        month4a = self.months[5]  # December 2016
        self.assertIn("box-primary", month4a.get_attribute("class"))
        self.assertIn("btn-primary", month4a.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn(self.r4a.department.hospital.name, month4a.text)
        self.assertIn(self.r4a.department.name, month4a.text)

        self.assertElementPresent("a", container=month4a)
        req_btn = month4a.find_element_by_css_selector("a")

        self.assertIn("Show Requested", req_btn.text)
        self.assertIn("bg-yellow", req_btn.find_element_by_tag_name("span").get_attribute("class"))

        # Click the `Show Requested` button
        req_btn.click()
        self.assertIn("box-warning", month4a.get_attribute("class"))
        self.assertIn("btn-warning", month4a.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn(self.rr4a.requested_department.get_department().hospital.name, month4a.text)
        self.assertIn(self.rr4a.requested_department.get_department().name, month4a.text)

        self.assertElementPresent("a", container=month4a)
        current_btn = month4a.find_element_by_css_selector("a")

        self.assertIn("Show Current", current_btn.text)
        self.assertIn("bg-blue", current_btn.find_element_by_tag_name("span").get_attribute("class"))

        # Click the `Show Current` button to return to original view
        current_btn.click()
        self.assertIn("box-primary", month4a.get_attribute("class"))
        self.assertIn("btn-primary", month4a.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn(self.r4a.department.hospital.name, month4a.text)
        self.assertIn(self.r4a.department.name, month4a.text)

        # #####################################################
        # (4.b) Requested Occupied month (cancellation request)
        # #####################################################
        month4b = self.months[7]  # February 2017
        self.assertIn("box-primary", month4b.get_attribute("class"))
        self.assertIn("btn-primary", month4b.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn(self.r4b.department.hospital.name, month4b.text)
        self.assertIn(self.r4b.department.name, month4b.text)

        self.assertElementPresent("a", container=month4b)
        req_btn = month4b.find_element_by_css_selector("a")

        self.assertIn("Show Requested", req_btn.text)
        self.assertIn("bg-yellow", req_btn.find_element_by_tag_name("span").get_attribute("class"))

        # Click the `Show Requested` button
        req_btn.click()
        self.assertIn("box-danger", month4b.get_attribute("class"))
        self.assertIn("btn-danger", month4b.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn("You have requested cancellation of this rotation.", month4b.text)

        self.assertElementPresent("a", container=month4b)
        current_btn = month4b.find_element_by_css_selector("a")

        self.assertIn("Show Current", current_btn.text)
        self.assertIn("bg-blue", current_btn.find_element_by_tag_name("span").get_attribute("class"))

        # Click the `Show Current` button to return to original view
        current_btn.click()
        self.assertIn("box-primary", month4b.get_attribute("class"))
        self.assertIn("btn-primary", month4b.find_element_by_tag_name("button").get_attribute("class"))
        self.assertIn(self.r4b.department.hospital.name, month4b.text)
        self.assertIn(self.r4b.department.name, month4b.text)

    def test_modal_appearance(self):
        # Test 5 states
        # ####################
        # (1) Unoccupied month
        # ####################
        month1 = self.months[1]  # August 2016

        modal_btn = month1.find_element_by_css_selector("button")
        modal_btn.click()

        self.assertElementPresent(".modal-dialog")
        modal = self.browser.find_element_by_css_selector(".modal-dialog")

        self.assertElementPresent(".nav", container=modal)
        nav = modal.find_element_by_css_selector(".nav")

        self.assertIn("Request a Rotation", nav.text)
        self.assertIn("Request History", nav.text)
        self.assertEqual(len(nav.find_elements_by_css_selector("li")), 2)

        tab_content = modal.find_element_by_css_selector(".tab-content")
        self.assertElementPresent("form", container=tab_content)

        request_history_tab = modal.find_element_by_css_selector("[index=\"'request-history'\"]")
        request_history_tab.click()

        self.assertIn("No request history for this month.", tab_content.text)

        modal.find_element_by_css_selector("[data-dismiss='modal']").click()

        # #####################################################
        # Special Case: Unoccupied with Previous Delete Request
        # #####################################################

        # TODO: Test appearance of request history

        # ##################
        # (2) Occupied month
        # ##################
        month2 = self.months[2]  # September 2016

        modal_btn = month2.find_element_by_css_selector("button")
        modal_btn.click()

        self.assertElementPresent(".modal-dialog")
        modal = self.browser.find_element_by_css_selector(".modal-dialog")

        self.assertElementPresent(".nav", container=modal)
        nav = modal.find_element_by_css_selector(".nav")

        self.assertIn("Current Rotation", nav.text)
        self.assertIn("Request a Change", nav.text)
        self.assertIn("Request History", nav.text)
        self.assertEqual(len(nav.find_elements_by_css_selector("li")), 3)

        tab_content = modal.find_element_by_css_selector(".tab-content")

        self.assertIn(self.r2.specialty.name, tab_content.text)
        self.assertIn(self.r2.department.hospital.name, tab_content.text)
        self.assertIn(self.r2.department.name, tab_content.text)

        if self.r2.specialty.is_subspecialty():
            self.assertIn(self.r2.specialty.get_general_specialty().name, tab_content.text)
            self.assertIn(self.r2.department.parent_department.name, tab_content.text)

        # TODO: Assert presence of request and review dates

        rotation_request_tab = modal.find_element_by_css_selector("[index=\"'rotation-request'\"]")
        rotation_request_tab.click()

        self.assertElementPresent("form", container=tab_content)

        request_history_tab = modal.find_element_by_css_selector("[index=\"'request-history'\"]")
        request_history_tab.click()

        self.assertElementPresent(".timeline", container=tab_content)
        timeline = tab_content.find_element_by_css_selector(".timeline")

        self.assertEqual(len(timeline.find_elements_by_css_selector("li")), 1)

        history_entry1 = timeline.find_elements_by_css_selector("li")[0]
        self.assertIn(self.r2.department.name, history_entry1.text)  # FIXME: should be based on a RotationRequest
        self.assertElementPresent(".fa .fa-check .bg-green", container=history_entry1)

        # TODO: Assert presence of request and review date tooltips + request date

        modal.find_element_by_css_selector("[data-dismiss='modal']").click()

        # ##############################
        # (3) Requested Unoccupied month
        # ##############################
        month3 = self.months[4]  # November 2016

        modal_btn = month3.find_element_by_css_selector("button")
        modal_btn.click()

        self.assertElementPresent(".modal-dialog")
        modal = self.browser.find_element_by_css_selector(".modal-dialog")

        self.assertElementPresent(".nav", container=modal)
        nav = modal.find_element_by_css_selector(".nav")

        self.assertIn("Current Request", nav.text)
        self.assertIn("Request History", nav.text)
        self.assertEqual(len(nav.find_elements_by_css_selector("li")), 2)

        tab_content = modal.find_element_by_css_selector(".tab-content")

        self.assertIn(self.rr3.specialty.name, tab_content.text)
        self.assertIn(self.rr3.department.hospital.name, tab_content.text)
        self.assertIn(self.rr3.department.name, tab_content.text)
        # self.assertIn(self.rr3.plan_request.submission_datetime.strftime("%d %B %Y"), tab_content.text)
        # FIXME: Testing datetime should only be done on a submitted plan request! (Otherwise no date will be there.)

        if self.rr3.specialty.is_subspecialty():
            self.assertIn(self.rr3.specialty.get_general_specialty().name, tab_content.text)
            self.assertIn(self.rr3.department.parent_department.name, tab_content.text)

        # TODO: Test clicking "Update Request" button. It should show request edit form.

        request_history_tab = modal.find_element_by_css_selector("[index=\"'request-history'\"]")
        request_history_tab.click()

        self.assertElementPresent(".timeline", container=tab_content)
        timeline = tab_content.find_element_by_css_selector(".timeline")

        self.assertEqual(len(timeline.find_elements_by_css_selector("li")), 1)

        history_entry1 = timeline.find_elements_by_css_selector("li")[0]
        self.assertIn(self.rr3.requested_department.get_department().name, history_entry1.text)
        self.assertElementPresent(".fa .fa-clock-o .bg-yellow", container=history_entry1)

        self.assertElementPresent("[title='Pending']", container=history_entry1)
        self.assertElementPresent("[title='Requested %s']" % self.rr3.plan_request.submission_datetime \
                                  .strftime("%d %B %Y"), container=history_entry1)

        modal.find_element_by_css_selector("[data-dismiss='modal']").click()

        # ###############################################
        # (4.a) Requested Occupied month (update request)
        # ###############################################
        month4a = self.months[5]  # December 2016

        modal_btn = month4a.find_element_by_css_selector("button")
        modal_btn.click()

        self.assertElementPresent(".modal-dialog")
        modal = self.browser.find_element_by_css_selector(".modal-dialog")

        self.assertElementPresent(".nav", container=modal)
        nav = modal.find_element_by_css_selector(".nav")

        self.assertIn("Current Rotation", nav.text)
        self.assertIn("Current Request", nav.text)
        self.assertIn("Request History", nav.text)
        self.assertEqual(len(nav.find_elements_by_css_selector("li")), 3)

        tab_content = modal.find_element_by_css_selector(".tab-content")

        self.assertIn(self.r4a.specialty.name, tab_content.text)
        self.assertIn(self.r4a.department.hospital.name, tab_content.text)
        self.assertIn(self.r4a.department.name, tab_content.text)

        if self.r4a.specialty.is_subspecialty():
            self.assertIn(self.r4a.specialty.get_general_specialty().name, tab_content.text)
            self.assertIn(self.r4a.department.parent_department.name, tab_content.text)

        # TODO: Assert presence of request and review dates

        rotation_request_tab = modal.find_element_by_css_selector("[index=\"'rotation-request'\"]")
        rotation_request_tab.click()

        self.assertIn(self.rr4a.specialty.name, tab_content.text)
        self.assertIn(self.rr4a.department.hospital.name, tab_content.text)
        self.assertIn(self.rr4a.department.name, tab_content.text)
        # self.assertIn(self.rr4a.plan_request.submission_datetime.strftime("%d %B %Y"), tab_content.text)
        # FIXME: Testing datetime should only be done on a submitted plan request! (Otherwise no date will be there.)

        if self.rr4a.specialty.is_subspecialty():
            self.assertIn(self.rr4a.specialty.get_general_specialty().name, tab_content.text)
            self.assertIn(self.rr4a.department.parent_department.name, tab_content.text)

        # TODO: Test clicking "Update Request" button. It should show request edit form.
        # self.assertElementPresent("form", container=tab_content)

        request_history_tab = modal.find_element_by_css_selector("[index=\"'request-history'\"]")
        request_history_tab.click()

        self.assertElementPresent(".timeline", container=tab_content)
        timeline = tab_content.find_element_by_css_selector(".timeline")

        self.assertEqual(len(timeline.find_elements_by_css_selector("li")), 2)

        history_entry1 = timeline.find_elements_by_css_selector("li")[0]
        self.assertIn(self.rr4a.requested_department.get_department().name, history_entry1.text)
        self.assertElementPresent(".fa .fa-clock-o .bg-yellow", container=history_entry1)

        # TODO: Assert presence of request and review date tooltips + request date

        history_entry2 = timeline.find_elements_by_css_selector("li")[1]
        self.assertIn(self.r4a.department.name, history_entry2.text)
        self.assertElementPresent(".fa .fa-check .bg-green", container=history_entry2)

        # TODO: Assert presence of request and review date tooltips + request date

        modal.find_element_by_css_selector("[data-dismiss='modal']").click()

        # #####################################################
        # (4.b) Requested Occupied month (cancellation request)
        # #####################################################
        month4b = self.months[7]  # February 2017

        modal_btn = month4b.find_element_by_css_selector("button")
        modal_btn.click()

        self.assertElementPresent(".modal-dialog")
        modal = self.browser.find_element_by_css_selector(".modal-dialog")

        self.assertElementPresent(".nav", container=modal)
        nav = modal.find_element_by_css_selector(".nav")

        self.assertIn("Current Rotation", nav.text)
        self.assertIn("Current Request", nav.text)
        self.assertIn("Request History", nav.text)
        self.assertEqual(len(nav.find_elements_by_css_selector("li")), 3)

        tab_content = modal.find_element_by_css_selector(".tab-content")

        self.assertIn(self.r4b.specialty.name, tab_content.text)
        self.assertIn(self.r4b.department.hospital.name, tab_content.text)
        self.assertIn(self.r4b.department.name, tab_content.text)

        if self.r4b.specialty.is_subspecialty():  # FIXME: r4b specialty isn't a subspecialty; this will never be True
            self.assertIn(self.r4b.specialty.get_general_specialty().name, tab_content.text)
            self.assertIn(self.r4b.department.parent_department.name, tab_content.text)

        # TODO: Assert presence of request and review dates

        rotation_request_tab = modal.find_element_by_css_selector("[index=\"'rotation-request'\"]")
        rotation_request_tab.click()

        self.assertIn("You have requested cancellation of this rotation.", tab_content.text)
        # self.assertIn(self.rr4b.plan_request.submission_datetime.strftime("%d %B %Y"), tab_content.text)
        # FIXME: Testing datetime should only be done on a submitted plan request! (Otherwise no date will be there.)

        # TODO: Test clicking "Update Request" button. It should show request edit form.
        # self.assertElementPresent("form", container=tab_content)

        request_history_tab = modal.find_element_by_css_selector("[index=\"'request-history'\"]")
        request_history_tab.click()

        self.assertElementPresent(".timeline", container=tab_content)
        timeline = tab_content.find_element_by_css_selector(".timeline")

        self.assertEqual(len(timeline.find_elements_by_css_selector("li")), 2)

        history_entry1 = timeline.find_elements_by_css_selector("li")[0]
        self.assertIn("Cancel Rotation", history_entry1.text)
        self.assertElementPresent(".fa .fa-clock-o .bg-yellow", container=history_entry1)

        # TODO: Assert presence of request and review date tooltips + request date

        history_entry2 = timeline.find_elements_by_css_selector("li")[1]
        self.assertIn(self.r4b.department.name, history_entry2.text)
        self.assertElementPresent(".fa .fa-check .bg-green", container=history_entry2)

        # TODO: Assert presence of request and review date tooltips + request date

        modal.find_element_by_css_selector("[data-dismiss='modal']").click()
