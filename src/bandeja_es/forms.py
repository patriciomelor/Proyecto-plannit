from django import forms
from django.forms import (formset_factory, modelformset_factory)
import django.forms.widgets
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Paquete, Version
from multiupload.fields import MultiFileField, MultiMediaField, MultiImageField

# class DocumentoListForm(forms.Form):
#     documento = forms.MultipleChoiceField(required=False, label="Escoja los documentos a enviar: ")
#     file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label="Adjunte archivo al los documentos: ")
#     # documento = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False, label="Escoja los documentos a enviar: ")

class CreatePaqueteForm(forms.ModelForm):
    documento = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'class': "form-check-input"}), required=False, label="Escoja los documentos a enviar: ")

    class Meta:
        model = Paquete
        fields = ['destinatario', 'asunto', 'descripcion']

    def __init__(self, *args, **kwargs):
        self.documento = kwargs.pop('documento', None)
        super(CreatePaqueteForm, self).__init__(*args, **kwargs)
        self.fields['documento'].choices = self.documento

VersionFormset = modelformset_factory(
    Version,
    fields=('document_version','comentario','archivo', 'revision', 'estado_cliente', 'estado_contratista'),
    extra=1,
)