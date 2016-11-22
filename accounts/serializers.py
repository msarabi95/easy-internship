from accounts.models import Profile, Intern
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class ProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="get_role_display")
    ar_full_name = serializers.CharField(source="get_ar_full_name")
    en_full_name = serializers.CharField(source="get_en_full_name")
    mugshot = serializers.URLField(source="get_mugshot_url")

    class Meta:
        model = Profile
        fields = ('id', 'user', 'role', 'mugshot', 'ar_first_name', 'ar_middle_name', 'ar_last_name',
                  'en_first_name', 'en_middle_name', 'en_last_name', 'ar_full_name', 'en_full_name')


class InternSerializer(serializers.ModelSerializer):
    saudi_id = serializers.URLField(source='saudi_id.url')
    passport = serializers.URLField(source='passport.url')

    class Meta:
        model = Intern
        fields = ('id', 'profile', 'alt_email', 'student_number', 'badge_number', 'phone_number', 'mobile_number',
                  'address', 'saudi_id_number', 'saudi_id', 'passport_number', 'passport',
                  'medical_record_number', 'contact_person_name', 'contact_person_relation',
                  'contact_person_mobile', 'contact_person_email', 'gpa')
