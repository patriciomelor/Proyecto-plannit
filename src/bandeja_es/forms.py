from django import forms
import django.forms.widgets
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Paquete
from multiupload.fields import MultiFileField, MultiMediaField, MultiImageField

class DocumentoListForm(forms.Form):
    documento = forms.MultipleChoiceField(required=False, label="Escoja los documentos a enviar: ")
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    # documento = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False, label="Escoja los documentos a enviar: ")

class CreatePaqueteForm(forms.ModelForm):
    class Meta:
        model = Paquete
        fields = ['nombre', 'asunto', 'periodo', 'destinatario']

