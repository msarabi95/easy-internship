# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-01 05:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0007_auto_20160901_0519'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rotationrequest',
            options={'ordering': ('internship', 'month')},
        ),
        migrations.AddField(
            model_name='rotationrequest',
            name='internship',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='rotation_requests', to='planner.Internship'),
            preserve_default=False,
        ),
    ]
