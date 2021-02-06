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
    Especialidad = django_filters.CharFilter(
        widget=forms.TextInput(
            attrs={
                'name':'#ordenName',
                'id':'ordenName',
                'autocomplete':'on'
                }
            )
        )
    Descripcion = django_filters.CharFilter(
        widget=forms.TextInput(
            attrs={
                'name':'#ordenName2',
                'id':'ordenName2',
                'autocomplete':'on'
                }
            )
        )
    Codigo_documento = django_filters.CharFilter(
        widget=forms.TextInput(
            attrs={
                'name':'#ordenName3',
                'id':'ordenName3',
                'autocomplete':'on'
                }
            )
        )
    Tipo_Documento = django_filters.CharFilter(
        label='Codigo documento interno',
        widget=forms.TextInput(
            attrs={
                'name':'#ordenName4',
                'id':'ordenName4',
                'autocomplete':'on'
                }
            )
        )
    Numero_documento_interno = django_filters.CharFilter(
        label='Tipo de documento',
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
    