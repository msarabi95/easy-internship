# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-30 04:06
from __future__ import unicode_literals

from django.db import migrations


def forwards_func(apps, schema_editor):

    # We are basically transferring relationships from being stored in `department` ForeignKeys
    # into being stored in a set of `hospital`, `specialty`, and `location` ForeignKeys

    # In the process, we're also moving department contact details, memo specifications, and special requirements
    # to a dedicated `CustomDepartmentDetail` model

    # This basically, will free us from the necessity of the `Department` model all together

    ################
    Department = apps.get_model('hospitals', 'Department')
    Hospital = apps.get_model('hospitals', 'Hospital')
    Specialty = apps.get_model('hospitals', 'Specialty')
    Location = apps.get_model('hospitals', 'Location')
    CustomDepartmentDetail = apps.get_model('hospitals', 'CustomDepartmentDetail')
    
    DepartmentSettings = apps.get_model('hospitals', 'DepartmentSettings')
    DepartmentMonthSettings = apps.get_model('hospitals', 'DepartmentMonthSettings')
    
    Rotation = apps.get_model('rotations', 'Rotation')
    RotationRequest = apps.get_model('rotations', 'RotationRequest')

    # First, we'll need to create `Location` instances for departments with multiple locations
    # We'll go over each hospital-specialty combination and create location instances for combinations that
    # return multiple `Department`s
    
    location_dict = dict()  # Create a dictionary that maps departments to locations, for reference in later parts
    
    for hospital in Hospital.objects.all():
        for specialty in Specialty.objects.all():
            departments = Department.objects.filter(hospital=hospital, specialty=specialty)
            if departments.count() > 1:
                for department in departments:
                    location = Location.objects.create(
                        hospital=department.hospital,
                        specialty=department.specialty,
                        name=department.name,
                    )
                    location_dict[department] = location

    # Next we'll create `CustomDepartmentDetail` instances for all KAMC departments that require memos,
    # moving the specification of the memo settings as well as their contact details
    kamc_memo_depts = Department.objects.filter(hospital__is_kamc=True, requires_memo=True)
    for department in kamc_memo_depts:
        CustomDepartmentDetail.objects.create(
            hospital=department.hospital,
            specialty=department.specialty,
            location=location_dict[department] if department in location_dict else None,
            # Use the `location_dict` previously created
            contact_name=department.contact_name,
            contact_position=department.contact_position,
            email=department.email,
            phone=department.phone,
            extension=department.extension,
            requires_memo=department.requires_memo,
            memo_handed_by_intern=department.memo_handed_by_intern,
            has_requirement=department.has_requirement,
            requirement_description=department.requirement_description,
            requirement_file=department.requirement_file,
        )

    # We'll also specify that KAMC hospitals require no memo by default
    Hospital.objects.filter(is_kamc=True).update(requires_memo=False)

    # Finally, we'll go over each of the ForeignKeys to `Department` and transfer the info to the
    # `hospital`, `specialty`, and `location` ForeignKeys
    for ds in DepartmentSettings.objects.all():
        ds.hospital = ds.department.hospital
        ds.specialty = ds.department.specialty
        ds.location = location_dict[ds.department] if ds.department in location_dict else None
        ds.save()
        
    for dms in DepartmentMonthSettings.objects.all():
        dms.hospital = dms.department.hospital
        dms.specialty = dms.department.specialty
        dms.location = location_dict[dms.department] if dms.department in location_dict else None
        dms.save()
        
    for r in Rotation.objects.all():
        r.hospital = r.department.hospital
        # r.specialty = r.department.specialty
        r.location = location_dict[r.department] if r.department in location_dict else None
        r.save()
        
    for rr in RotationRequest.objects.all():
        rr.hospital = rr.requested_department.department.hospital
        # rr.specialty = rr.requested_department.department.specialty
        rr.location = location_dict[rr.requested_department.department] if rr.requested_department.department in location_dict else None
        rr.save()


def reverse_func(apps, schema_editor):

    # In the reverse function, we'll restore data from the `hospital`, `specialty`, and `location` fields
    # into `department`

    # In the process we'll also transfer department info from hospital info as well as `CustomDepartmentDetail`s

    ##########

    Department = apps.get_model('hospitals', 'Department')
    Hospital = apps.get_model('hospitals', 'Hospital')
    Specialty = apps.get_model('hospitals', 'Specialty')
    Location = apps.get_model('hospitals', 'Location')
    CustomDepartmentDetail = apps.get_model('hospitals', 'CustomDepartmentDetail')

    DepartmentSettings = apps.get_model('hospitals', 'DepartmentSettings')
    DepartmentMonthSettings = apps.get_model('hospitals', 'DepartmentMonthSettings')
    
    Rotation = apps.get_model('rotations', 'Rotation')
    RequestedDepartment = apps.get_model('rotations', 'RequestedDepartment')
    RotationRequest = apps.get_model('rotations', 'RotationRequest')
    
    # First, we create department instances from the existing hospital, specialty, and location data
    # If applicable, we get its data from `CustomDepartmentDetail`
    
    def create_department(hospital, specialty, location=None):
        custom_detail = CustomDepartmentDetail.objects.filter(hospital=hospital, specialty=specialty, location=location)
        detail = custom_detail.first() if custom_detail.exists() else hospital
        
        department_name = "Department of %s" % specialty
        if location:
            department_name += " - %s" % location.name
            
        department = Department.objects.create(
            hospital=hospital,
            specialty=specialty,
            name=department_name,
            contact_name=detail.contact_name,
            contact_position=detail.contact_position,
            email=detail.email,
            phone=detail.phone,
            extension=detail.extension,
            requires_memo=detail.requires_memo,
            memo_handed_by_intern=detail.memo_handed_by_intern,
            has_requirement=detail.has_requirement,
            requirement_description=detail.requirement_description,
            requirement_file=detail.requirement_file,
        )
        
        return department
    
    location_dict = dict()  # Create a dictionary to map departments to locations; this will be used later on
    
    for hospital in Hospital.objects.all():
        for specialty in Specialty.objects.all():
            locations = Location.objects.filter(hospital=hospital, specialty=specialty)
            if locations.exists():
                for location in locations:
                    department = create_department(hospital, specialty, location)
                    location_dict[location] = department
            else:
                create_department(hospital, specialty)
                
    # Next, we'll go over the ForeignKeys to `hospital`, `specialty`, and `location`, and transfer them
    # to `Department`
    for ds in DepartmentSettings.objects.all():
        departments = Department.objects.filter(hospital=ds.hospital, specialty=ds.specialty)
        ds.department = departments.first() if departments.count() == 1 else location_dict[ds.location]
    
    for dms in DepartmentMonthSettings.objects.all():
        departments = Department.objects.filter(hospital=dms.hospital, specialty=dms.specialty)
        dms.department = departments.first() if departments.count() == 1 else location_dict[dms.location]
        
    for r in Rotation.objects.all():
        departments = Department.objects.filter(hospital=r.hospital, specialty=r.specialty)
        r.department = departments.first() if departments.count() == 1 else location_dict[r.location]
        
    for rr in RotationRequest.objects.all():
        departments = Department.objects.filter(hospital=rr.hospital, specialty=rr.specialty)
        rd = RequestedDepartment(
            is_in_database=True,
            department=departments.first() if departments.count() == 1 else location_dict[rr.location],
        )
        rd.save()
        rr.requested_department = rd
        rr.save()


class Migration(migrations.Migration):

    dependencies = [
        ('hospitals', '0008_location_abbreviation'),
        ('rotations', '0006_auto_20170130_0703'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
            reverse_func,
        )
    ]