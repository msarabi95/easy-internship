# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-22 21:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='intern',
            name='alt_email',
            field=models.EmailField(default='', max_length=254),
            preserve_default=False,
        ),
    ]
