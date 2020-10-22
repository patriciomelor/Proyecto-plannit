from django import forms
import django.forms.widgets
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Paquete


class DocumentoListForm(forms.Form):

    documento = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=True, label="Escoja los documentos a enviar: ")



