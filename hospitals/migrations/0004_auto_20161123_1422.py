# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-23 11:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospitals', '0003_auto_20161121_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='contact_position',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hospital',
            name='contact_position',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
    ]
