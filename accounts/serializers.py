from accounts.models import Profile, Intern, Batch
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
        fields = ('id', 'user', 'role', 'mugshot', 'ar_first_name', 'ar_father_name', 'ar_last_name',
                  'en_first_name', 'en_father_name', 'en_last_name', 'ar_full_name', 'en_full_name')


class InternSerializer(serializers.ModelSerializer):
    id_image = serializers.URLField(source='id_image.url')
    passport_image = serializers.SerializerMethodField(method_name='get_passport_image_url')
    passport_attachment = serializers.SerializerMethodField(method_name='get_passport_attachment_url')
    batch = serializers.StringRelatedField()
    university = serializers.StringRelatedField()

    def get_passport_image_url(self, obj):
        if (obj.is_ksauhs_intern and obj.has_passport) or (obj.is_agu_intern and obj.passport_image):
            try:
                return obj.passport_image.url
            except ValueError:
                return None
        return None

    def get_passport_attachment_url(self, obj):
        return obj.passport_attachment.url if obj.is_ksauhs_intern and not obj.has_passport else None

    class Meta:
        model = Intern
        fields = ('id', 'profile', 'alt_email', 'student_number', 'badge_number', 'phone_number', 'mobile_number',
                  'address', 'id_number', 'id_image', 'has_passport', 'passport_number', 'passport_image', 'passport_attachment',
                  'medical_record_number', 'medical_checklist', 'contact_person_name', 'contact_person_relation',
                  'contact_person_mobile', 'contact_person_email', 'gpa', 'academic_transcript', 'graduation_date',
                  'is_ksauhs_intern', 'is_agu_intern', 'is_outside_intern', 'internship', 'batch', 'university')


class BatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Batch
        fields = '__all__'


class InternTableSerializer(serializers.ModelSerializer):
    mugshot = serializers.URLField(source='profile.get_mugshot_url')
    name = serializers.CharField(source='profile.get_en_full_name')
    email = serializers.EmailField(source='profile.user.email')
    internship_id = serializers.IntegerField(source='internship.id')

    class Meta:
        model = Intern
        fields = ('id', 'mugshot', 'name', 'student_number', 'badge_number', 'email', 'mobile_number', 'internship_id',)


class FullInternSerializer(InternSerializer):
    profile = ProfileSerializer()

    class Meta(InternSerializer.Meta):
        pass
