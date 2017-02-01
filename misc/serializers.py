
from misc.models import Announcement
from rest_framework import serializers
from django.utils import timezone


class AnnouncementSerializer(serializers.ModelSerializer):


    def create(self,validated_data):
        if validated_data.is_published:
            instance.publish_datetime = timezone.now()
            instance.save()
        return instance

    def update(self, instance, validated_data):
        if validated_data.is_published and not instance.is_published:
            instance.publish_datetime = timezone.now()
            instance.save()
            return instance
        elif not validated_data.is_published:
            instance.publish_datetime = None
            instance.save()
        return instance

    class Meta:
        model = Announcement
        author = serializers.ReadOnlyField(source='author.username')
        fields = '__all__'

