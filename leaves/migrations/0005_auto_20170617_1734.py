# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-06-17 14:34
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('leaves', '0004_auto_20170615_1317'),
    ]

    operations = [
        migrations.AddField(
            model_name='leave',
            name='return_date',
            field=models.DateField(default=datetime.datetime(2017, 6, 17, 14, 34, 13, 246165, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='return_date',
            field=models.DateField(default=datetime.datetime(2017, 6, 17, 14, 34, 24, 955051, tzinfo=utc)),
            preserve_default=False,
        ),
    ]