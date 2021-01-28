from django import forms
from django.forms import BaseFormSet
from django.forms import (formset_factory, modelformset_factory)
from django.urls import (reverse_lazy, reverse)
from crispy_forms.helper import FormHelper
from django.core.exceptions import ValidationError

from crispy_forms.layout import Submit
from panel_carga.models import Documento
from django.contrib.auth.models import User

from .models import Paquete, Version, PrevPaquete, PrevVersion
from panel_carga.views import ProyectoMixin

from panel_carga.choices import TYPES_REVISION
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
    prev_revision = forms.ChoiceField(choices=TYPES_REVISION, label='Revisión')
    class Meta:
        model = PrevVersion
        fields = ['prev_documento_fk', 'prev_revision', 'prev_archivo','prev_comentario' ,'prev_estado_cliente', 'prev_estado_contratista']
        labels = {
            'prev_documento_fk': 'Código Documento',
            'prev_estado_cliente': 'Estado Cliente',
            'prev_estado_contratista': 'Estado Contratista',
            'prev_archivo' : 'Archivo',
            'prev_comentario' : 'Archivo de Comentario',
        }
        widgets ={
            'prev_documento_fk': forms.Select(attrs={'class': 'select2'})
        }

class PrevVersionForm(forms.ModelForm):
    class Meta:
        model = PrevVersion
        fields = ['prev_documento_fk', 'prev_revision', 'prev_archivo','prev_comentario' ,'prev_estado_cliente', 'prev_estado_contratista']
        labels = {
            'prev_documento_fk': 'Código Documento',
            'prev_estado_cliente': 'Estado Cliente',
            'prev_estado_contratista': 'Estado Contratista',
            'prev_archivo' : 'Archivo',
            'prev_comentario' : 'Archivo de Comentario',
        }
        widgets ={
            'prev_documento_fk': forms.Select(attrs={'class': 'select2'})
        }

    def clean(self):
        cleaned_data = super().clean()
        try:
            doc = cleaned_data.get('prev_documento_fk')
            nombre_documento = doc.Codigo_documento
            nombre_archivo = str(cleaned_data.get('prev_archivo'))
        except AttributeError:
            raise ValidationError('Inconsistencia de Datos en el formulario')
        
        if not verificar_nombre_archivo(nombre_documento, nombre_archivo):
            self.add_error('prev_archivo', 'No coinciden los nombres')
            raise ValidationError('El nombre del Documento seleccionado y el del archivo no coinciden, Por favor verifique los datos.')

# class cualquierwea(VersionDocPreview):        
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args,**kwargs)
#         proyect = kwargs.pop('proyecto')
#         self.fields['prev.documento_fk'].queryset=Documento.objects.filter(proyecto=proyect)
    
      
PreviewVersionSet = formset_factory(VersionDocPreview)

def verificar_nombre_archivo(nombre_documento, nombre_archivo):
    try:
        index = nombre_archivo.index('.')
    except ValueError:
        index = len(nombre_archivo)

    cleaned_name = nombre_archivo[:index]
    extencion = nombre_archivo[index:]

    if nombre_documento == cleaned_name:
        return True
    else:
        return False