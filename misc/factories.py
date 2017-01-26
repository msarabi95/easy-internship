import factory

from misc.models import DocumentTemplate


class DocumentTemplateFactory(factory.DjangoModelFactory):
    label = factory.Sequence(lambda n: "Document Template %d" % n)
    codename = factory.Sequence(lambda n: "doctemplate%d" % n)
    type = 'docx'
    template_file = factory.django.FileField(filename="doctemplate.docx")

    class Meta:
        model = DocumentTemplate
