import django_filters
from django import forms
from .models import Paquete, PaqueteDocumento, BorradorPaquete

from django.http import JsonResponse

class PaqueteFilter(django_filters.FilterSet):
    fecha_creacion = django_filters.DateFilter(
        lookup_expr='icontains',
        label= 'Fecha de Creación:',
        widget=forms.DateInput(attrs={
            'type': 'date'
        })
    )
    owner = django_filters.ModelChoiceFilter(
        lookup_expr='icontains',
        label = 'Autor:',
        widget=forms.TextInput(
            attrs={
                'name':'#ordenName', 
                'id':'ordenName'
                }
            ), 
        ),

    id = django_filters.NumberFilter(
        lookup_expr='icontains',
        label='Numero de Tramital:',
        widget=forms.TextInput(
            attrs={
                'name':'#ordenName2',
                'id':'ordenName2',
                }
            ), 
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
            'type': 'date',

        })
    )
    class Meta:
        model = BorradorPaquete
        fields = ['fecha_creacion']

