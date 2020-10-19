from django.contrib import admin
from import_export import resources
from .models import Documento, Proyecto, Tipo_Documento
from import_export.admin import ImportExportModelAdmin
# Register your models here.


class DocumentoResource(resources.ModelResource):
    class Meta:
        model = Documento

class DocAdmin(ImportExportModelAdmin):
    resource_class = DocumentoResource

admin.site.register(Documento, DocAdmin)
admin.site.register(Proyecto)
admin.site.register(Tipo_Documento)
