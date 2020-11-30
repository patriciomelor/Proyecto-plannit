from django.shortcuts import render, redirect
from django.urls import (reverse_lazy, reverse)
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView)
from panel_carga.views import ProyectoMixin

from .models import Paquete, PaqueteDocumento, Borrador, BorradorDocumento, BorradorVersion, Version, PrevVersion, PrevVersion, PrevPaquete
from .forms import CreatePaqueteForm, VersionFormset, PaqueteBorradorForm, BorradorVersionFormset, PaquetePreviewForm, PreviewVersionFormset
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
    
    def post(self, request, *args, **kwargs):
        form = self.request.POST.get('borrador')
        print(form)
        return redirect(reverse_lazy('Bandejaeys'))

def create_borrador(request):
    borrador_paraquete = PaqueteBorradorForm()
    borrador_version_set = VersionFormset()
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        borrador_paraquete = PaqueteBorradorForm(request.POST or None)
        borrador_version_set = VersionFormset(request.POST or None, request.FILES or None)
        if borrador_paraquete.is_valid() and borrador_version_set.is_valid():
            print(borrador_version_set)
        # package_pk = 0
        # documentos_list = []
        # borrador_paraquete = CreatePaqueteForm(request.POST or None)
        # borrador_version_set = BorradorVersionFormset(request.POST or None, request.FILES or None)
        # if borrador_paraquete.is_valid() and borrador_version_set.is_valid():
        #     obj = form_paraquete.save(commit=False)
        #     obj.owner = request.user
        #     obj.save()
        #     borrador_pk = obj.pk
        #     borrador = Borrador.objects.get(pk=borrador_pk)
        #     for form in borrador_version_set:
        #         version = form.save(commit=False)
        #         documento = form.cleaned_data.get('documento_fk')
        #         package.documento.add(documento)
        #         version.owner = request.user
        #         version.paquete_fk = package
        #         version.save()
    return JsonResponse('Success', safe=False)
class BorradorDetail(ProyectoMixin, DetailView):
    model = Borrador
    context_object_name = 'borrador'
    pass
class BorradorDelete(ProyectoMixin, DeleteView):
    model = Borrador
    success_url = reverse_lazy('Bandejaeys')
    pass

class CreatePaqueteView(ProyectoMixin, TemplateView):
    template_name = 'bandeja_es/create-paquete2.html'
    success_url = reverse_lazy('Bandejaeys')

    def get(self, request, *args, **kwargs):
        context = {}
        paquete_prev = PrevPaquete.objects.get(pk=self.kwargs['paquete'])
        context['paquete'] = paquete_prev
        context['versiones'] = self.kwargs['versiones']
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        paquete_prev = PrevPaquete.objects.get(pk=self.kwargs['paquete'])
        paquete = Paquete(
            asunto = paquete_prev.asunto,
            descripcion = paquete_prev.descripcion,
            destinatario = paquete_prev.destinatario,
            owner = paquete_prev.owner,
        )
        paquete.save()
        versiones = self.kwargs['versiones']
        for version in versiones:
            paquete.documento.add(version)
            vertion = Version(
                owner= version.prev_owner,
                documento_fk= version.prev_documento_fk,
                revision= version.prev_revision,
                estado_cliente= version.prev_estado_cliente,
                estado_contratista= version.prev_estado_contratista,
                paquete_fk= version.prev_paquete_fk
            )


# def create_paquete(request, ):
#     context={}
#     if request.method == 'GET':

#         return

def create_preview(request):
    context = {}
    if request.method == 'POST':
        package_pk = 0
        versiones_list = []
        form_paraquete = PaquetePreviewForm(request.POST or None)
        formset_version = PreviewVersionFormset(request.POST or None, request.FILES or None)
        if form_paraquete.is_valid() and formset_version.is_valid():
            obj = form_paraquete.save(commit=False)
            obj.owner = request.user
            obj.save()
            package_pk = obj.pk
            package = PrevPaquete.objects.get(pk=package_pk)
            for form in formset_version:
                version = form.save(commit=False)
                documento = form.cleaned_data.get('prev_documento_fk')
                versiones_list.append()
                package.documento.add(documento)
                version.owner = request.user
                version.paquete_fk = package
                version.save()
                versiones_list.append(version) #lista de pk's de las versiones del paquete
        
        return redirect('paquete-crear', kwargs={'paquete': package_pk, 'versiones': versiones_list})

    else:
        data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '',
        }
        form_paraquete = PaquetePreviewForm()
        formset_version = PreviewVersionFormset(data)
        doc = Documento.objects.filter(proyecto=request.session.get('proyecto'))
        documento_opciones = ()
        context['form_paraquete'] = form_paraquete
        context['formset'] = formset_version

    return render(request, 'bandeja_es/create-paquete2.html', context)
    
