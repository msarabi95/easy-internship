from django.test import TestCase
from month import Month

from hospitals.factories import DepartmentFactory
from hospitals.models import DepartmentMonthSettings
from rotations.models import AcceptanceList
from rotations.serializers import AcceptanceListSerializer


class AcceptanceListSerializerTests(TestCase):
    def setUp(self):
        self.d = DepartmentFactory()
        self.m = Month(2017, 2)
        DepartmentMonthSettings.objects.create(
            department=self.d,
            month=self.m,
            total_seats=50,
        )

        self.al = AcceptanceList(department=self.d, month=self.m)

    def test_serializer_save(self):
        als_ = AcceptanceListSerializer(self.al)
        als = AcceptanceListSerializer(data=als_.data, instance=self.al)
        als.is_valid()
        saved_al = als.save()
        self.assertIsInstance(saved_al, AcceptanceList)
        self.assertEqual(saved_al.department, self.d)
        self.assertEqual(saved_al.month, self.m)