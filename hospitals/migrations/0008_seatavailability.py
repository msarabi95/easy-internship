# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-08-09 11:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hospitals', '0007_auto_20170617_1734'),
    ]

    operations = [
        migrations.CreateModel(
            name='SeatAvailability',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name_plural': 'Seat availabilities',
            },
            bases=('hospitals.departmentmonthsettings',),
        ),
    ]
