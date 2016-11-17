# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-16 21:30
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import month.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('planner', '0019_auto_20161117_0030'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Leave',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', month.models.MonthField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('intern', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leaves', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LeaveCancelRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission_datetime', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='LeaveCancelRequestResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_approved', models.BooleanField()),
                ('comments', models.TextField()),
                ('response_datetime', models.DateTimeField(auto_now_add=True)),
                ('request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='response', to='leaves.LeaveCancelRequest')),
            ],
        ),
        migrations.CreateModel(
            name='LeaveRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', month.models.MonthField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('submission_datetime', models.DateTimeField(auto_now_add=True)),
                ('intern', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_requests', to=settings.AUTH_USER_MODEL)),
                ('rotation_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_requests', to='planner.RotationRequest')),
            ],
        ),
        migrations.CreateModel(
            name='LeaveRequestResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_approved', models.BooleanField()),
                ('comments', models.TextField()),
                ('response_datetime', models.DateTimeField(auto_now_add=True)),
                ('request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='response', to='leaves.LeaveRequest')),
            ],
        ),
        migrations.CreateModel(
            name='LeaveSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_days', models.PositiveIntegerField()),
                ('intern', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LeaveType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codename', models.CharField(max_length=16)),
                ('name', models.CharField(max_length=32)),
                ('max_days', models.PositiveIntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='leavesetting',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_settings', to='leaves.LeaveType'),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_requests', to='leaves.LeaveType'),
        ),
        migrations.AddField(
            model_name='leavecancelrequest',
            name='original_request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cancel_requests', to='leaves.LeaveRequest'),
        ),
        migrations.AddField(
            model_name='leavecancelrequest',
            name='rotation_request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='leave_cancel_requests', to='planner.RotationRequest'),
        ),
        migrations.AddField(
            model_name='leave',
            name='request',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='leave', to='leaves.LeaveRequest'),
        ),
        migrations.AddField(
            model_name='leave',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leaves', to='leaves.LeaveType'),
        ),
    ]
