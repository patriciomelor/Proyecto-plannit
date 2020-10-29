from django.shortcuts import render
from django.shortcuts import render
from django.urls import (reverse_lazy, reverse)
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin

from .models import Documento, Paquete, PaqueteDocumento
from .forms import CreatePaqueteForm
# Create your views here.

class InBoxView(ProyectoMixin, ListView):
    model = Paquete
    template_name = 'bandeja_es/baes.html'
    context_object_name = 'paquetes'
    paginate_by = 10

    def get_queryset(self):
        return Paquete.objects.filter(destinatario=self.request.user).order_by('-fecha_creacion')
    
class EnviadosView(ProyectoMixin, ListView):
    model = Paquete
    template_name = 'bandeja_es/baes_Enviado.html'
    context_object_name = 'paquetes'
    paginate_by = 10

    def get_queryset(self):
        return Paquete.objects.filter(owner=self.request.user).order_by('-fecha_creacion')
   
class PapeleraView(ProyectoMixin, ListView):
    model = Paquete
    # template_name = 
    context_object_name = 'paquetes'

class PaqueteDetail(ProyectoMixin, DetailView):
    model = Paquete
    template_name = 'bandeja_es/paquete-detail.html'
    context_object_name = 'paquete'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pakg_doc = PaqueteDocumento.objects.filter(paquete_id=self.kwargs['pk'])
        context["documentos"] = pakg_doc
        return context
    
class PaqueteUpdate(ProyectoMixin, UpdateView):
    model = Paquete
    template_name = 'bandeja_es/paquete-update.html'
    form_class = CreatePaqueteForm
    success_url = reverse_lazy('paquete-detalle')

class PaqueteDelete(ProyectoMixin, DeleteView):
    model = Paquete
    template_name = 'bandeja_es/paquete-delete.html'
    success_url = reverse_lazy('Bandejaeys')
    context_object_name = 'paquete'

class CreatePaqueteView(ProyectoMixin, CreateView):
    template_name = 'bandeja_es/create-paquete.html'
    success_url = reverse_lazy('Bandejaeys')
    form_class = CreatePaqueteForm

    def get_form_kwargs(self):
        kwargs = super(CreatePaqueteView, self).get_form_kwargs()
        doc = Documento.objects.filter(proyecto=self.proyecto)
        documento_opciones = ()
        for docs in doc:
            documento_opciones = documento_opciones + ((docs.pk, docs.Codigo_documento) ,)
        kwargs['documento'] = documento_opciones
        return kwargs

    def form_valid(self, form, **kwargs):
        package_pk = 0
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        package_pk = obj.pk
        docs = self.request.POST.getlist('documento')
        files = self.request.FILES.getlist('file_field')
        package = Paquete.objects.get(pk=package_pk)
        for documento in docs:
            doc_seleccionado = Documento.objects.get(pk=documento)
            package.documento.add(doc_seleccionado)
        for file in files:
            doc_seleccionado.archivo = file
            doc_seleccionado.save()
        return HttpResponseRedirect(reverse_lazy('Bandejaeys'))
    


def create_paquete(request):
    context = {}
    if request.method == 'POST':
        package_pk = 0
        form_paraquete = CreatePaqueteForm(request.POST or None)
        if form_paraquete.is_valid():
            obj = form_paraquete.save(commit=False)
            obj.owner = request.user
            obj.save()
            package_pk = obj.pk
        form_documento = DocumentoListForm(request.POST or None, request.FILES or None)
        docs = request.POST.getlist('documento')
        files = request.FILES.getlist('file_field')
        package = Paquete.objects.get(pk=package_pk)
        for documento in docs:
            doc_seleccionado = Documento.objects.get(pk=documento)
            package.documento.add(doc_seleccionado)
            for file in files:
                doc_seleccionado.archivo = file
        return HttpResponseRedirect(reverse_lazy('Bandejaeys'))

    else:
        form_paraquete = CreatePaqueteForm()
        form_documento = DocumentoListForm()
        
        doc = Documento.objects.filter(proyecto=request.session.get('proyecto'))
        documento_opciones = ()
        for documento in doc:
            documento_opciones = documento_opciones + ((documento.pk, documento.Codigo_documento) ,)
        form_documento.fields['documento'].choices = documento_opciones
    context['form_documento'] = form_documento
    context['form_paraquete'] = form_paraquete

    return render(request, 'bandeja_es/create-paquete.html', context)