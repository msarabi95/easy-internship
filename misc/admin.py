from django.contrib import admin

from misc.models import DocumentTemplate, Announcements


class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ['label', 'codename', 'type', 'template_file']
    list_filter = ['type']

class AnnouncementsAdmin(admin.ModelAdmin):
    list_display = ['Text']

admin.site.register(DocumentTemplate, DocumentTemplateAdmin)
admin.site.register(Announcements, AnnouncementsAdmin)