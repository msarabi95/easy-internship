from django.core.urlresolvers import reverse_lazy

from functional_tests.po_base import BasePage


class SigninPage(BasePage):
    url = reverse_lazy("userena_signin")

    _username_field_selector = "input[name=identification]"
    _password_field_selector = "input[name=password]"
    _submit_button_selector = "button[type=submit]"

    @property
    def username(self):
        return self.browser.find_element_by_css_selector(self._username_field_selector).value()

    @username.setter
    def username(self, value):
        self.browser.find_element_by_css_selector(self._username_field_selector).send_keys(value)

    @property
    def password(self):
        return self.browser.find_element_by_css_selector(self._password_field_selector).value()

    @password.setter
    def password(self, value):
        self.browser.find_element_by_css_selector(self._password_field_selector).send_keys(value)

    @property
    def submit_button(self):
        return self.browser.find_element_by_css_selector(self._submit_button_selector)

    def login(self, username, password, remember_me=False):
        self.username = username
        self.password = password

        if remember_me:
            pass

        self.submit_button.click()
