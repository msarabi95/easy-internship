
from misc.models import Announcement
from rest_framework import serializers
from django.utils import timezone


class AnnouncementSerializer(serializers.ModelSerializer):


    def create(self,validated_data):
        if not validated_data.is_published:
            validated_data.publish_datetime = None
            validated_data.save()
        return alidated_data

    def update(self, instance, validated_data):
        if validated_data.is_published and not instance.is_published:
            validated_data.publish_datetime = timezone.now()
            validated_data.save()
            return validated_data
        elif not validated_data.is_published:
            validated_data.publish_datetime = None
            validated_data.save()
            return validated_data

    class Meta:
        model = Announcement
        author = serializers.ReadOnlyField(source='author.username')
        fields = '__all__'

