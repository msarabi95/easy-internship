from django.db.models.signals import post_save
from django.dispatch import receiver

from hospitals.models import Hospital, Specialty, Department


@receiver(post_save, sender=Hospital)
def create_departments_for_hospital(sender, instance, created, **kwargs):
    """
    For every newly created `Hospital`, create a `Department` corresponding to each `Specialty`.
    """
    if created:
        departments = list()
        for specialty in Specialty.objects.all():
            departments.append(Department(
                hospital=instance,
                name="Department of %s" % specialty.name,
                specialty=specialty,
                contact_name=instance.contact_name,
                contact_position=instance.contact_position,
                email=instance.email,
                phone=instance.phone,
                extension=instance.extension,
                has_requirement=instance.has_requirement,
                requirement_description=instance.requirement_description,
                requirement_file=instance.requirement_file,
            ))
        
        Department.objects.bulk_create(departments)


@receiver(post_save, sender=Specialty)
def create_departments_for_specialty(sender, instance, created, **kwargs):
    """
    For every newly created `Specialty`, create a corresponding `Department` in each `Hospital`.
    """
    if created:
        departments = list()
        for hospital in Hospital.objects.all():
            departments.append(Department(
                hospital=hospital,
                name="Department of %s" % instance.name,
                specialty=instance,
                contact_name=hospital.contact_name,
                contact_position=hospital.contact_position,
                email=hospital.email,
                phone=hospital.phone,
                extension=hospital.extension,
                has_requirement=hospital.has_requirement,
                requirement_description=hospital.requirement_description,
                requirement_file=hospital.requirement_file,
            ))
        Department.objects.bulk_create(departments)