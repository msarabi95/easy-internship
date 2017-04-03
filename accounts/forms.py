import random
from hashlib import sha1
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from accounts.models import Intern, Profile, University, Batch
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator, MinLengthValidator
from month import Month
from months.models import Internship
from userena.forms import SignupFormOnlyEmail, ChangeEmailForm
from userena.utils import get_profile_model


class ChooseUniversityForm(forms.Form):
    """
    A form shown at the beginning of the sign up process to choose an institute.
    """
    def __init__(self, *args, **kwargs):
        super(ChooseUniversityForm, self).__init__(*args, **kwargs)
        self.fields['university_id'].widget.attrs['class'] = 'input-lg'

    page = forms.IntegerField(initial=1, widget=forms.HiddenInput())
    university_id = forms.ChoiceField(
        label="University",
        choices=list(University.objects.values_list('id', 'name')) + [(-1, 'Other')]
    )


class BaseSignupForm(SignupFormOnlyEmail):
    """
    A full signup form for interns, which appropriately saves the intern's
    data into `User`, `Profile`, `Intern`, and `Internship` models.

    """
    def __init__(self, *args, **kwargs):
        super(BaseSignupForm, self).__init__(*args, **kwargs)
        self.fields['university'].initial = self.university_id

    page = forms.IntegerField(initial=2, widget=forms.HiddenInput())
    university = forms.CharField(widget=forms.HiddenInput())

    ar_first_name = forms.CharField(label="First name (Arabic)", max_length=32)
    ar_father_name = forms.CharField(label="Father name (Arabic)", max_length=32)
    ar_grandfather_name = forms.CharField(label="Grandfather name (Arabic)", max_length=32)
    ar_last_name = forms.CharField(label="Last name (Arabic)", max_length=32)

    en_first_name = forms.CharField(label="First name (English)", max_length=32)
    en_father_name = forms.CharField(label="Father name (English)", max_length=32)
    en_grandfather_name = forms.CharField(label="Grandfather name (English)", max_length=32)
    en_last_name = forms.CharField(label="Last name (English)", max_length=32)

    phone_number = forms.CharField(
        max_length=16,
        validators=[RegexValidator(r'^\+[1-9]{1}[0-9]{3,14}$', message="Phone number should follow the format +966XXXXXXXXX.")],
        required=False,
    )
    mobile_number = forms.CharField(
        max_length=16,
        validators=[RegexValidator(r'^\+[1-9]{1}[0-9]{3,14}$', message="Mobile number should follow the format +966XXXXXXXXX.")],
    )
    address = forms.CharField(
        max_length=128,
        widget=forms.Textarea
    )

    id_number = forms.CharField(
        label="ID number",
        max_length=10,
        validators=[RegexValidator(r'^\d+$', message="ID number should consist of numbers only.")]
    )
    id_image = forms.ImageField(
        label="ID image",
        help_text="Note that this will be visible to all medical internship unit staff members."
    )

    contact_person_name = forms.CharField(
        max_length=64
    )
    contact_person_relation = forms.CharField(
        max_length=32
    )
    contact_person_mobile = forms.CharField(
        max_length=16,
        validators=[RegexValidator(r'^\+[1-9]{1}[0-9]{3,14}$', message="Mobile number should follow the format +966XXXXXXXXX.")],
    )
    contact_person_email = forms.EmailField(
        max_length=64
    )

    gpa = forms.FloatField(
        label="GPA",
        validators=[MaxValueValidator(5.0), MinValueValidator(0.0)]
    )

    MONTH_CHOICES = (
        (1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December"),
    )

    starting_year = forms.IntegerField(
        label="Starting year",
        validators=[MinValueValidator(2017)],
        initial=2017,
    )
    starting_month = forms.IntegerField(
        label="Starting month",
        widget=forms.Select(choices=MONTH_CHOICES),
        initial=7,  # July is the default month for internship start
    )

    def get_username(self):
        """
        Generate a random username
        """
        while True:
            username = sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
            try:
                get_user_model().objects.get(username__iexact=username)
            except get_user_model().DoesNotExist: break
        return username

    def get_university(self):
        """
        Get the correct university for the user signing up
        """
        university_id = int(self.cleaned_data.get('university'))

        if university_id > 0:
            return University.objects.get(id=university_id)
        else:
            return University(
                name=self.cleaned_data.get('university_name'),
                abbreviation=self.cleaned_data.get('university_abbreviation'),
                city=self.cleaned_data.get('university_city'),
                country=self.cleaned_data.get('university_country'),
                internship_phone=self.cleaned_data.get('university_internship_phone'),
                internship_fax=self.cleaned_data.get('university_internship_fax'),
                internship_email=self.cleaned_data.get('university_internship_email'),
            )  # NOTE: This needs to be saved

    def save(self):
        """
        Override the save method to save the intern's info into models other than `User`.
        """
        # Use the first part of the user's email as a username
        self.cleaned_data['username'] = self.get_username()

        # Save the parent form and get the user.
        # Notice we're calling the super of `SignupFormOnlyEmail` (not BaseSignupForm), essentially
        # ignoring the save() implementation in `SignupFormOnlyEmail`
        new_user = super(SignupFormOnlyEmail, self).save()

        # Get the profile, the `save` method above creates a profile for each
        # user because it calls the manager method `create_user`.
        # See: https://github.com/bread-and-pepper/django-userena/blob/master/userena/managers.py#L65
        user_profile = new_user.profile

        user_profile.ar_first_name = self.cleaned_data['ar_first_name']
        user_profile.ar_father_name = self.cleaned_data['ar_father_name']
        user_profile.ar_grandfather_name = self.cleaned_data['ar_grandfather_name']
        user_profile.ar_last_name = self.cleaned_data['ar_last_name']

        user_profile.en_first_name = self.cleaned_data['en_first_name']
        user_profile.en_father_name = self.cleaned_data['en_father_name']
        user_profile.en_grandfather_name = self.cleaned_data['en_grandfather_name']
        user_profile.en_last_name = self.cleaned_data['en_last_name']

        # Sign-up is for interns only, so set the role of the user to intern
        user_profile.role = Profile.INTERN

        user_profile.save()

        # Create an Intern profile for the new user
        intern_profile = Intern(profile=user_profile)
        intern_profile.phone_number = self.cleaned_data['phone_number']
        intern_profile.mobile_number = self.cleaned_data['mobile_number']
        intern_profile.address = self.cleaned_data['address']

        intern_profile.id_number = self.cleaned_data['id_number']
        intern_profile.id_image = self.cleaned_data['id_image']

        intern_profile.contact_person_name = self.cleaned_data['contact_person_name']
        intern_profile.contact_person_relation = self.cleaned_data['contact_person_relation']
        intern_profile.contact_person_mobile = self.cleaned_data['contact_person_mobile']
        intern_profile.contact_person_email = self.cleaned_data['contact_person_email']

        intern_profile.gpa = self.cleaned_data['gpa']

        university = self.get_university()
        if not university.id:
            university.save()
        intern_profile.university = university

        intern_profile.batch = Batch.objects.for_user(
            start_month=Month(self.cleaned_data['starting_year'], self.cleaned_data['starting_month']),
            university=university,
        ).first()

        intern_profile.save()

        # Create an Internship object for the new intern
        internship = Internship(
            intern=intern_profile,
            start_month=Month(self.cleaned_data['starting_year'], self.cleaned_data['starting_month'])
        )
        internship.save()

        # Userena expects to get the new user from this form, so return the new
        # user.
        return new_user


class KSAUHSSignupForm(BaseSignupForm):
    """
    A signup form specific for KSAU-HS interns.
    """
    form_type = "ksauhs"

    def __init__(self, *args, **kw):
        """
        Add an extra validator to the email field.
        """
        super(KSAUHSSignupForm, self).__init__(*args, **kw)

        self.fields['email'].validators.append(RegexValidator(
            r'^\w+@ksau-hs.edu.sa$', message="Email must end in '@ksau-hs.edu.sa'."
        ))
        self.fields['phone_number'].validators = [RegexValidator(
            r'^\+966\d{9}$', message="Phone number should follow the format +966XXXXXXXXX."
        )]
        self.fields['mobile_number'].validators = [RegexValidator(
            r'^\+9665\d{8}$', message="Mobile number should follow the format +9665XXXXXXXX."
        )]
        self.fields['id_number'].validators = [RegexValidator(
            r'^\d{10}$', message="Saudi ID should consist of 10 numbers only."
        )]
        self.fields['contact_person_mobile'].validators = [RegexValidator(
            r'^\+9665\d{8}$', message="Mobile number should follow the format +9665XXXXXXXX."
        )]

    student_number = forms.CharField(
        max_length=9,
        validators=[RegexValidator(r'^\d+$', message="Enter numbers only."), MinLengthValidator(9)]
    )
    badge_number = forms.CharField(
        max_length=9,
        validators=[RegexValidator(r'^\d+$', message="Enter numbers only."), MinLengthValidator(5)]
    )
    alt_email = forms.EmailField(label="Alternative email")

    # Note that the following is a `has_no_passport`, opposite to the `has_passport` field on the `Intern `model
    has_no_passport = forms.BooleanField(
        required=False,
        label="I don't have a valid passport."
    )
    passport_number = forms.CharField(
        required=False,
        max_length=32,
        validators=[RegexValidator(
            r'^\w{1}\d{6}$',
            message="Passport number should consist of a letter followed by 6 numbers."
        )]
    )
    passport_image = forms.ImageField(
        required=False,
        label="Passport image",
        help_text="Note that this will be visible to all medical internship unit staff members."
    )
    passport_attachment = forms.FileField(
        required=False,
        label="Expired or no passport form",
    )

    medical_record_number = forms.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d+$', message="Enter numbers only.")]
    )

    def clean(self):
        """
        Validate passport fields.
        """
        cleaned_data = super(KSAUHSSignupForm, self).clean()
        if cleaned_data.get('has_no_passport') is True:
            if cleaned_data.get('passport_attachment') is None:

                # TODO: Clear passport & passport number

                self.add_error('passport_attachment', forms.ValidationError("This field is required."))
        else:

            # TODO: Clear passport attachment

            if cleaned_data.get('passport_number', None) == "":
                self.add_error('passport_number', forms.ValidationError("This field is required."))
            if cleaned_data.get('passport_image') is None:
                self.add_error('passport_image', forms.ValidationError("This field is required."))
        return cleaned_data

    def clean_email(self):
        email = super(KSAUHSSignupForm, self).clean_email()
        username_to_be = email.split("@")[0].lower()

        if User.objects.filter(username=username_to_be).exists():
            raise forms.ValidationError("This email conflicts with an existing username.")

        return email

    def get_username(self):
        return self.cleaned_data['email'].split("@")[0].lower()

    def save(self):
        user = super(KSAUHSSignupForm, self).save()
        intern_profile = user.profile.intern

        intern_profile.alt_email = self.cleaned_data['alt_email']
        intern_profile.student_number = self.cleaned_data['student_number']
        intern_profile.badge_number = self.cleaned_data['badge_number']

        intern_profile.has_passport = not self.cleaned_data.get('has_no_passport', False)
        intern_profile.passport_number = self.cleaned_data['passport_number']
        intern_profile.passport = self.cleaned_data['passport_image']
        intern_profile.passport_attachment = self.cleaned_data['passport_attachment']

        intern_profile.medical_record_number = self.cleaned_data['medical_record_number']

        intern_profile.save()

        return user


class AGUSignupForm(BaseSignupForm):
    """
    A signup form specific for AGU interns.
    """
    form_type = "agu"

    passport_number = forms.CharField(
        required=False,
        max_length=32,
        # validators=[RegexValidator(
        #     r'^\w{1}\d{6}$',
        #     message="Passport number should consist of a letter followed by 6 numbers."
        # )]
    )
    passport_image = forms.ImageField(
        required=False,
        label="Passport image",
        help_text="Note that this will be visible to all medical internship unit staff members."
    )

    def save(self):
        user = super(AGUSignupForm, self).save()
        intern_profile = user.profile.intern

        intern_profile.passport_number = self.cleaned_data.get('passport_number')
        intern_profile.passport_image = self.cleaned_data.get('passport_image')

        intern_profile.save()

        return user


class OutsideSignupForm(BaseSignupForm):
    """
    A signup form for all interns outside KSAU-HS and AGU.
    """
    form_type = "outside"

    def __init__(self, *args, **kwargs):
        super(OutsideSignupForm, self).__init__(*args, **kwargs)
        self.fields['graduation_year'].widget.attrs['placeholder'] = "Year"

        if self.university_id > 0:
            self.university = University.objects.get(id=self.university_id)

            self.fields['university_name'].initial = self.university.name
            self.fields['university_abbreviation'].initial = self.university.abbreviation
            self.fields['university_city'].initial = self.university.city
            self.fields['university_country'].initial = self.university.country
            self.fields['university_internship_phone'].initial = self.university.internship_phone
            self.fields['university_internship_fax'].initial = self.university.internship_fax
            self.fields['university_internship_email'].initial = self.university.internship_email

            self.fields['university_name'].disabled = True
            self.fields['university_abbreviation'].disabled = True
            self.fields['university_city'].disabled = True
            self.fields['university_country'].disabled = True
            self.fields['university_internship_phone'].disabled = True
            self.fields['university_internship_fax'].disabled = True
            self.fields['university_internship_email'].disabled = True

    graduation_year = forms.IntegerField(
        initial=2017,
    )
    graduation_month = forms.IntegerField(
        widget=forms.Select(choices=BaseSignupForm.MONTH_CHOICES),
        initial=6,
    )

    medical_checklist = forms.FileField()
    academic_transcript = forms.FileField()

    university_name = forms.CharField(
        label="Name",
    )
    university_abbreviation = forms.CharField(
        label="Abbreviation",
    )
    university_city = forms.CharField(
        label="City",
    )
    university_country = forms.CharField(
        label="Country",
    )
    university_internship_phone = forms.CharField(
        label="Internship office phone",
    )
    university_internship_fax = forms.CharField(
        label="Internship office fax",
    )
    university_internship_email = forms.CharField(
        label="Internship office email",
    )

    def save(self):
        user = super(OutsideSignupForm, self).save()
        intern_profile = user.profile.intern

        intern_profile.graduation_date = Month(self.cleaned_data['graduation_year'], self.cleaned_data['graduation_month'])
        intern_profile.medical_checklist = self.cleaned_data['medical_checklist']
        intern_profile.academic_transcript = self.cleaned_data['academic_transcript']

        intern_profile.save()

        return user


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

    # Note that the following is a `has_no_passport`, opposite to the `has_passport` field on the `Intern `model
    has_no_passport = forms.BooleanField(
        required=False,
        label="I don't have a valid passport."
    )
    passport_number = forms.CharField(
        required=False,
        max_length=32,
        validators=[RegexValidator(
            r'^\w{1}\d{6}$',
            message="Passport number should consist of a letter followed by 6 numbers."
        )]
    )
    passport = forms.ImageField(
        required=False,
        label="Passport image",
        help_text="Note that this will be visible to all medical internship unit staff members."
    )
    passport_attachment = forms.FileField(
        required=False,
        label="Expired or no passport form",
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

        self.fields['has_no_passport'].initial = not intern_profile.has_passport
        self.fields['passport_number'].initial = intern_profile.passport_number
        self.fields['passport'].initial = intern_profile.passport
        self.fields['passport_attachment'].initial = intern_profile.passport_attachment

        self.fields['medical_record_number'].initial = intern_profile.medical_record_number

        self.fields['contact_person_name'].initial = intern_profile.contact_person_name
        self.fields['contact_person_relation'].initial = intern_profile.contact_person_relation
        self.fields['contact_person_mobile'].initial = intern_profile.contact_person_mobile
        self.fields['contact_person_email'].initial = intern_profile.contact_person_email

        self.fields['gpa'].initial = intern_profile.gpa

    def clean(self):
        """
        Validate passport fields.
        """
        cleaned_data = super(EditInternProfileForm, self).clean()
        if cleaned_data.get('has_no_passport') is True:
            if cleaned_data.get('passport_attachment') is None:

                # TODO: Clear passport & passport number

                self.add_error('passport_attachment', forms.ValidationError("This field is required."))
        else:

            # TODO: Clear passport attachment

            if cleaned_data.get('passport_number') == "":
                self.add_error('passport_number', forms.ValidationError("This field is required."))
            if cleaned_data.get('passport') is None:
                self.add_error('passport', forms.ValidationError("This field is required."))
        return cleaned_data

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

        intern_profile.has_passport = not self.cleaned_data.get('has_no_passport', False)
        intern_profile.passport_number = self.cleaned_data['passport_number']
        intern_profile.passport = self.cleaned_data['passport']
        intern_profile.passport_attachment = self.cleaned_data['passport_attachment']

        intern_profile.medical_record_number = self.cleaned_data['medical_record_number']

        intern_profile.contact_person_name = self.cleaned_data['contact_person_name']
        intern_profile.contact_person_relation = self.cleaned_data['contact_person_relation']
        intern_profile.contact_person_mobile = self.cleaned_data['contact_person_mobile']
        intern_profile.contact_person_email = self.cleaned_data['contact_person_email']

        intern_profile.gpa = self.cleaned_data['gpa']

        intern_profile.save()

        return profile
