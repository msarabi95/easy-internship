
from misc.models import Announcement
from rest_framework import serializers
from django.utils import timezone


class AnnouncementSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        instance = super(AnnouncementSerializer, self).create(validated_data)
        if instance.published:
            instance.publish_datetime == timezone.now()
            return instance

    def update(self,instance,validated_data):
        instance = super(AnnouncementSerializer, self).create(validated_data)
        Announcement.update_datetime == timezone.now()

        if instance.published:
            instance.publish_datetime == timezone.now()
            return instance
        if not instance.published:
            instance.publish_datetime = None
            instance.save()
        return instance


    class Meta:
        model = Announcement
        fields = '__all__'
