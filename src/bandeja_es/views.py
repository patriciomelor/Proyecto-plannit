from django.shortcuts import render
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin

from .models import Documento, Paquete, PaqueteDocumento
from .forms import DocumentoListForm
# Create your views here.

class IndexView(ProyectoMixin, TemplateView):
    template_name = 'bandeja_es/baes.html'


def create_paquete(request):
    context = {}
    if request.method == 'POST':
        form = DocumentoListForm(request.POST or None)
        if form.is_valid():
            documentos = request.POST.getlist('documento')
            print(documentos)
    else:
        form = DocumentoListForm()
        doc = Documento.objects.filter(proyecto=request.session.get('proyecto'))
        documento_opciones = ()
        for documento in doc:
            documento_opciones = documento_opciones + ((documento.pk, documento.nombre) ,)
        form.fields['documento'].choices = documento_opciones
        context['form'] = form

    return render(request, 'bandeja_es/create-paquete.html', context)
# class CreatePaquete(ProyectoMixin, FormView):
#     template_name = 'bandeja_es/create-paquete.html'
#     form_class = DocumentoListForm
#     success_url = reverse_lazy('Bandejaeys')

#     def get(self, request, *args, **kwargs):
#         """Handle GET requests: instantiate a blank version of the form."""
#         form = DocumentoListForm()
#         documentos = Documento.objects.filter(proyecto=self.proyecto)
#         documento_opciones = ()
#         for documento in documentos:
#             documento_opciones = documento_opciones + ((documento.pk, documento.nombre) ,)
#         form.fields['documento'].choices = documento_opciones

#         return render(request, self.template_name, context={'form': form})

#     def form_valid(self, form):
#         documentos = form.cleaned_data.getlist('documento')
#         print(documentos)
#         return super().form_valid(form)
    


