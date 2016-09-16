from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()
    level = serializers.IntegerField()
    tags = serializers.CharField()
    extra_tags = serializers.CharField()
    level_tag = serializers.CharField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass