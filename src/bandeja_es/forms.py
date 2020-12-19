from django import forms
from django.forms import BaseFormSet
from django.forms import (formset_factory, modelformset_factory)
import django.forms.widgets
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from panel_carga.models import Documento
from multiupload.fields import MultiFileField, MultiMediaField, MultiImageField
from django.contrib.auth.models import User

from .models import Paquete, Version, BorradorPaquete, BorradorVersion, PrevPaquete, PrevVersion
from panel_carga.views import ProyectoMixin

from panel_carga.choices import TYPES_REVISION
from django.contrib.auth.models import User
from panel_carga.models import Documento



# class DocumentoListForm(forms.Form):
#     documento = forms.MultipleChoiceField(required=False, label="Escoja los documentos a enviar: ")
#     file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label="Adjunte archivo al los documentos: ")
#     # documento = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False, label="Escoja los documentos a enviar: ")

class BaseArticleFormSet(BaseFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields["destinatario"] = forms.ModelChoiceField(queryset=User.objects.all())
        form.fields["asunto"] = forms.CharField(max_length=250)
        form.fields["descripcion"] = forms.CharField(widget=forms.Textarea,max_length=500)

# ***********************************
#   formularios para crear paquete y versiones, pronto quedarán inactivos
# ***********************************

class CreatePaqueteForm(forms.ModelForm):
    descripcion = forms.CharField(widget=forms.Textarea, max_length=500)
    class Meta:
        model = Paquete
        fields = ['destinatario', 'asunto']
class VersionDocForm(forms.ModelForm):
    class Meta:
        model = Version
        fields = ['documento_fk', 'revision', 'archivo', 'comentario', 'estado_cliente', 'estado_contratista']

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['documento_fk'].queryset = Documento.objects.none()
        
VersionFormset = formset_factory(VersionDocForm, extra=1)


# ***********************************
#   formularios para crear el BORRADOR del paquete y versiones, con el debido FORMSET
# ***********************************

class PaqueteBorradorForm(forms.ModelForm):
    class Meta:
        model = BorradorPaquete
        fields = ['descripcion', 'destinatario', 'asunto']

class VersionDocBorrador(forms.ModelForm):
    class Meta:
        model = BorradorVersion
        fields = ['documento_fk', 'revision', 'archivo', 'comentario', 'estado_cliente', 'estado_contratista']

BorradorVersionFormset = formset_factory(VersionDocBorrador)

# ***********************************
#formularios para crear la PREVIEW del paquete y versiones, con el debido FORMSET
# ***********************************

class PaquetePreviewForm(forms.ModelForm):
    descripcion = forms.CharField(widget=forms.Textarea, max_length=500)
    class Meta:
        model = PrevPaquete
        fields = ['prev_receptor', 'prev_asunto']
        labels = {
            'prev_receptor': 'Destinatario'
        }
class VersionDocPreview(forms.ModelForm):
    prev_revision = forms.ChoiceField(choices=TYPES_REVISION)
    class Meta:
        model = PrevVersion
        fields = ['prev_documento_fk', 'prev_revision', 'prev_archivo','prev_comentario' ,'prev_estado_cliente', 'prev_estado_contratista']
        labels = {
            'prev_documento_fk': 'Código Documento',
            'prev_archivo' : 'Archivo',
            'prev_comentario' : 'Archivo de Comentario',
            'prev_revision' : 'Revisión'
        }

    
      
PreviewVersionSet = formset_factory(VersionDocPreview)