from __future__ import unicode_literals

from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from ckeditor.fields import RichTextField
from misc.managers import AnnouncementManager



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


class Announcement(models.Model):
    author = models.ForeignKey(User )
    last_updated_by= models.ForeignKey(User, null=True, related_name='editor')
    title = models.CharField(max_length=50)
    submission_datetime = models.DateTimeField(auto_now_add=True)
    publish_datetime = models.DateTimeField(auto_now_add=True,null=True)
    update_datetime = models.DateTimeField(auto_now_add=True,null=True)
    text = RichTextField(('contents of announcment'))
    objects = AnnouncementManager()
    is_published = models.BooleanField(default=False)

    # When it's editied save the date and the user
    def save(self,*args, **kwargs):

         if self.id:
            self.updated = timezone.now()
            return super(Announcement, self).save(*args, **kwargs)



    def __unicode__(self):
        return self.title


