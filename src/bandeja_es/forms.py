from django import forms
import django.forms.widgets
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class DocumentoListForm(forms.Form):
    documentos = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, label="Escoja los documentos a enviar: ")