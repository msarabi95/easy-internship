from django.contrib import admin

from misc.models import DocumentTemplate


class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ['label', 'codename', 'type', 'template_file']
    list_filter = ['type']

admin.site.register(DocumentTemplate, DocumentTemplateAdmin)