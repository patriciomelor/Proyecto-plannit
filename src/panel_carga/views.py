import os.path
import datetime
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from django.views.generic.base import TemplateView, RedirectView, View
from import_export import resources
from tablib import Dataset
from django.core.exceptions import FieldError, ValidationError
from django.db import IntegrityError
from django.urls import reverse_lazy
from .models import Proyecto, Documento, Revision, Historial
from .forms import ProyectoForm, DocumentoForm, ProyectoSelectForm, RevisionForm, UploadFileForm
from tools.views import ProyectoSeleccionadoMixin
# Create your views here.

# Document Resources
class DocumentResource(resources.ModelResource):
    class Meta:
        model = Documento
        field = ( 'especialidad','descripcion','num_documento','tipo_doc',  'fecha_inicio_Emision', 'fecha_fin_Emision')
        exclude = ('id', 'emision', 'archivo', 'ultima_edicion', 'owner', 'proyecto')
        import_id_fields = ('id')

# End Document Resources

class ProyectoSelectView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    success_message = "Proyecto seleccionado correctamente"
    template_name = 'panel_carga/list-proyecto.html'
    form_class = ProyectoSelectForm
    model = Proyecto
    success_url = reverse_lazy("index")

    def dispatch(self, request, *args, **kwargs):
        obj = None
        if not Proyecto.objects.filter(encargado=request.user):
            return HttpResponseRedirect(reverse_lazy('proyecto-crear'))
        return super(ProyectoSelectView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.request.session['proyecto'] = form.cleaned_data['proyectos'].id
        return super().form_valid(form)

class ProyectoMixin(SuccessMessageMixin, ProyectoSeleccionadoMixin):
    model = Proyecto

class ListaProyecto(ProyectoMixin, ListView):
    queryset = Proyecto.objects.all()
    template_name = 'panel_carga/list-proyecto.html'
    context_object_name = 'proyectos'

class CreateProyecto(CreateView):
    form_class = ProyectoForm
    template_name = 'panel_carga/create-proyecto.html'
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        form.instance.encargado = self.request.user
        return super().form_valid(form)

class DetailProyecto(ProyectoMixin, DetailView):
    template_name = 'panel_carga/detail-proyecto.html'
    context_object_name = "proyecto"

class CreateDocumento(ProyectoMixin, CreateView):
    model = Documento
    form_class = DocumentoForm
    # fields = ['especialidad', 'descripcion', 'num_documento', 'tipo', 'fecha_inicio_Emision','fecha_fin_Emision', 'archivo']
    template_name = 'panel_carga/create-documento.html'
    success_url = reverse_lazy("index")
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.proyecto = self.proyecto
        return super().form_valid(form)

class DetailDocumento(ProyectoMixin, DetailView):
    model = Documento
    template_name = 'panel_carga/detail-docuemnto.html'

class ListDocumento(ProyectoMixin, ListView):
    model = Documento
    template_name = 'administrador/PaneldeCarga/pdc.html'
    context_object_name = "documentos"
    paginate_by = 15

    def get_queryset(self):
        return Documento.objects.filter(proyecto=self.proyecto)

    def post(self, request, *args, **kwargs):
        documentos_erroneos = []
        dataset = Dataset()
        new_documentos = request.FILES['importfile']
        imported_data = dataset.load(new_documentos.read(), format='xlsx')
        for data in imported_data:
            try:
                documento = Documento(
                    especialidad= data[0],
                    descripcion= data[1],
                    num_documento= data[2],
                    tipo_doc= data[3],
                    fecha_inicio_Emision= data[4],
                    fecha_fin_Emision= data[5],
                    proyecto= self.proyecto,
                    owner= request.user
                )

                documento.save()
            except IntegrityError:
                documentos_erroneos.append(data)
            except ValueError:
                documentos_erroneos.append(data)
            except TypeError:
                documentos_erroneos.append(data)
        return render(request, 'panel_carga/list-error.html', context={'errores': documentos_erroneos})

# funcion de exportación
def export_document(request):
    context = {}
    dataset = DocumentResource().export()
    response  = HttpResponse(dataset.xlsx , content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="documento.xlsx"'
    return response
class DeleteDocumento(ProyectoMixin, DeleteView):
    template_name = 'panel_carga/delete-documento.html'
    model = Documento
    success_url = reverse_lazy('PanelCarga')
    context_object_name = 'documento'
    
class UpdateDocumento(ProyectoMixin, UpdateView):
    model = Documento
    form_class = DocumentoForm
    template_name = 'panel_carga/update-documento.html'
    success_url = reverse_lazy('PanelCarga')
    context_object_name = "documento"

    def form_valid(self, form):
        registro = Historial.objects.create(
            owner= self.request.user,
            fecha= datetime.datetime.now(),
            documento= Documento.objects.get(pk=self.kwargs['pk'])
        )
        return super().form_valid(form)
        
class CreateRevision(ProyectoMixin, CreateView):
    form_class = RevisionForm
    template_name = 'panel_carga/create-revision.html'
    success_url = reverse_lazy("index")



class DocumentoFileUploadView(ProyectoMixin, ListView):
    model = Documento
    template_name = 'panel_carga/list-documento.html'
    context_object_name = "documentos"
    paginate_by = 15

    def get_queryset(self):
        return Documento.objects.filter(proyecto=self.proyecto)

