from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from django.views.generic.base import TemplateView, RedirectView, View

from django.urls import reverse_lazy
from .models import Proyecto, Documento
from .forms import ProyectoForm, DocumentoForm, ProyectoSelectForm
from tools.views import ProyectoSeleccionadoMixin
# Create your views here.

class ProyectoSelectView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    success_message = 'Bienvenido!'
    success_url = reverse_lazy('index')
    template_name = 'panel_carga/list-proyecto.html'
    form_class = ProyectoSelectForm
    model = Proyecto

    def form_valid(self, form):
        self.request.session['proyecto'] = form.cleaned_data['proyectos'].pk
        return super().form_valid(form)

class ProyectoMixin(SuccessMessageMixin, ProyectoSeleccionadoMixin):
    model = Proyecto

class ProyectoList(ListView):
    queryset = Proyecto.objects.all()
    template_name = 'panel_carga/list-proyecto.html'
    context_object_name = 'proyectos'

class CreateProyecto(ProyectoMixin, CreateView):
    form_class = ProyectoForm
    template_name = 'panel_carga/create-proyecto.html'
    success_url = reverse_lazy("index")

class DetailProyecto(ProyectoMixin, DetailView):
    model = Proyecto
    template_name = 'panel_carga/detail-proyecto.html'

class DocumentoList(ProyectoMixin, ListView):
    model = Documento
    context_object_name = 'documentos'
    template_name='administrador/PaneldeCarga/pdc.html'

class CreateDocumento(CreateView):
    form_class = DocumentoForm
    template_name = 'panel_carga/create-documento.html'
    success_url = reverse_lazy("index")

class DetailDocumento(DetailView):
    model = Documento
    template_name = 'panel_carga/detail-docuemnto.html'