from django.contrib import admin

from misc.models import DocumentTemplate, Announcement


class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ['label', 'codename', 'type', 'template_file']
    list_filter = ['type']


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['text','title','is_published']

admin.site.register(DocumentTemplate, DocumentTemplateAdmin)
admin.site.register(Announcement, AnnouncementAdmin)