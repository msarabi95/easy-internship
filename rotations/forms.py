from django import forms
from djng.forms.angular_model import NgModelFormMixin
from djng.forms.angular_validation import NgFormValidationMixin
from djng.styling.bootstrap3.forms import Bootstrap3ModelForm
from rotations.models import RequestedDepartment


class RotationRequestForm(NgFormValidationMixin, NgModelFormMixin, Bootstrap3ModelForm):
    form_name = 'rotationRequestForm'
    scope_prefix = 'rotationRequestData'

    def __init__(self, *args, **kwargs):
        super(RotationRequestForm, self).__init__(*args, **kwargs)
        self.fields['department_specialty'].label = "Specialty"
        self.fields['department_hospital'].label = "Hospital"
        self.fields['department_name'].label = "Name of Department"
        self.fields['department_contact_name'].label = "Name of Contact Person in the Department"
        self.fields['department_email'].label = "Email"
        self.fields['department_phone'].label = "Phone"
        self.fields['department_extension'].label = "Extension"

    is_elective = forms.BooleanField(required=False, initial=False,
                                     label="This is an elective.",
                                     help_text="Check this box if this is an elective rotation.")

    class Meta:
        model = RequestedDepartment
        fields = ('department_specialty', 'department_hospital', 'department_name',
                  'department_contact_name', 'department_email',
                  'department_phone', 'department_extension',
                  'department', 'is_in_database', 'is_elective')
        widgets = {'department': forms.HiddenInput(), 'is_in_database': forms.HiddenInput()}
