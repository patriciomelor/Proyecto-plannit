import django_filters
from .models import Paquete, PaqueteDocumento, BorradorPaquete, BorradorDocumento

from django.http import JsonResponse

class PaqueteFilter(django_filters.FilterSet):
    class Meta:
        model = Paquete
        fields = ['id', 'owner', 'fecha_creacion']

class PaqueteDocumentoFilter(django_filters.FilterSet):
    class Meta:
        model = PaqueteDocumento
        fields = '__all__'

class BorradorFilter(django_filters.FilterSet):
    class Meta:
        model = BorradorPaquete
        fields = ['fecha_creacion']

class BorradorDocumentoFilter(django_filters.FilterSet):
    class Meta:
        model = BorradorDocumento
        fields = '__all__'
