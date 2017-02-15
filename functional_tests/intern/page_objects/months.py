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
    def current_is_elective(self):
        if self.is_occupied:
            return self.check_element_exists_by_css_selector(".current-elective")
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
    def requested_is_elective(self):
        if self.has_rotation_request:
            return self.check_element_exists_by_css_selector(".requested-elective")
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


class MonthDetailPage(BasePage):
    @property
    def url(self):
        return "#/planner/%d/" % int(self.month)

    def __init__(self, month, *args, **kwargs):
        self.month = month
        super(MonthDetailPage, self).__init__(*args, **kwargs)

    @property
    def month_label(self):
        return self.browser.find_element_by_css_selector(".month-label").text

    @property
    def summary(self):
        return self.browser.find_element_by_css_selector(".summary").text

    @property
    def is_empty(self):
        return

    @property
    def is_occupied(self):
        return self.check_element_exists_by_css_selector(".current-rotation-detail")

    @property
    def is_frozen(self):
        return self.check_element_exists_by_css_selector(".current-freeze-detail")

    @property
    def is_disabled(self):
        return

    @property
    def has_rotation_request(self):
        return self.check_element_exists_by_css_selector(".rotation-request-detail")

    @property
    def has_rotation_cancel_request(self):
        return self.check_element_exists_by_css_selector(".rotation-cancel-request-detail")

    @property
    def has_freeze_request(self):
        return self.check_element_exists_by_css_selector(".freeze-request-detail")

    @property
    def has_freeze_cancel_request(self):
        return self.check_element_exists_by_css_selector(".freeze-cancel-request-detail")

    # ############################################################################################################## #

    @property
    def current_specialty(self):
        if self.is_occupied:
            return self.browser.find_elements_by_css_selector(".current-specialty").text
        return None

    @property
    def current_hospital(self):
        if self.is_occupied:
            return self.browser.find_elements_by_css_selector(".current-hospital").text
        return None

    @property
    def current_location(self):
        if self.is_occupied:
            return self.browser.find_elements_by_css_selector(".current-location").text
        return None

    @property
    def current_is_elective(self):
        if self.is_occupied:
            return self.browser.find_elements_by_css_selector(".current-elective").text == "Yes"
        return None

    @property
    def current_rotation_submission_datetime(self):
        if self.is_occupied:
            return self.browser.find_elements_by_css_selector(".current-rotation-submission-datetime").text
        return None

    @property
    def current_rotation_approval_datetime(self):
        if self.is_occupied:
            return self.browser.find_elements_by_css_selector(".current-rotation-approval-datetime").text
        return None

    # ############################################################################################################## #

    @property
    def rotation_request_specialty(self):
        if self.has_rotation_request:
            return self.browser.find_element_by_css_selector(".requested-specialty").text
        return None

    @property
    def rotation_request_hospital(self):
        if self.has_rotation_request:
            return self.browser.find_element_by_css_selector(".requested-hospital").text
        return None

    @property
    def rotation_request_location(self):
        if self.has_rotation_request:
            return self.browser.find_element_by_css_selector(".requested-location").text
        return None

    @property
    def rotation_request_is_elective(self):
        if self.has_rotation_request:
            return self.browser.find_element_by_css_selector(".requested-elective").text == "Yes"
        return None

    @property
    def rotation_request_submission_datetime(self):
        if self.has_rotation_request:
            return self.browser.find_element_by_css_selector(".requested-submission-datetime").text
        return None

    @property
    def rotation_request_contact_name(self):
        if self.has_rotation_request:
            return self.browser.find_element_by_css_selector(".requested-contact-name").text
        return None

    @property
    def rotation_request_contact_position(self):
        if self.has_rotation_request:
            return self.browser.find_element_by_css_selector(".requested-contact-position").text
        return None

    @property
    def rotation_request_email(self):
        if self.has_rotation_request:
            return self.browser.find_element_by_css_selector(".requested-email").text
        return None

    @property
    def rotation_request_phone(self):
        if self.has_rotation_request:
            return self.browser.find_element_by_css_selector(".requested-phone").text
        return None

    @property
    def rotation_request_extension(self):
        if self.has_rotation_request:
            return self.browser.find_element_by_css_selector(".requested-extension").text
        return None

    # ############################################################################################################## #

    @property
    def rotation_cancel_request_description(self):
        if self.has_rotation_cancel_request:
            return self.browser.find_element_by_css_selector(".rotation-cancel-request-description").text
        return None

    @property
    def rotation_cancel_request_submission_datetime(self):
        if self.has_rotation_cancel_request:
            return self.browser.find_element_by_css_selector(".rotation-cancel-request-submission-datetime").text
        return None

    # ############################################################################################################## #

    @property
    def current_freeze_submission_datetime(self):
        if self.is_frozen:
            return self.browser.find_element_by_css_selector(".current-freeze-request-datetime").text
        return None

    @property
    def current_freeze_justification(self):
        if self.is_frozen:
            return self.browser.find_element_by_css_selector(".current-freeze-justification").text
        return None

    @property
    def current_freeze_approval_datetime(self):
        if self.is_frozen:
            return self.browser.find_element_by_css_selector(".current-freeze-approval-datetime").text
        return None

    # ############################################################################################################## #

    @property
    def freeze_request_submission_datetime(self):
        if self.has_freeze_request:
            return self.browser.find_element_by_css_selector(".freeze-request-submission-datetime").text
        return None

    @property
    def freeze_request_justification(self):
        if self.has_freeze_request:
            return self.browser.find_element_by_css_selector(".freeze-request-justification").text
        return None

    # ############################################################################################################## #

    @property
    def freeze_cancel_request_submission_datetime(self):
        if self.has_freeze_request:
            return self.browser.find_element_by_css_selector(".freeze-cancel-request-submission-datetime").text
        return None
