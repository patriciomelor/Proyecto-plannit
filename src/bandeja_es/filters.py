import django_filters
from .models import Paquete, PaqueteDocumento, Borrador, BorradorDocumento

from django.http import JsonResponse

class PaqueteFilter(django_filters.FilterSet):
    class Meta:
        model = Paquete
        fields = ['id', 'owner', 'fecha_creacion']

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Paquete.objects.filter(name__icontains=request.POST['term'])[0:20]:
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

class PaqueteDocumentoFilter(django_filters.FilterSet):
    class Meta:
        model = PaqueteDocumento
        fields = '__all__'
    
    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in PaqueteDocumento.objects.filter(name__icontains=request.POST['term'])[0:20]:
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

class BorradorFilter(django_filters.FilterSet):
    class Meta:
        model = Borrador
        fields = ['nombre', 'fecha_creacion']

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Borrador.objects.filter(name__icontains=request.POST['term'])[0:20]:
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

class BorradorDocumentoFilter(django_filters.FilterSet):
    class Meta:
        model = BorradorDocumento
        fields = '__all__'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in BorradorDocumento.objects.filter(name__icontains=request.POST['term'])[0:20]:
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)