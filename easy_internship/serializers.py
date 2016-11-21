from month import Month
from rest_framework import serializers


class MonthField(serializers.Field):
    """
    Month objects are serialized into month id' notation.
    """
    def to_representation(self, obj):
        return int(obj)

    def to_internal_value(self, data):
        return Month.from_int(int(data))


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
