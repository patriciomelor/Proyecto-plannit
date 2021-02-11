import django_filters
from django import forms
from panel_carga.models import Documento
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from bandeja_es.models import Version

class DocFilter(django_filters.FilterSet):
    fecha_Emision_0 = django_filters.DateFilter(
        label='Fecha Emision 0', 
        lookup_expr='icontains',
        widget=forms.DateInput(attrs={
            'id': 'datepicker2',
            'type': 'text',
            'class' : 'datepicker2'

        }), input_formats=['%Y-%m-%d'])

    fecha_Emision_B = django_filters.DateFilter(
        lookup_expr='icontains',
        label='Fecha Emision B', 
        widget=forms.DateInput(attrs={
            'id': 'datepicker2',
            'type': 'text',
            'class' : 'datepicker2'

        }), input_formats=['%Y-%m-%d']
    )
    Especialidad = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Especialidad', 
        widget=forms.TextInput(
            attrs={
                'name':'#ordenName',
                'id':'ordenName',
                'autocomplete':'on'
                }
            )
        )
    Descripcion = django_filters.CharFilter(
        lookup_expr='icontains', 
        label='Descripción', 
        widget=forms.TextInput(
            attrs={
                'name':'#ordenName2',
                'id':'ordenName2',
                'autocomplete':'on'
                }
            )
        )
    Codigo_documento = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Codigo Documento', 
        widget=forms.TextInput(
            attrs={
                'name':'#ordenName3',
                'id':'ordenName3',
                'autocomplete':'on'
                }
            )
        )
    Tipo_Documento = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Tipo Documento', 
        widget=forms.TextInput(
            attrs={
                'name':'#ordenName4',
                'id':'ordenName4',
                'autocomplete':'on'
                }
            )
        )
    Numero_documento_interno = django_filters.CharFilter(
        lookup_expr='icontains', 
        label='Numero Interno', 
        widget=forms.TextInput(
            attrs={
                'name':'#ordenName5',
                'id':'ordenName5',
                'autocomplete':'on'
                }
            )
        )

    class Meta:
        model = Documento
        fields = ['Codigo_documento', 'fecha_Emision_B', 'Especialidad','Tipo_Documento','Numero_documento_interno','Descripcion']
    
    def __init__(self, *args, **kwargs):
        super(DocFilter, self).__init__(*args, **kwargs)
        if self.data == {}:
            self.queryset = self.queryset.none()
    