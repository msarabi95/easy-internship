# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-12-05 22:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rotations', '0002_requesteddepartment_department_contact_position'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rotationrequest',
            old_name='delete',
            new_name='is_delete',
        ),
    ]
