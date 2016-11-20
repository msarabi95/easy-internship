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


