from django.shortcuts import render
from django.shortcuts import render
from django.urls import (reverse_lazy, reverse)
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin

from .models import Documento, Paquete, PaqueteDocumento
from .forms import DocumentoListForm, CreatePaqueteForm
# Create your views here.

class InBoxView(ProyectoMixin, ListView):
    model = Paquete
    template_name = 'bandeja_es/baes.html'
    context_object_name = 'paquetes'
    paginate_by = 5

    def get_queryset(self):
        return Paquete.objects.filter(owner=self.request.user)
    
class EnviadosView(ProyectoMixin, ListView):
    model = Paquete
    template_name = 'bandeja_es/baes_Enviado.html'
    context_object_name = 'paquetes'
class PapeleraView(ProyectoMixin, ListView):
    model = Paquete
    # template_name = 
    context_object_name = 'paquetes'

class PaqueteDetail(ProyectoMixin, DetailView):
    model = Paquete
    template_name = 'bandeja_es/paquete-detail.html'
    context_object_name = 'paquete'

class PaqueteUpdate(ProyectoMixin, UpdateView):
    model = Paquete
    template_name = 'bandeja_es/paquete-update.html'
    form_class = CreatePaqueteForm
    success_url = reverse_lazy('paquete-detalle')

class PaqueteDelete(ProyectoMixin, DeleteView):
    model = Paquete
    template_name = 'bandeja_es/paquete-delete.html'
    success_url = reverse_lazy('Bandejaeys')
    context_object_name = 'paquete'

def create_paquete(request):
    context = {}
    if request.method == 'POST':
        package_pk = 0
        form_paraquete = CreatePaqueteForm(request.POST or None)
        if form_paraquete.is_valid():
            obj = form_paraquete.save(commit=False)
            obj.owner = request.user
            obj.save()
            package_pk = obj.pk
        form_documento = DocumentoListForm(request.POST or None, request.FILES or None)
        docs = request.POST.getlist('documento')
        files = request.FILES.getlist('file_field')
        package = Paquete.objects.get(pk=package_pk)
        for documento in docs:
            doc_seleccionado = Documento.objects.get(pk=documento)
            package.documento.add(doc_seleccionado)
            for file in files:
                doc_seleccionado.archivo = file
        return HttpResponseRedirect(reverse_lazy('Bandejaeys'))

    else:
        form_paraquete = CreatePaqueteForm()
        form_documento = DocumentoListForm()
        
        doc = Documento.objects.filter(proyecto=request.session.get('proyecto'))
        documento_opciones = ()
        for documento in doc:
            documento_opciones = documento_opciones + ((documento.pk, documento.num_documento) ,)
        form_documento.fields['documento'].choices = documento_opciones
    context['form_documento'] = form_documento
    context['form_paraquete'] = form_paraquete

    return render(request, 'bandeja_es/create-paquete.html', context)