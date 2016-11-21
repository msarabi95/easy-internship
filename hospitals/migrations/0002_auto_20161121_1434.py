# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-21 11:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospitals', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='hospital',
            name='contact_name',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hospital',
            name='email',
            field=models.EmailField(default='', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hospital',
            name='extension',
            field=models.CharField(default='', max_length=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hospital',
            name='phone',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
    ]
