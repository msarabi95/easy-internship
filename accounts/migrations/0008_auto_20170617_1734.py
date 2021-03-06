# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-06-17 14:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20170403_0429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intern',
            name='batch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interns', to='accounts.Batch'),
        ),
        migrations.AlterField(
            model_name='intern',
            name='university',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interns', to='accounts.University'),
        ),
    ]
