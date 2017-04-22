# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-04-03 01:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20170402_2052'),
    ]

    operations = [
        migrations.AddField(
            model_name='intern',
            name='batch',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounts.Batch'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='intern',
            name='university',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounts.University'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='intern',
            name='phone_number',
            field=models.CharField(blank=True, max_length=16),
        ),
    ]