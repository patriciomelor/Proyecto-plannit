from django.shortcuts import render
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin

# from .models import 
from .forms import DocumentoListForm
# Create your views here.

class IndexView(ProyectoMixin, TemplateView):
    template_name = 'bandeja_es/baes.html'

class CreatePaquete(ProyectoMixin, FormView):
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
        documentos = form.cleaned_data.get('documento')
        print(documentos)
        return super().form_valid(form)
    


