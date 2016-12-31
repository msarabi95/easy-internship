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
    passport = serializers.SerializerMethodField(method_name='get_passport_url')
    passport_attachment = serializers.SerializerMethodField(method_name='get_passport_attachment_url')

    def get_passport_url(self, obj):
        return obj.passport.url if obj.has_passport else None

    def get_passport_attachment_url(self, obj):
        return obj.passport_attachment.url if not obj.has_passport else None

    class Meta:
        model = Intern
        fields = ('id', 'profile', 'alt_email', 'student_number', 'badge_number', 'phone_number', 'mobile_number',
                  'address', 'saudi_id_number', 'saudi_id', 'has_passport', 'passport_number', 'passport', 'passport_attachment',
                  'medical_record_number', 'contact_person_name', 'contact_person_relation',
                  'contact_person_mobile', 'contact_person_email', 'gpa')


class InternTableSerializer(serializers.ModelSerializer):
    mugshot = serializers.URLField(source='profile.get_mugshot_url')
    name = serializers.CharField(source='profile.get_en_full_name')
    email = serializers.EmailField(source='profile.user.email')
    internship_id = serializers.IntegerField(source='internship.id')

    class Meta:
        model = Intern
        fields = ('id', 'mugshot', 'name', 'student_number', 'badge_number', 'email', 'mobile_number', 'internship_id',)
