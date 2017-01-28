
from misc.models import Announcements
from rest_framework import serializers
from django.contrib.auth.models import User


class AnnouncementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcements
        author = serializers.ReadOnlyField(source='owner.username')
        fields = (
            'author','Text','submission_date'
        )

        def create(self, validated_data):
            return Announcements.objects.create(**validated_data)

        def update(self, instance, validated_data):
            pass



class UserSerializer(serializers.ModelSerializer):
    announcements = serializers.PrimaryKeyRelatedField(many=True, queryset=Announcements.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'announcements')