# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-16 21:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0018_auto_20161022_0859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rotationrequestforward',
            name='key',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
