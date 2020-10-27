import django_filters
from .models import Documento
class DocFilter(django_filters.FilterSet):
    class Meta:
        model = Documento
        fields = ['especialidad', 'descripcion', 'num_documento']