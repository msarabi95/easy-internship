from djng.forms import NgFormValidationMixin, NgModelFormMixin
from djng.styling.bootstrap3.forms import Bootstrap3ModelForm

from months.models import FreezeRequest


class FreezeRequestForm(NgFormValidationMixin, NgModelFormMixin, Bootstrap3ModelForm):
    form_name = 'freezeRequestForm'
    scope_prefix = 'freezeRequestData'

    class Meta:
        model = FreezeRequest
        fields = ('justification', )
