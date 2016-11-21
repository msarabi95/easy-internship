# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-21 04:19
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import month.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('planner', '0026_auto_20161121_0721'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='RequestedDepartment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_in_database', models.BooleanField()),
                ('department_name', models.CharField(blank=True, max_length=128)),
                ('department_contact_name', models.CharField(blank=True, max_length=128)),
                ('department_email', models.EmailField(blank=True, max_length=128)),
                ('department_phone', models.CharField(blank=True, max_length=128, validators=[django.core.validators.RegexValidator('^\\+\\d{12}$', code='invalid_phone_number', message='Phone number should follow the format +966XXXXXXXXX.')])),
                ('department_extension', models.CharField(blank=True, max_length=16, validators=[django.core.validators.RegexValidator('^\\d{3}\\d*$', code='invalid_extension', message='Extension should be at least 3 digits long.')])),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='department_requests', to='hospitals.Department')),
                ('department_hospital', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hospitals.Hospital')),
                ('department_specialty', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hospitals.Specialty')),
            ],
        ),
        migrations.CreateModel(
            name='Rotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', month.models.MonthField()),
                ('is_elective', models.BooleanField(default=False)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rotations', to='hospitals.Department')),
                ('internship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rotations', to='months.Internship')),
            ],
        ),
        migrations.CreateModel(
            name='RotationRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', month.models.MonthField()),
                ('delete', models.BooleanField(default=False)),
                ('is_elective', models.BooleanField(default=False)),
                ('submission_datetime', models.DateTimeField(auto_now_add=True)),
                ('internship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rotation_requests', to='months.Internship')),
                ('requested_department', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='rotations.RequestedDepartment')),
                ('specialty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rotation_requests', to='hospitals.Specialty')),
            ],
            options={
                'ordering': ('internship', 'month'),
            },
        ),
        migrations.CreateModel(
            name='RotationRequestForward',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=20, unique=True)),
                ('forward_datetime', models.DateTimeField(auto_now_add=True)),
                ('rotation_request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='forward', to='rotations.RotationRequest')),
            ],
        ),
        migrations.CreateModel(
            name='RotationRequestForwardResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_approved', models.BooleanField()),
                ('response_memo', models.FileField(upload_to='forward_response_memos')),
                ('comments', models.TextField()),
                ('respondent_name', models.CharField(max_length=128)),
                ('response_datetime', models.DateTimeField(auto_now_add=True)),
                ('forward', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='response', to='rotations.RotationRequestForward')),
            ],
        ),
        migrations.CreateModel(
            name='RotationRequestResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_approved', models.BooleanField()),
                ('comments', models.TextField()),
                ('response_datetime', models.DateTimeField(auto_now_add=True)),
                ('rotation_request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='response', to='rotations.RotationRequest')),
            ],
        ),
        migrations.AddField(
            model_name='rotation',
            name='rotation_request',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='rotations.RotationRequest'),
        ),
        migrations.AddField(
            model_name='rotation',
            name='specialty',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rotations', to='hospitals.Specialty'),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations,
        )
    ]
