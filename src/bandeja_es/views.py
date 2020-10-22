from django.shortcuts import render
from django.shortcuts import render
from django.urls import (reverse_lazy, reverse)
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin

from .models import Documento, Paquete, PaqueteDocumento
from .forms import DocumentoListForm
# Create your views here.

class IndexView(ProyectoMixin, TemplateView):
    template_name = 'bandeja_es/baes.html'


def cargar_documentos(request, pk):
    context = {}
    if request.method == 'POST':
        form = DocumentoListForm(request.POST or None)
        if form.is_valid():
            docs = request.POST.getlist('documento')
            cant_docs = len(docs)
            package = Paquete.objects.get(pk=pk)
            for documento in docs:
                doc_seleccionado = Documento.objects.get(pk=documento[0])
                package.documento.add(doc_seleccionado, through_defaults={'cantidad': cant_docs})
            return HttpResponseRedirect(reverse_lazy('Bandejaeys'))
    else:
        form = DocumentoListForm()
        doc = Documento.objects.filter(proyecto=request.session.get('proyecto'))
        documento_opciones = ()
        for documento in doc:
            documento_opciones = documento_opciones + ((documento.pk, documento.nombre) ,)
        form.fields['documento'].choices = documento_opciones
        context['form'] = form

    return render(request, 'bandeja_es/carga-documentos.html', context)

class CreatePaquete(ProyectoMixin, CreateView):
    model = Paquete
    template_name = 'bandeja_es/create-paquete.html'
    fields = ['nombre', 'asunto', 'periodo']
    pk_url_kwarg = 'pk'


    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self, **kwargs):
        return reverse('cargar-documentos', kwargs={'pk': self.pk_url_kwarg})

