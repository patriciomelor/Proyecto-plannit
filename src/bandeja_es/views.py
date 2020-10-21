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

    def post(self, request, *args, **kwargs):
        pass