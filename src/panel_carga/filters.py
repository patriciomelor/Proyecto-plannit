import django_filters
from django import forms
from .models import Documento
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class DocFilter(django_filters.FilterSet): 
    fecha_Emision_B = django_filters.DateFilter(
        lookup_expr='icontains',
        widget=forms.DateInput(attrs={
            'id': 'datepicker',
            'type': 'text',
            'class' : 'datepicker'

        }), input_formats=['%Y-%m-%d'])
    fecha_Emision_0 = django_filters.DateFilter(
        lookup_expr='icontains',
        widget=forms.DateInput(attrs={
            'id': 'datepicker2',
            'type': 'text',
            'class' : 'datepicker2'

        }), input_formats=['%Y-%m-%d'])
    Especialidad = django_filters.CharFilter(widget=forms.TextInput(attrs={'name':'#ordenName','id':'ordenName','autocomplete':'on'}))
    Descripcion = django_filters.CharFilter(widget=forms.TextInput(attrs={'name':'#ordenName2','id':'ordenName2','autocomplete':'on'}))
    Codigo_documento = django_filters.CharFilter(widget=forms.TextInput(attrs={'name':'#ordenName3','id':'ordenName3','autocomplete':'on'}))
    Tipo_Documento = django_filters.CharFilter(widget=forms.TextInput(attrs={'name':'#ordenName4','id':'ordenName4','autocomplete':'on'}))
    Numero_documento_interno = django_filters.CharFilter(widget=forms.TextInput(attrs={'name':'#ordenName5','id':'ordenName5','autocomplete':'on'}))
    class Meta:
        model=Documento
        fields = ['Especialidad', 'Descripcion', 'Codigo_documento','Tipo_Documento','Numero_documento_interno','fecha_Emision_B','fecha_Emision_0']

   