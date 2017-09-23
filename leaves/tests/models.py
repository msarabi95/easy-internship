from django.test import TestCase
from month import Month

from leaves.models import LeaveRequest

from model_mommy import mommy


class TestLeaveRequestQuerySet(TestCase):
    def test_cancelled(self):
        """
        A cancelled leave request represents a leave request that has first been approved then cancelled
        based on a cancellation request by the intern.
        """
        # An open leave request
        self.leave_request1 = mommy.make(
            'leaves.LeaveRequest',
            month=Month(2018, 8),
        )

        # An approved leave request
        self.leave_request2 = mommy.make(
            'leaves.LeaveRequest',
            month=Month(2018, 8),
            response__is_approved=True,
        )

        # An approved leave request with an open cancellation request
        self.leave_request3 = mommy.make(
            'leaves.LeaveRequest',
            month=Month(2018, 8),
            response__is_approved=True,
        )
        self.leave_request3.cancel_requests.add(mommy.make(
            'leaves.LeaveCancelRequest',
            leave_request=self.leave_request3,
            month=Month(2018, 8),
        ))

        # An approved leave request with an approved cancellation request
        self.leave_request4 = mommy.make(
            'leaves.LeaveRequest',
            month=Month(2018, 8),
            response__is_approved=True,
        )
        self.leave_request4.cancel_requests.add(mommy.make(
            'leaves.LeaveCancelRequest',
            leave_request=self.leave_request4,
            month=Month(2018, 8),
            response__is_approved=True,
        ))

        self.assertNotIn(self.leave_request1, LeaveRequest.objects.cancelled())
        self.assertNotIn(self.leave_request2, LeaveRequest.objects.cancelled())
        self.assertNotIn(self.leave_request3, LeaveRequest.objects.cancelled())
        self.assertIn(self.leave_request4, LeaveRequest.objects.cancelled())
