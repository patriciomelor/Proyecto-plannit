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

class IndexView(ProyectoMixin, TemplateView):
    template_name = 'bandeja_es/baes.html'


class CreatePaquete(ProyectoMixin, CreateView):
    model = Paquete
    template_name = 'bandeja_es/create-paquete.html'
    fields = ['nombre', 'asunto', 'periodo']
    pk_url_kwarg = 'pk'


    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self, **kwargs):
        return reverse('cargar-documentos', kwargs={'pk': self.object.pk})

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
        form_documento = DocumentoListForm(request.POST or None)
        docs = request.POST.getlist('documento')
        cant_docs = len(docs)
        package = Paquete.objects.get(pk=package_pk)
        for documento in docs:
            doc_seleccionado = Documento.objects.get(pk=documento)
            package.documento.add(doc_seleccionado)
        return HttpResponseRedirect(reverse_lazy('Bandejaeys'))

    else:
        form_paraquete = CreatePaqueteForm()
        form_documento = DocumentoListForm()
        
        doc = Documento.objects.filter(proyecto=request.session.get('proyecto'))
        documento_opciones = ()
        for documento in doc:
            documento_opciones = documento_opciones + ((documento.pk, documento.nombre) ,)
        form_documento.fields['documento'].choices = documento_opciones
    context['form_documento'] = form_documento
    context['form_paraquete'] = form_paraquete

    return render(request, 'bandeja_es/create-paquete.html', context)