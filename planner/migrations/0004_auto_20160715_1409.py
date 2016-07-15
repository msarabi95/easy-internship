# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-15 14:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0003_rotationrequest_delete'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rotationrequest',
            options={'ordering': ('plan_request', 'month')},
        ),
        migrations.AlterModelOptions(
            name='specialty',
            options={'verbose_name_plural': 'Specialties'},
        ),
        migrations.RemoveField(
            model_name='rotationrequestforward',
            name='id',
        ),
        migrations.AddField(
            model_name='rotationrequestforward',
            name='key',
            field=models.CharField(default='', max_length=20, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
