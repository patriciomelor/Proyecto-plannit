import django_filters
from django import forms
from .models import Documento
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class DocFilter(django_filters.FilterSet): 
    fecha_Emision_B = forms.DateField(widget=forms.TextInput(attrs={'type': 'date','class':'select2'}), input_formats=['%Y-%m-%d'])
    fecha_Emision_0 = forms.DateField(widget=forms.TextInput(attrs={'type': 'date','class':'select2'}), input_formats=['%Y-%m-%d'])
    
    Especialidad = forms.ChoiceField(widget=forms.Select(attrs={'class':'select2'}))

    class Meta:
        model=Documento
        fields = ['Especialidad', 'Descripcion', 'Codigo_documento','Tipo_Documento','Numero_documento_interno','fecha_Emision_B','fecha_Emision_0']

   