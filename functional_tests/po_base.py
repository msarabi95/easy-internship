

class BasePage(object):
    """
    Base class for page objects.
    Adapted from: https://justin.abrah.ms/python/selenium-page-object-pattern--the-key-to-maintainable-tests.html
    """
    url = None

    def __init__(self, browser, base_url):
        self.browser = browser
        self.base_url = base_url

    @property
    def title(self):
        return self.browser.title

    def fill_form_by_css(self, form_css, value):
        elem = self.browser.find(form_css)
        elem.send_keys(value)

    def fill_form_by_id(self, form_element_id, value):
        return self.fill_form_by_css('#%s' % form_element_id, value)

    def navigate(self):
        self.browser.get(self.base_url + str(self.url))


class BaseElement(object):
    """
    Base class for element objects.
    """
    def __init__(self, browser, element):
        """

        Args:
            browser: A selenium webdriver instance
            element: A selenium WebElement

        Returns: None

        """
        self.browser = browser
        self.element = element
