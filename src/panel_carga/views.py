import os.path
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from django.views.generic.base import TemplateView, RedirectView, View
from import_export import resources
from tablib import Dataset

from django.urls import reverse_lazy
from .models import Proyecto, Documento
from .forms import ProyectoForm, DocumentoForm, ProyectoSelectForm
from tools.views import ProyectoSeleccionadoMixin
# Create your views here.

# Document Resources
class DocumentResource(resources.ModelResource):
    class Meta:
        model = Documento
        exclude = ('id', 'proyecto', 'emision', 'archivo')

# End Document Resources

class ProyectoSelectView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = 'panel_carga/list-proyecto.html'
    form_class = ProyectoSelectForm
    model = Proyecto

    def form_valid(self, form):
        self.request.session['proyecto'] = form.cleaned_data['proyectos'].pk
        self.nombre_proyecto = form.cleaned_data['proyectos'].pk
        return super().form_valid(form)

class ProyectoMixin(SuccessMessageMixin, ProyectoSeleccionadoMixin):
    model = Proyecto

class ProyectoList(ListView):
    queryset = Proyecto.objects.all()
    template_name = 'panel_carga/list-proyecto.html'
    context_object_name = 'proyectos'

class CreateProyecto(CreateView):
    form_class = ProyectoForm
    template_name = 'panel_carga/create-proyecto.html'
    success_url = reverse_lazy("index")

class DetailProyecto(ProyectoMixin, DetailView):
    model = Proyecto
    template_name = 'panel_carga/detail-proyecto.html'


class CreateDocumento(CreateView):
    form_class = DocumentoForm
    template_name = 'panel_carga/create-documento.html'
    success_url = reverse_lazy("index")

class DetailDocumento(DetailView):
    model = Documento
    template_name = 'panel_carga/detail-docuemnto.html'

class ListDocumento(ListView):
    model = Documento
    template_name = 'panel_carga/list-documento.html'
    context_object_name = "documentos"

def export_document(request):
    context = {}
    dataset = DocumentResource().export()
    response  = HttpResponse(dataset.xlsx , content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="documento.xlsx"'
    return response


def import_document(request):
    context = {}

    if request.method == 'POST':
        document_resource = DocumentResource()
        dataset = Dataset()
        new_documentos = request.FILES['importfile']
        imported_data = dataset.load(new_documentos.read(), format='xlsx')
        result = document_resource.import_data(dataset, dry_run=True)
        print(result.has_errors())
    context['documentos'] = Documento.objects.all()

    return render(request, 'administrador/PaneldeCarga/pdc.html', context)