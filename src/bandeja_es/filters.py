import django_filters
from .models import Paquete, PaqueteDocumento, Borrador, BorradorDocumento

class PaqueteFilter(django_filters.FilterSet):
    class Meta:
        model = Paquete
        fields = '__all__'

class PaqueteDocumentoFilter(django_filters.FilterSet):
    class Meta:
        model = PaqueteDocumento
        fields = '__all__'

class BorradorFilter(django_filters.FilterSet):
    class Meta:
        model = Borrador
        fields = '__all__'

class BorradorDocumentoFilter(django_filters.FilterSet):
    class Meta:
        model = BorradorDocumento
        fields = '__all__'