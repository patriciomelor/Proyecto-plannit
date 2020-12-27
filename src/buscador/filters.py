import django_filters
from django import forms
from .models import Documento
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from bandeja_es.models import Version

class DocFilter(django_filters.FilterSet):
    class Meta:
        model = Documento
        fields = ['Codigo_documento', 'fecha_Emision_B', 'Especialidad']