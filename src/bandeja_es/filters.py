import django_filters
from django import forms
from .models import Paquete, PaqueteDocumento, BorradorPaquete

from django.http import JsonResponse

class PaqueteFilter(django_filters.FilterSet):
    fecha_creacion = django_filters.DateFilter(
        lookup_expr='icontains',
        label= 'Fecha de Creación:',
        widget=forms.DateInput(attrs={
            'id': 'datepicker',
            'type': 'text',
            'class' : 'datepicker'

        })
    )
    owner = django_filters.ModelChoiceFilter(
        widget=forms.TextInput(
            attrs={
                'name':'#ordenName', 
                'id':'ordenName',
                }
            ), 
        label='Autor',
        ),
    id = django_filters.NumberFilter(
        widget=forms.TextInput(
            attrs={
                'name':'#ordenName2',
                'id':'ordenName2',
                }
            ), 
        label='Numero de Tramital:',
    )
    class Meta:
        model = Paquete
        fields = ['id', 'owner', 'fecha_creacion']
        labels = {
            'id': 'Número de Tramital:',
            'owner': 'Autor:'
        }

class PaqueteDocumentoFilter(django_filters.FilterSet):
    class Meta:
        model = PaqueteDocumento
        fields = '__all__'

class BorradorFilter(django_filters.FilterSet):
    fecha_creacion = django_filters.DateFilter(
        lookup_expr='icontains',
        widget=forms.DateInput(attrs={
            'id': 'datepicker',
            'type': 'text',
            'class' : 'datepicker'

        })
    )
    class Meta:
        model = BorradorPaquete
        fields = ['fecha_creacion']

