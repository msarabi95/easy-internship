from accounts.models import Intern, Profile
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from month import Month
from planner.models import Internship
from userena.forms import SignupForm
from userena.utils import get_profile_model


class InternSignupForm(SignupForm):
    """
    A form to demonstrate how to add extra fields to the signup form, in this
    case adding the first and last name.

    """
    ar_first_name = forms.CharField(label="First name (Arabic)", max_length=32)
    ar_middle_name = forms.CharField(label="Middle name (Arabic)", max_length=32)
    ar_last_name = forms.CharField(label="Last name (Arabic)", max_length=32)

    en_first_name = forms.CharField(label="First name (English)", max_length=32)
    en_middle_name = forms.CharField(label="Middle name (English)", max_length=32)
    en_last_name = forms.CharField(label="Last name (English)", max_length=32)

    student_number = forms.CharField(max_length=9)
    badge_number = forms.CharField(max_length=9)
    phone_number = forms.CharField(max_length=16)
    mobile_number = forms.CharField(max_length=16)
    address = forms.CharField(max_length=128, widget=forms.Textarea)

    saudi_id_number = forms.CharField(max_length=10)
    passport_number = forms.CharField(max_length=32)
    medical_record_number = forms.CharField(max_length=10)

    contact_person_name = forms.CharField(max_length=64)
    contact_person_relation = forms.CharField(max_length=32)
    contact_person_mobile = forms.CharField(max_length=16)
    contact_person_email = forms.EmailField(max_length=64)

    gpa = forms.FloatField(validators=[MaxValueValidator(5.0), MinValueValidator(0.0)])

    def __init__(self, *args, **kw):
        """

        A bit of hackery to get the first name and last name at the top of the
        form instead at the end.

        """
        super(InternSignupForm, self).__init__(*args, **kw)
        # # Put the first and last name at the top
        # new_order = self.fields.keyOrder[:-2]
        # new_order.insert(0, 'first_name')
        # new_order.insert(1, 'last_name')
        # self.fields.keyOrder = new_order

    def save(self):
        """
        Override the save method to save the first and last name to the user
        field.

        """
        # First save the parent form and get the user.
        new_user = super(InternSignupForm, self).save()

        # Get the profile, the `save` method above creates a profile for each
        # user because it calls the manager method `create_user`.
        # See: https://github.com/bread-and-pepper/django-userena/blob/master/userena/managers.py#L65
        user_profile = new_user.profile
        
        user_profile.ar_first_name = self.cleaned_data['ar_first_name']
        user_profile.ar_middle_name = self.cleaned_data['ar_middle_name']
        user_profile.ar_last_name = self.cleaned_data['ar_last_name']
        
        user_profile.en_first_name = self.cleaned_data['en_first_name']
        user_profile.en_middle_name = self.cleaned_data['en_middle_name']
        user_profile.en_last_name = self.cleaned_data['en_last_name']

        # Sign-up is for interns only, so set the role of the user to intern
        user_profile.role = Profile.INTERN

        user_profile.save()
        
        # Create an Intern profile for the new user
        intern_profile = Intern(profile=user_profile)
        intern_profile.student_number = self.cleaned_data['student_number']
        intern_profile.badge_number = self.cleaned_data['badge_number']
        intern_profile.phone_number = self.cleaned_data['phone_number']
        intern_profile.mobile_number = self.cleaned_data['mobile_number']
        intern_profile.address = self.cleaned_data['address']

        intern_profile.saudi_id_number = self.cleaned_data['saudi_id_number']
        intern_profile.passport_number = self.cleaned_data['passport_number']
        intern_profile.medical_record_number = self.cleaned_data['medical_record_number']

        intern_profile.contact_person_name = self.cleaned_data['contact_person_name']
        intern_profile.contact_person_relation = self.cleaned_data['contact_person_relation']
        intern_profile.contact_person_mobile = self.cleaned_data['contact_person_mobile']
        intern_profile.contact_person_email = self.cleaned_data['contact_person_email']

        intern_profile.gpa = self.cleaned_data['gpa']

        intern_profile.save()

        # Create an Internship object for the new intern
        internship = Internship(intern=intern_profile, start_month=Month(2016, 7))  # FIXME: This should be set to something dynamic
        internship.save()

        # Userena expects to get the new user from this form, so return the new
        # user.
        return new_user


class EditInternProfileForm(forms.ModelForm):
    ar_first_name = forms.CharField(label="First name (Arabic)", max_length=32)
    ar_middle_name = forms.CharField(label="Middle name (Arabic)", max_length=32)
    ar_last_name = forms.CharField(label="Last name (Arabic)", max_length=32)

    en_first_name = forms.CharField(label="First name (English)", max_length=32)
    en_middle_name = forms.CharField(label="Middle name (English)", max_length=32)
    en_last_name = forms.CharField(label="Last name (English)", max_length=32)

    student_number = forms.CharField(max_length=9)
    badge_number = forms.CharField(max_length=9)
    phone_number = forms.CharField(max_length=16)
    mobile_number = forms.CharField(max_length=16)
    address = forms.CharField(max_length=128, widget=forms.Textarea)

    saudi_id_number = forms.CharField(max_length=10)
    passport_number = forms.CharField(max_length=32)
    medical_record_number = forms.CharField(max_length=10)

    contact_person_name = forms.CharField(max_length=64)
    contact_person_relation = forms.CharField(max_length=32)
    contact_person_mobile = forms.CharField(max_length=16)
    contact_person_email = forms.EmailField(max_length=64)

    gpa = forms.FloatField(validators=[MaxValueValidator(5.0), MinValueValidator(0.0)])

    class Meta:
        model = get_profile_model()
        exclude = ["user", "role"]

    def __init__(self, *args, **kwargs):
        super(EditInternProfileForm, self).__init__(*args, **kwargs)

        # Initialize values of Intern profile fields

        intern_profile = self.instance.intern

        self.fields['student_number'].initial = intern_profile.student_number
        self.fields['badge_number'].initial = intern_profile.badge_number
        self.fields['phone_number'].initial = intern_profile.phone_number
        self.fields['mobile_number'].initial = intern_profile.mobile_number
        self.fields['address'].initial = intern_profile.address

        self.fields['saudi_id_number'].initial = intern_profile.saudi_id_number
        self.fields['passport_number'].initial = intern_profile.passport_number
        self.fields['medical_record_number'].initial = intern_profile.medical_record_number

        self.fields['contact_person_name'].initial = intern_profile.contact_person_name
        self.fields['contact_person_relation'].initial = intern_profile.contact_person_relation
        self.fields['contact_person_mobile'].initial = intern_profile.contact_person_mobile
        self.fields['contact_person_email'].initial = intern_profile.contact_person_email

        self.fields['gpa'].initial = intern_profile.gpa

    def save(self, *args, **kwargs):
        profile = super(EditInternProfileForm, self).save(*args, **kwargs)

        intern_profile = profile.intern

        intern_profile.student_number = self.cleaned_data['student_number']
        intern_profile.badge_number = self.cleaned_data['badge_number']
        intern_profile.phone_number = self.cleaned_data['phone_number']
        intern_profile.mobile_number = self.cleaned_data['mobile_number']
        intern_profile.address = self.cleaned_data['address']

        intern_profile.saudi_id_number = self.cleaned_data['saudi_id_number']
        intern_profile.passport_number = self.cleaned_data['passport_number']
        intern_profile.medical_record_number = self.cleaned_data['medical_record_number']

        intern_profile.contact_person_name = self.cleaned_data['contact_person_name']
        intern_profile.contact_person_relation = self.cleaned_data['contact_person_relation']
        intern_profile.contact_person_mobile = self.cleaned_data['contact_person_mobile']
        intern_profile.contact_person_email = self.cleaned_data['contact_person_email']

        intern_profile.gpa = self.cleaned_data['gpa']

        intern_profile.save()

        return profile
