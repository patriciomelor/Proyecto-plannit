import os.path
import datetime
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic.edit import FormMixin
from import_export import resources
from tablib import Dataset
from django.core.exceptions import FieldError, ValidationError
from django.db import IntegrityError
from django.urls import reverse_lazy
from .models import Proyecto, Documento, Revision, Historial
from .forms import ProyectoForm, DocumentoForm, ProyectoSelectForm, RevisionForm, UploadFileForm
from .filters import DocFilter
from tools.views import ProyectoSeleccionadoMixin
# Create your views here.

# Document Resources
class DocumentResource(resources.ModelResource):
    class Meta:
        model = Documento
        field = ( 'Especialidad','descripcion','Codigo_documento','Numero_documento_interno','Tipo_Documento', 'fecha_Emision_B', 'fecha_Emision_0')
        exclude = ('id', 'emision', 'archivo', 'ultima_edicion', 'owner', 'proyecto')
        import_id_fields = ('id')

# End Document Resources

class ProyectoSelectView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    success_message = "Proyecto seleccionado correctamente"
    template_name = 'panel_carga/list-proyecto.html'
    form_class = ProyectoSelectForm
    model = Proyecto
    success_url = reverse_lazy("index")


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
    success_url = reverse_lazy("PanelCarga")
    
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
        qs =  Documento.objects.filter(proyecto=self.proyecto)
        lista_documentos_filtrados = DocFilter(self.request.GET, queryset=qs)
        return  lista_documentos_filtrados.qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doc = Documento.objects.filter(proyecto=self.proyecto)
        context["filter"] = DocFilter(self.request.GET, queryset=self.get_queryset())
        return context
    

    def post(self, request, *args, **kwargs):
        documentos_erroneos = []
        dataset = Dataset()
        new_documentos = request.FILES['importfile']
        imported_data = dataset.load(new_documentos.read(), format='xlsx')
        for data in imported_data:
            try:
                documento = Documento(
                    Especialidad= data[0],
                    Descripcion= data[1],
                    Codigo_documento= data[2],
                    Numero_documento_interno= data[3], 
                    Tipo_Documento= data[4],
                    fecha_Emision_B= data[5],
                    fecha_Emision_0= data[6],
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
class DeleteDocumento(ProyectoMixin, ListView):
    template_name = 'panel_carga/delete-lista_documentos.html'
    model = Documento
    success_url = reverse_lazy('PanelCarga')
    context_object_name = 'documentos'

    def get_queryset(self):
        return Documento.objects.filter(proyecto=self.proyecto)
    
    def post(self, request, *args, **kwargs):
        documentos_ids = self.request.POST.getlist('id[]')
        for documento in documentos_ids:
            doc = Documento.objects.get(pk=documento)
            doc.delete()
        return render(request, self.template_name)

def delete_todos_documentos(request):
    if request.method == 'POST':
        doc = Documento.objects.filter(proyecto=request.session.get('proyecto'))
        doc.delete()
        return HttpResponseRedirect(reverse_lazy("PanelCarga"))
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

