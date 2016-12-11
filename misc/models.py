from __future__ import unicode_literals

from django.core.validators import RegexValidator
from django.db import models


class DocumentTemplate(models.Model):
    label = models.CharField(max_length=50)
    codename = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                r'^[a-z_]+[a-z0-9_]*$',
                "Please use lowercase letters, numbers, and underscores only. You can't start with a number.",
            )
        ]
    )
    type = models.CharField(max_length=4, choices=(
        ('pdf', 'PDF'),
        ('docx', 'Microsoft Word'),
    ))
    template_file = models.FileField(upload_to='document_templates')
