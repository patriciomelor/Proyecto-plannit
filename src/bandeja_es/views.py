from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin
from panel_carga.models import Documento
from .models import Paquete, PaqueteDocumento
from .forms import DocumentoListForm
# Create your views here.

class IndexView(ProyectoMixin, ListView):
    template_name = 'bandeja_es/baes.html'
    model = Paquete
    context_object_name = 'paquetes'

    def get_queryset(self):
        return Paquete.objects.filter(owner=self.request.user)
    
class CrearPaquete(ProyectoMixin, CreateView):
    model = Paquete
    template_name = 'bandeja_es/create-paquete.html'
    form_class = DocumentoListForm
    success_url = reverse_lazy('Bandejaeys')

    def get(self, request, *args, **kwargs):
        """Handle GET requests: instantiate a blank version of the form."""
        form = DocumentoListForm()
        documentos = Documento.objects.filter(proyecto=self.proyecto)
        documento_opciones = ()
        for documento in documentos:
            documento_opciones = documento_opciones + ((documento.pk, documento.nombre) ,)
        form.fields['documento'].choices = documento_opciones

        return render(request, self.template_name, context={'form': form})

    def form_valid(self, form):

        form.instance.owner = self.request.user
        return super().form_valid(form)
    


        