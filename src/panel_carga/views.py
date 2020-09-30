from django.shortcuts import render
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from django.views.generic.base import TemplateView, RedirectView, View

from django.urls import reverse_lazy
from .models import Proyecto, Documento
from .forms import ProyectoForm, DocumentoForm

# Create your views here.

class ProyectoList(ListView):
    queryset = Proyecto.objects.all()
    template_name = 'panel_carga/list-proyecto.html'
    context_object_name = 'proyectos'

class CreateProyecto(CreateView):
    form_class = ProyectoForm
    template_name = 'panel_carga/create-proyecto.html'
    success_url = reverse_lazy("index")

class DetailProyecto(DetailView):
    model = Proyecto
    template_name = 'panel_carga/detail-proyecto.html'

class CreateDocumento(CreateView):
    form_class = DocumentoForm
    template_name = 'panel_carga/create-documento.html'
    success_url = reverse_lazy("index")

class DetailDocumento(DetailView):
    model = Documento
    template_name = 'panel_carga/detail-docuemnto.html'