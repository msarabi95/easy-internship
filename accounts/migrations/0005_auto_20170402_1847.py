# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-04-02 15:47
from __future__ import unicode_literals

from django.db import migrations
from month import Month


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    University = apps.get_model("accounts", "University")
    Batch = apps.get_model("accounts", "Batch")
    db_alias = schema_editor.connection.alias
    University.objects.using(db_alias).bulk_create([
        University(
            name="King Saud bin Abdulaziz University for Health Sciences",
            abbreviation="KSAU-HS",
            city="Riyadh",
            country="Saudi Arabia",
            is_ksauhs=True,
            is_agu=False,
        ),
        University(
            name="Arabian Gulf University",
            abbreviation="AGU",
            city="Manama",
            country="Bahrain",
            is_ksauhs=False,
            is_agu=True,
        ),
        University(
            name="King Saud University",
            abbreviation="KSU",
            city="Riyadh",
            country="Saudi Arabia",
            is_ksauhs=False,
            is_agu=False,
        )
    ])

    Batch.objects.using(db_alias).bulk_create([
        Batch(
            name="Batch 10",
            abbreviation="B10",
            is_ksauhs=True,
            is_agu=False,
            start_month=Month(2017, 7),
        ),
        Batch(
            name="AGU Batch of 2017-2018",
            abbreviation="AGU-17-18",
            is_ksauhs=False,
            is_agu=True,
            start_month=Month(2017, 7),
        ),
        Batch(
            name="Outside Batch of 2017-2018",
            abbreviation="Out-17-18",
            is_ksauhs=False,
            is_agu=False,
            start_month=Month(2017, 7),
        )
    ])


def reverse_func(apps, schema_editor):
    # forwards_func() creates 3 University and 3 Batch instances,
    # so reverse_func() should delete them.
    University = apps.get_model("accounts", "University")
    Batch = apps.get_model("accounts", "Batch")
    db_alias = schema_editor.connection.alias
    University.objects.using(db_alias).filter(abbreviation="KSAU-HS").delete()
    University.objects.using(db_alias).filter(abbreviation="AGU").delete()
    University.objects.using(db_alias).filter(abbreviation="KSU").delete()

    Batch.objects.using(db_alias).filter(abbreviation="B10").delete()
    Batch.objects.using(db_alias).filter(abbreviation="AGU-17-18").delete()
    Batch.objects.using(db_alias).filter(abbreviation="Out-17-18").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_batch_university'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
            reverse_func,
        )
    ]
