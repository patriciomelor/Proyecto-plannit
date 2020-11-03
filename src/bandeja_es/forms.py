from django import forms
import django.forms.widgets
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Paquete
from multiupload.fields import MultiFileField, MultiMediaField, MultiImageField

# class DocumentoListForm(forms.Form):
#     documento = forms.MultipleChoiceField(required=False, label="Escoja los documentos a enviar: ")
#     file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label="Adjunte archivo al los documentos: ")
#     # documento = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False, label="Escoja los documentos a enviar: ")

class CreatePaqueteForm(forms.ModelForm):
    documento = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False, label="Escoja los documentos a enviar: ")
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label="Adjunte archivo al los documentos: ")
    class Meta:
        model = Paquete
        fields = ['destinatario', 'asunto', 'descripcion']

    def __init__(self, *args, **kwargs):
        self.documento = kwargs.pop('documento', None)
        super(CreatePaqueteForm, self).__init__(*args, **kwargs)
        self.fields['documento'].choices = self.documento

