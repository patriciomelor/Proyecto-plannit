import django_filters
from django import forms
from panel_carga.models import Documento
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from bandeja_es.models import Version

class DocFilter(django_filters.FilterSet):
    fecha_Emision_B = django_filters.DateFilter(
        lookup_expr='icontains',
        widget=forms.DateInput(attrs={
            'id': 'datepicker',
            'type': 'text',
            'class' : 'datepicker'

        })
    )
    class Meta:
        model = Documento
        fields = ['Codigo_documento', 'fecha_Emision_B', 'Especialidad','Tipo_Documento','Numero_documento_interno','Descripcion']
    
    def __init__(self, *args, **kwargs):
        super(DocFilter, self).__init__(*args, **kwargs)
        if self.data == {}:
            self.queryset = self.queryset.none()
    