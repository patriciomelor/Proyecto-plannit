from django import forms
import django.forms.widgets
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

<<<<<<< HEAD
class DocumentoListForm(forms.ModelForm):
    documento = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=True, label="Escoja los documentos a enviar: ")
    class Meta:
        model = Paquete
        fields = ['nombre', 'asunto', 'periodo','documento']
=======
class DocumentoListForm(forms.Form):
    documentos = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, label="Escoja los documentos a enviar: ")
>>>>>>> c222e321ecda116d30e943758852d53133044014
