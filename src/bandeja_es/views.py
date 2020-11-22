from django.shortcuts import render, redirect
from django.urls import (reverse_lazy, reverse)
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin

from .models import Paquete, PaqueteDocumento, Borrador, BorradorDocumento, Version
from .forms import CreatePaqueteForm, VersionFormset
from .filters import PaqueteFilter, PaqueteDocumentoFilter, BorradorFilter, BorradorDocumentoFilter
from panel_carga.filters import DocFilter
from panel_carga.models import Documento
# Create your views here.

class InBoxView(ProyectoMixin, ListView):
    model = Paquete
    template_name = 'bandeja_es/baes.html'
    context_object_name = 'paquetes'
    paginate_by = 15

    def get_queryset(self):
        pkg =  Paquete.objects.filter(destinatario=self.request.user)
        lista_paquetes_filtrados = PaqueteFilter(self.request.GET, queryset=pkg)
        return  lista_paquetes_filtrados.qs.order_by('-fecha_creacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pkg = Paquete.objects.filter(destinatario=self.request.user)
        context["filter"] = PaqueteFilter(self.request.GET, queryset=self.get_queryset())
        return context
    
class EnviadosView(ProyectoMixin, ListView):
    model = Paquete
    template_name = 'bandeja_es/baes_Enviado.html'
    context_object_name = 'paquetes'
    paginate_by = 10

    def get_queryset(self):
        pkg =  Paquete.objects.filter(owner=self.request.user)
        lista_paquetes_filtrados = PaqueteFilter(self.request.GET, queryset=pkg)
        return  lista_paquetes_filtrados.qs.order_by('-fecha_creacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pkg = Paquete.objects.filter(owner=self.request.user)
        context["filter"] = PaqueteFilter(self.request.GET, queryset=self.get_queryset())
        return context
   
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
        paquete = Paquete.objects.get(pk=self.kwargs['pk'])
        versiones = Version.objects.filter(paquete_fk=paquete)
        context['versiones'] = versiones
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

# class CreatePaqueteView(ProyectoMixin, CreateView):
#     template_name = 'bandeja_es/create-paquete.html'
#     success_url = reverse_lazy('Bandejaeys')
#     form_class = CreatePaqueteForm
    

#     def get_queryset(self):
#         qs =  Documento.objects.filter(proyecto=self.proyecto)
#         lista_documentos_filtrados = DocFilter(self.request.GET, queryset=qs)
#         return  lista_documentos_filtrados.qs
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         doc = Documento.objects.filter(proyecto=self.proyecto)
#         context["filter"] = DocFilter(self.request.GET, queryset=self.get_queryset())
#         return context

#     def get_form_kwargs(self):
#         kwargs = super(CreatePaqueteView, self).get_form_kwargs()
#         doc =  self.get_queryset()
#         documento_opciones = ()
#         for docs in doc:
#             documento_opciones = documento_opciones + ((docs.pk, str(docs.Codigo_documento + " -- " + " -- " + docs.Especialidad)) ,)
#         kwargs['documento'] = documento_opciones
#         return kwargs

#     def form_valid(self, form, **kwargs):
#         package_pk = 0
#         obj = form.save(commit=False)
#         obj.owner = self.request.user
#         obj.save()
#         package_pk = obj.pk
#         docs = self.request.POST.getlist('documento')
#         # files = self.request.FILES.getlist('file_field')
#         package = Paquete.objects.get(pk=package_pk)
#         for documento in docs:
#             doc_seleccionado = Documento.objects.get(pk=documento)
#             package.documento.add(doc_seleccionado)
#         # for file in files:
#         #     doc_seleccionado.archivo = file
#         #     doc_seleccionado.save()
#         return HttpResponseRedirect(reverse_lazy('Bandejaeys'))
    
#     def form_invalid(self, form, **kwargs):
#         pass

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Paquete.objects.filter(name__icontains=request.POST['term'])[0:20]:
                    item = i.toJSON()
                    item['text'] = i.name
                    data.append(item)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

class BorradorList(ProyectoMixin, ListView):
    model = Borrador
    template_name = 'bandeja_es/borrador.html'
    context_object_name = 'borradores'
    paginate_by = 15

    def get_queryset(self):
        qs =  Borrador.objects.filter(owner=self.request.user)
        lista_borradores_filtrados = BorradorFilter(self.request.GET, queryset=qs)
        return  lista_borradores_filtrados.qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        draft = Borrador.objects.filter(owner=self.request.user)
        context["filter"] = BorradorFilter(self.request.GET, queryset=self.get_queryset())
        return context


class BorradorCreate(ProyectoMixin, CreateView):
    model = Borrador
    success_url = reverse_lazy('Bandejaeys')
    pass


class BorradorDetail(ProyectoMixin, DetailView):
    model = Borrador
    context_object_name = 'borrador'
    pass

class BorradorDelete(ProyectoMixin, DeleteView):
    model = Borrador
    success_url = reverse_lazy('Bandejaeys')
    pass

def create_paquete(request):
    context = {}
    if request.method == 'POST':
        package_pk = 0
        documentos_list = []
        form_paraquete = CreatePaqueteForm(request.POST or None)
        formset_version = VersionFormset(request.POST or None, request.FILES or None)
        if form_paraquete.is_valid() and formset_version.is_valid():
            obj = form_paraquete.save(commit=False)
            obj.owner = request.user
            obj.save()
            package_pk = obj.pk
            package = Paquete.objects.get(pk=package_pk)
            for form in formset_version:
                version = form.save(commit=False)
                documento = form.cleaned_data.get('documento_fk')
                package.documento.add(documento)
                version.owner = request.user
                version.paquete_fk = package
                version.save()
        
        return redirect(reverse_lazy('Bandejaeys'))

    else:
        data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '',
        }
        form_paraquete = CreatePaqueteForm()
        formset_version = VersionFormset(data)
        doc = Documento.objects.filter(proyecto=request.session.get('proyecto'))
        documento_opciones = ()
        context['form_paraquete'] = form_paraquete
        context['formset'] = formset_version
        context['documentos'] = doc

    return render(request, 'bandeja_es/create-paquete2.html', context)
    
