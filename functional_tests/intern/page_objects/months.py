from functional_tests.po_base import BasePage, BaseElement


class MonthListPage(BasePage):
    url = "/#/planner/"

    @property
    def month_boxes(self):
        return map(
            lambda element: MonthBox(self.browser, element),
            self.browser.find_elements_by_css_selector(".internship-month"),
        )


class MonthBox(BaseElement):

    @property
    def month_label(self):
        return self.element.find_element_by_css_selector(".box-title").text

    @property
    def box_class(self):
        return self.element.get_attribute("class")

    @property
    def is_occupied(self):
        return "occupied" in self.box_class

    @property
    def is_frozen(self):
        return "frozen" in self.box_class

    @property
    def is_disabled(self):
        return "disabled" in self.box_class

    @property
    def has_rotation_request(self):
        return "has-rotation-request" in self.box_class

    @property
    def has_rotation_cancel_request(self):
        return "has-rotation-cancel-request" in self.box_class

    @property
    def has_freeze_request(self):
        return "has-freeze-request" in self.box_class

    @property
    def has_freeze_cancel_request(self):
        return "has-freeze-cancel-request" in self.box_class

    @property
    def current_specialty(self):
        if self.is_occupied:
            return self.element.find_element_by_css_selector(".current-specialty").text
        return None

    @property
    def current_hospital(self):
        if self.is_occupied:
            return self.element.find_element_by_css_selector(".current-hospital").text
        return None

    @property
    def current_location(self):
        if self.is_occupied:
            return self.element.find_element_by_css_selector(".current-location").text
        return None

    @property
    def requested_specialty(self):
        if self.has_rotation_request:
            return self.element.find_element_by_css_selector(".requested-specialty").text
        return None

    @property
    def requested_hospital(self):
        if self.has_rotation_request:
            return self.element.find_element_by_css_selector(".requested-hospital").text
        return None

    @property
    def requested_location(self):
        if self.has_rotation_request:
            return self.element.find_element_by_css_selector(".requested-location").text
        return None

    @property
    def rotation_cancel_request_description(self):
        return self.element.find_element_by_css_selector(".rotation-cancel-request-description").text

    @property
    def disabled_month_description(self):
        return self.element.find_element_by_css_selector(".disabled-month-description").text

    @property
    def primary_button_text(self):
        return self.element.find_element_by_css_selector(".primary-button").text

    @property
    def extra_buttons_text_list(self):
        return map(
            lambda element: element.text,
            self.element.find_elements_by_css_selector(".extra-button"),
        )

    def toggle_dropdown(self):
        self.element.find_element_by_css_selector(".dropdown-toggle").click()
