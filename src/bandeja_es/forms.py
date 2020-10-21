from django import forms
import django.forms.widgets
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Paquete

class DocumentoListForm(forms.ModelForm):
    documento = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, label="Escoja los documentos a enviar: ")
    class Meta:
        model = Paquete
        fields = ['nombre', 'asunto', 'periodo','documento']