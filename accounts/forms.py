from django.contrib.auth.models import User

from accounts.models import Intern, Profile
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator, MinLengthValidator
from month import Month
from months.models import Internship
from userena.forms import SignupFormOnlyEmail, ChangeEmailForm
from userena.utils import get_profile_model


class InternSignupForm(SignupFormOnlyEmail):
    """
    A full signup form for interns, which appropriately saves the intern's
    data into `User`, `Profile`, `Intern`, and `Internship` models.

    """
    ar_first_name = forms.CharField(label="First name (Arabic)", max_length=32)
    ar_middle_name = forms.CharField(label="Middle name (Arabic)", max_length=32)
    ar_last_name = forms.CharField(label="Last name (Arabic)", max_length=32)

    en_first_name = forms.CharField(label="First name (English)", max_length=32)
    en_middle_name = forms.CharField(label="Middle name (English)", max_length=32)
    en_last_name = forms.CharField(label="Last name (English)", max_length=32)

    student_number = forms.CharField(
        max_length=9,
        validators=[RegexValidator(r'^\d+$', message="Enter numbers only."), MinLengthValidator(9)]
    )
    badge_number = forms.CharField(
        max_length=9,
        validators=[RegexValidator(r'^\d+$', message="Enter numbers only."), MinLengthValidator(5)]
    )
    alt_email = forms.EmailField(label="Alternative email")
    phone_number = forms.CharField(
        max_length=16,
        validators=[RegexValidator(r'^\+966\d{9}$', message="Phone number should follow the format +966XXXXXXXXX.")],
        required=False,
    )
    mobile_number = forms.CharField(
        max_length=16,
        validators=[RegexValidator(r'^\+9665\d{8}$', message="Mobile number should follow the format +9665XXXXXXXX.")]
    )
    address = forms.CharField(
        max_length=128,
        widget=forms.Textarea
    )

    saudi_id_number = forms.CharField(
        label="Saudi ID number",
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', message="Saudi ID should consist of 10 numbers only.")]
    )
    saudi_id = forms.ImageField(
        label="Saudi ID image",
        help_text="Note that this will be visible to all medical internship unit staff members."
    )
    passport_number = forms.CharField(
        max_length=32,
        validators=[RegexValidator(
            r'^\w{1}\d{6}$',
            message="Passport number should consist of a letter followed by 6 numbers."
        )]
    )
    passport = forms.ImageField(
        label="Passport image",
        help_text="Note that this will be visible to all medical internship unit staff members."
    )
    medical_record_number = forms.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d+$', message="Enter numbers only.")]
    )

    contact_person_name = forms.CharField(
        max_length=64
    )
    contact_person_relation = forms.CharField(
        max_length=32
    )
    contact_person_mobile = forms.CharField(
        max_length=16,
        validators=[RegexValidator(r'^\+9665\d{8}$', message="Mobile number should follow the format +9665XXXXXXXX.")],
    )
    contact_person_email = forms.EmailField(
        max_length=64
    )

    gpa = forms.FloatField(
        label="GPA",
        validators=[MaxValueValidator(5.0), MinValueValidator(0.0)]
    )

    starting_year = forms.IntegerField(
        label="Starting year",
        validators=[MinValueValidator(2017)],
        help_text="The year in which your internship will start (e.g. 2017)",
    )

    def __init__(self, *args, **kw):
        """
        Add an extra validator to the email field.

        """
        super(InternSignupForm, self).__init__(*args, **kw)

        self.fields['email'].validators.append(RegexValidator(
            r'^\w+@ksau-hs.edu.sa$', message="Email must end in '@ksau-hs.edu.sa'."
        ))

    def clean_email(self):
        email = super(InternSignupForm, self).clean_email()
        username_to_be = email.split("@")[0].lower()

        if User.objects.filter(username=username_to_be).exists():
            raise forms.ValidationError("This email conflicts with an existing username.")

        return email

    def save(self):
        """
        Override the save method to save the intern's info into models other than `User`.

        """
        # Use the first part of the user's email as a username
        self.cleaned_data['username'] = self.cleaned_data['email'].split("@")[0].lower()

        # Save the parent form and get the user.
        # Notice we're calling the super of `SignupFormOnlyEmail` (not InternSignupForm), essentially
        # ignoring the save() implementation in `SignupFormOnlyEmail`
        new_user = super(SignupFormOnlyEmail, self).save()

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
        intern_profile.alt_email = self.cleaned_data['alt_email']
        intern_profile.student_number = self.cleaned_data['student_number']
        intern_profile.badge_number = self.cleaned_data['badge_number']
        intern_profile.phone_number = self.cleaned_data['phone_number']
        intern_profile.mobile_number = self.cleaned_data['mobile_number']
        intern_profile.address = self.cleaned_data['address']

        intern_profile.saudi_id_number = self.cleaned_data['saudi_id_number']
        intern_profile.saudi_id = self.cleaned_data['saudi_id']
        intern_profile.passport_number = self.cleaned_data['passport_number']
        intern_profile.passport = self.cleaned_data['passport']
        intern_profile.medical_record_number = self.cleaned_data['medical_record_number']

        intern_profile.contact_person_name = self.cleaned_data['contact_person_name']
        intern_profile.contact_person_relation = self.cleaned_data['contact_person_relation']
        intern_profile.contact_person_mobile = self.cleaned_data['contact_person_mobile']
        intern_profile.contact_person_email = self.cleaned_data['contact_person_email']

        intern_profile.gpa = self.cleaned_data['gpa']

        intern_profile.save()

        # Create an Internship object for the new intern
        internship = Internship(
            intern=intern_profile,
            start_month=Month(self.cleaned_data['starting_year'], 7)  # July of the year selected by the user
        )
        internship.save()

        # Userena expects to get the new user from this form, so return the new
        # user.
        return new_user


class ChangeInternEmailForm(ChangeEmailForm):
    def __init__(self, *args, **kw):
        """
        Add an extra validator to the email field.

        """
        super(ChangeInternEmailForm, self).__init__(*args, **kw)

        self.fields['email'].validators.append(RegexValidator(
            r'^\w+@ksau-hs.edu.sa$', message="Email must end in '@ksau-hs.edu.sa'."
        ))


class EditInternProfileForm(forms.ModelForm):
    ar_first_name = forms.CharField(label="First name (Arabic)", max_length=32)
    ar_middle_name = forms.CharField(label="Middle name (Arabic)", max_length=32)
    ar_last_name = forms.CharField(label="Last name (Arabic)", max_length=32)

    en_first_name = forms.CharField(label="First name (English)", max_length=32)
    en_middle_name = forms.CharField(label="Middle name (English)", max_length=32)
    en_last_name = forms.CharField(label="Last name (English)", max_length=32)

    student_number = forms.CharField(
        max_length=9,
        validators=[RegexValidator(r'^\d+$', message="Enter numbers only."), MinLengthValidator(9)]
    )
    badge_number = forms.CharField(
        max_length=9,
        validators=[RegexValidator(r'^\d+$', message="Enter numbers only."), MinLengthValidator(5)]
    )
    alt_email = forms.EmailField(label="Alternative email")
    phone_number = forms.CharField(
        max_length=16,
        validators=[RegexValidator(r'^\+966\d{9}$', message="Phone number should follow the format +966XXXXXXXXX.")],
        required=False,
    )
    mobile_number = forms.CharField(
        max_length=16,
        validators=[RegexValidator(r'^\+9665\d{8}$', message="Mobile number should follow the format +9665XXXXXXXX.")]
    )
    address = forms.CharField(
        max_length=128,
        widget=forms.Textarea
    )

    saudi_id_number = forms.CharField(
        label="Saudi ID number",
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', message="Saudi ID should consist of 10 numbers only.")]
    )
    saudi_id = forms.ImageField(
        label="Saudi ID image",
        help_text="Note that this will be visible to all medical internship unit staff members."
    )
    passport_number = forms.CharField(
        max_length=32,
        validators=[RegexValidator(
            r'^\w{1}\d{6}$',
            message="Passport number should consist of a letter followed by 6 numbers."
        )]
    )
    passport = forms.ImageField(
        label="Passport image",
        help_text="Note that this will be visible to all medical internship unit staff members."
    )
    medical_record_number = forms.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d+$', message="Enter numbers only.")]
    )

    contact_person_name = forms.CharField(
        max_length=64
    )
    contact_person_relation = forms.CharField(
        max_length=32
    )
    contact_person_mobile = forms.CharField(
        max_length=16,
        validators=[RegexValidator(r'^\+9665\d{8}$', message="Mobile number should follow the format +9665XXXXXXXX.")],
    )
    contact_person_email = forms.EmailField(
        max_length=64
    )

    gpa = forms.FloatField(
        label="GPA",
        validators=[MaxValueValidator(5.0), MinValueValidator(0.0)]
    )

    class Meta:
        model = get_profile_model()
        exclude = ["user", "role", "privacy"]

    def __init__(self, *args, **kwargs):
        super(EditInternProfileForm, self).__init__(*args, **kwargs)

        # Initialize values of Intern profile fields

        intern_profile = self.instance.intern

        self.fields['alt_email'].initial = intern_profile.alt_email
        self.fields['student_number'].initial = intern_profile.student_number
        self.fields['badge_number'].initial = intern_profile.badge_number
        self.fields['phone_number'].initial = intern_profile.phone_number
        self.fields['mobile_number'].initial = intern_profile.mobile_number
        self.fields['address'].initial = intern_profile.address

        self.fields['saudi_id_number'].initial = intern_profile.saudi_id_number
        self.fields['saudi_id'].initial = intern_profile.saudi_id
        self.fields['passport_number'].initial = intern_profile.passport_number
        self.fields['passport'].initial = intern_profile.passport
        self.fields['medical_record_number'].initial = intern_profile.medical_record_number

        self.fields['contact_person_name'].initial = intern_profile.contact_person_name
        self.fields['contact_person_relation'].initial = intern_profile.contact_person_relation
        self.fields['contact_person_mobile'].initial = intern_profile.contact_person_mobile
        self.fields['contact_person_email'].initial = intern_profile.contact_person_email

        self.fields['gpa'].initial = intern_profile.gpa

    def save(self, *args, **kwargs):
        profile = super(EditInternProfileForm, self).save(*args, **kwargs)

        intern_profile = profile.intern

        intern_profile.alt_email = self.cleaned_data['alt_email']
        intern_profile.student_number = self.cleaned_data['student_number']
        intern_profile.badge_number = self.cleaned_data['badge_number']
        intern_profile.phone_number = self.cleaned_data['phone_number']
        intern_profile.mobile_number = self.cleaned_data['mobile_number']
        intern_profile.address = self.cleaned_data['address']

        intern_profile.saudi_id_number = self.cleaned_data['saudi_id_number']
        intern_profile.saudi_id = self.cleaned_data['saudi_id']
        intern_profile.passport_number = self.cleaned_data['passport_number']
        intern_profile.passport = self.cleaned_data['passport']
        intern_profile.medical_record_number = self.cleaned_data['medical_record_number']

        intern_profile.contact_person_name = self.cleaned_data['contact_person_name']
        intern_profile.contact_person_relation = self.cleaned_data['contact_person_relation']
        intern_profile.contact_person_mobile = self.cleaned_data['contact_person_mobile']
        intern_profile.contact_person_email = self.cleaned_data['contact_person_email']

        intern_profile.gpa = self.cleaned_data['gpa']

        intern_profile.save()

        return profile
