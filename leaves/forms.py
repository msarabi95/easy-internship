from djng.forms import NgFormValidationMixin, NgModelFormMixin
from djng.styling.bootstrap3.forms import Bootstrap3ModelForm
from leaves.models import LeaveRequest


class LeaveRequestForm(NgFormValidationMixin, NgModelFormMixin, Bootstrap3ModelForm):
    form_name = 'leaveRequestForm'
    scope_prefix = 'leaveRequestData'

    class Meta:
        model = LeaveRequest
        fields = ('type', 'start_date', 'end_date')