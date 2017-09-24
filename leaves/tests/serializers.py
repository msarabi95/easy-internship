from django.test import TestCase
from model_mommy import mommy
from month import Month
from rest_framework import serializers

from leaves.serializers import LeaveCancelRequestSerializer


class TestLeaveCancelRequestSerializer(TestCase):
    def test_validate(self):
        """
        `validate` should prevent creation of more than one
        open cancellation request at the same time.
        """
        leave_request = mommy.make('leaves.LeaveRequest', month=Month(2018, 8))
        serializer1 = LeaveCancelRequestSerializer(data={
            'intern': leave_request.intern.id,
            'month': int(Month(2018, 8)),
            'leave_request': leave_request.id,
        })

        # The first request should be saved without any hassle
        try:
            serializer1.is_valid(raise_exception=True)
            serializer1.save()
        except serializers.ValidationError:
            raise AssertionError("An unexpected assertion error was raised by `LeaveCancelRequestSerializer`.")

        serializer2 = LeaveCancelRequestSerializer(data={
            'intern': leave_request.intern.id,
            'month': int(Month(2018, 8)),
            'leave_request': leave_request.id,
        })

        # The second request is prevented because an open request already exists
        self.assertRaises(serializers.ValidationError, serializer2.is_valid, raise_exception=True)
