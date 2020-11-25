from django import forms
from django.forms import BaseFormSet
from django.forms import (formset_factory, modelformset_factory)
import django.forms.widgets
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Paquete, Version, Borrador
from panel_carga.models import Documento
from multiupload.fields import MultiFileField, MultiMediaField, MultiImageField
from django.contrib.auth.models import User


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

class CreatePaqueteForm(forms.ModelForm):
    descripcion = forms.CharField(widget=forms.Textarea, max_length=500)
    class Meta:
        model = Paquete
        fields = ['destinatario', 'asunto']
class VersionDocForm(forms.ModelForm):
    class Meta:
        model = Version
        fields = ['documento_fk', 'revision', 'archivo', 'comentario', 'estado_cliente', 'estado_contratista']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['documento_fk'].queryset = Documento.objects.none()
        
VersionFormset = formset_factory(VersionDocForm, extra=1)
# VersionFormset = modelformset_factory(
#     Version,
#     fields = [ 'documento_fk','revision', 'archivo', 'comentario', 'estado_cliente', 'estado_contratista'],
#     extra=1,
# )

class PaqueteBorradorForm(forms.ModelForm):
    class Meta:
        model = Borrador
        fields = ['descripcion', 'destinatario', 'asunto']

# class VersionDocBorrador(forms.ModelForm):
#     class Meta:
