import os.path
import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic.edit import FormMixin
from django.core.exceptions import ValidationError
from import_export import resources
from import_export.widgets import DateWidget
from django.contrib import messages
from tablib import Dataset
from django.core.exceptions import FieldError, ValidationError
from django.db import IntegrityError
from django.urls import reverse_lazy
from .models import Proyecto, Documento, Revision, Historial
from .forms import ProyectoForm, DocumentoForm, ProyectoSelectForm, RevisionForm, UploadFileForm
from .filters import DocFilter
from tools.views import ProyectoSeleccionadoMixin
from tools.objects import SuperuserViewMixin, AdminViewMixin, is_superuser_check, is_admin_check

# Create your views here.

# Document Resources
class DocumentResource(resources.ModelResource):
    class Meta:
        model = Documento
        field = ('Especialidad','descripcion','Codigo_documento','Tipo_Documento', 'fecha_Emision_B', 'fecha_Emision_0')
        exclude = ('id', 'emision', 'archivo', 'ultima_edicion', 'owner', 'proyecto', 'Numero_documento_interno')
        import_id_fields = ('id')
        widgets = {
            'fecha_Emision_B': {'format': '%Y-%m-%d'},
            'fecha_Emision_0': {'format': '%Y-%m-%d'},
        }
    def export(self, queryset=None, *args, **kwargs):
        qs = Documento.objects.filter(proyecto=kwargs.pop('proyecto'))
        return super(DocumentResource, self).export(qs, *args, **kwargs)

# End Document Resources

class ProyectoSelectView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    success_message = "Proyecto seleccionado correctamente"
    template_name = 'panel_carga/list-proyecto.html'
    form_class = ProyectoSelectForm
    success_url = reverse_lazy("welcome")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        proyectos = self.request.user.participantes.all()
        kwargs['proyectos'] = proyectos
        return kwargs
        
    def form_valid(self, form):
        self.request.session['proyecto'] = form.cleaned_data['proyectos'].id
        return super().form_valid(form)

class ProyectoMixin(SuccessMessageMixin, ProyectoSeleccionadoMixin):
    model = Proyecto

class ListaProyecto(ProyectoMixin, ListView):
    template_name = 'panel_carga/list-proyecto.html'
    context_object_name = 'proyectos'

    def get_queryset(self):
        grupos = Group.objects.filter(user= self.request.user)
        proyectos = Proyecto.objects.filter(codigo__in=grupos)
        if proyectos: 
            return proyectos
        else:
            return HttpResponseRedirect(reverse_lazy('proyecto-crear'))
        
class CreateProyecto(CreateView, SuperuserViewMixin, AdminViewMixin):
    form_class = ProyectoForm
    template_name = 'panel_carga/create-proyecto.html'
    success_url = reverse_lazy("index")

class DetailProyecto(ProyectoMixin, SuperuserViewMixin, AdminViewMixin, DetailView):
    template_name = 'panel_carga/detail-proyecto.html'
    context_object_name = "proyecto"

class EditProyecto(ProyectoMixin, SuperuserViewMixin, AdminViewMixin, UpdateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'panel_carga/edit-proyecto.html'

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

    def form_invalid(self, form):
        messages.error(self.request, message='Ocurrio un error. Intentelo nuevamente')
        return super().form_invalid(form)

class DetailDocumento(ProyectoMixin, DetailView):
    model = Documento
    template_name = 'panel_carga/detail-docuemnto.html'

class ListDocumento(ProyectoMixin, ListView):
    model = Documento
    template_name = 'administrador/PaneldeCarga/pdc.html'
    context_object_name = "documentos"

    def get_queryset(self):
        qs =  Documento.objects.filter(proyecto=self.proyecto)
        lista_documentos_filtrados = DocFilter(self.request.GET, queryset=qs)
        return  lista_documentos_filtrados.qs.order_by('Codigo_documento')
    
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
            print(type(data),data)
            try:
                if isinstance(data[4], str):
                    fecha_b = data[4]
                else:
                    fecha_b = data[4].strftime("%Y-%m-%d")
                if isinstance(data[5], str):
                    fecha_0 = data[5]
                else:
                    fecha_0 = data[5].strftime("%Y-%m-%d")
                documento = Documento(
                    Especialidad= data[0],
                    Descripcion= data[1],
                    Codigo_documento= data[2],
                    Tipo_Documento= data[3],
                    fecha_Emision_B= fecha_b,
                    fecha_Emision_0= fecha_0,
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
    proyecto = request.session.get('proyecto')
    dataset = DocumentResource().export(proyecto=proyecto)
    response  = HttpResponse(dataset.xlsx , content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Panel_Carga.xlsx"'
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


class DeleteAllDocuments(ProyectoMixin, TemplateView):
    model = Documento
    template_name = 'panel_carga/delete-documento.html'
    
    def get_queryset(self):
        return Documento.objects.filter(proyecto=self.proyecto)
    
    def get(self, request, *args, **kwargs):
        context={}
        cant_registros = len(self.get_queryset())
        context['cantidad'] = cant_registros
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.get_queryset().delete()
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

