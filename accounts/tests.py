# coding=utf-8
import os

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class SignupFormTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(SignupFormTests, cls).setUpClass()
        cls.browser = webdriver.Firefox()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(SignupFormTests, cls).tearDownClass()

    def setUp(self):
        self.username = "abcdefghijklmn"

        self.browser.get("%s%s" % (self.live_server_url, reverse("userena_signup")))

        self.browser.find_element_by_css_selector("[name=ar_first_name]").send_keys(u"عبد الله")
        self.browser.find_element_by_css_selector("[name=ar_middle_name]").send_keys(u"أحمد")
        self.browser.find_element_by_css_selector("[name=ar_last_name]").send_keys(u"محمد")

        self.browser.find_element_by_css_selector("[name=en_first_name]").send_keys("Abdullah")
        self.browser.find_element_by_css_selector("[name=en_middle_name]").send_keys("Ahmad")
        self.browser.find_element_by_css_selector("[name=en_last_name]").send_keys("Muhammad")

        self.browser.find_element_by_css_selector("[name=student_number]").send_keys("350212011")
        self.browser.find_element_by_css_selector("[name=badge_number]").send_keys("34567")

        self.browser.find_element_by_css_selector("[name=email]").send_keys("%s@ksau-hs.edu.sa" % self.username)
        self.browser.find_element_by_css_selector("[name=alt_email]").send_keys("whatever@example.com")

        self.browser.find_element_by_css_selector("[name=phone_number]").send_keys("+966118011111")
        self.browser.find_element_by_css_selector("[name=mobile_number]").send_keys("+966567891011")

        self.browser.find_element_by_css_selector("[name=address]").send_keys("Moscow")

        self.browser.find_element_by_css_selector("[name=saudi_id_number]").send_keys("1234567890")
        self.browser.find_element_by_css_selector("[name=saudi_id]").send_keys(
            os.path.join(settings.BASE_DIR, "static/test_image.gif")
        )

        self.browser.find_element_by_css_selector("[name=medical_record_number]").send_keys("123456")

        self.browser.find_element_by_css_selector("[name=contact_person_name]").send_keys("Omar")
        self.browser.find_element_by_css_selector("[name=contact_person_relation]").send_keys("Brother")
        self.browser.find_element_by_css_selector("[name=contact_person_mobile]").send_keys("+966567123789")
        self.browser.find_element_by_css_selector("[name=contact_person_email]").send_keys("email@example.com")

        self.browser.find_element_by_css_selector("[name=gpa]").send_keys("4.5")
        self.browser.find_element_by_css_selector("[name=starting_month]").send_keys("July")
        self.browser.find_element_by_css_selector("[name=starting_year]").send_keys("2017")

        self.browser.find_element_by_css_selector("[name=password1]").send_keys("abcd1234")
        self.browser.find_element_by_css_selector("[name=password2]").send_keys("abcd1234")

    def test_correct_passport_number(self):
        """
        Test normal sign up.
        """
        self.browser.find_element_by_css_selector("[name=passport_number]").send_keys("A123456")
        self.browser.find_element_by_css_selector("[name=passport]").send_keys(
            os.path.join(settings.BASE_DIR, "static/test_image.gif")
        )
        self.browser.find_element_by_css_selector("button[type=submit]").click()
        self.assertEqual(
            self.browser.current_url,
            "%s%s" % (self.live_server_url, reverse("userena_signup_complete", args=(self.username, )))
        )

    def test_incorrect_passport_number(self):
        self.browser.find_element_by_css_selector("[name=passport_number]").send_keys("123456")  # without initial letter
        self.browser.find_element_by_css_selector("[name=passport]").send_keys(
            os.path.join(settings.BASE_DIR, "static/test_image.gif")
        )
        self.browser.find_element_by_css_selector("button[type=submit]").click()
        self.assertEqual(
            self.browser.current_url,
            "%s%s" % (self.live_server_url, reverse("userena_signup"))
        )
        try:
            self.browser.find_elements_by_xpath(
                "//*[contains(text(), '%s')]" % "Passport number should consist of a letter followed by 6 numbers."
            )
        except NoSuchElementException:
            raise AssertionError("Element not present.")

    def test_expired_or_no_passport_form(self):
        self.browser.find_element_by_css_selector("[name=has_no_passport]").send_keys(" ")
        self.browser.find_element_by_css_selector("[name=passport_attachment]").send_keys(
            os.path.join(settings.BASE_DIR, "static/expired_or_no_passport_form.pdf")
        )
        self.browser.find_element_by_css_selector("button[type=submit]").click()
        self.assertEqual(
            self.browser.current_url,
            "%s%s" % (self.live_server_url, reverse("userena_signup_complete", args=(self.username, )))
        )

    def test_fill_both_passport_and_no_passport_form(self):
        self.browser.find_element_by_css_selector("[name=passport_number]").send_keys("A123456")
        self.browser.find_element_by_css_selector("[name=passport]").send_keys(
            os.path.join(settings.BASE_DIR, "static/test_image.gif")
        )

        self.browser.find_element_by_css_selector("[name=has_no_passport]").send_keys(" ")

        self.browser.find_element_by_css_selector("[name=passport_attachment]").send_keys(
            os.path.join(settings.BASE_DIR, "static/expired_or_no_passport_form.pdf")
        )

        self.browser.find_element_by_css_selector("button[type=submit]").click()
        self.assertEqual(
            self.browser.current_url,
            "%s%s" % (self.live_server_url, reverse("userena_signup_complete", args=(self.username, )))
        )

