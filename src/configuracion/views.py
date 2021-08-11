from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic import FormView, CreateView, DeleteView, UpdateView, ListView, DetailView, FormView
from django.views.generic.edit import FormMixin
from panel_carga.views import ProyectoMixin
from django.contrib.auth.models import User, Group, Permission, PermissionsMixin

from status_encargado import forms
from .roles import ROLES
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.conf import settings 
from django.template.loader import render_to_string
from django.core.mail import send_mail 
from panel_carga.models import *
from panel_carga.forms import ProyectoForm
from bandeja_es.models import *
from tools.objects import SuperuserViewMixin, AdminViewMixin, is_superuser_check, is_admin_check

from .models import CausasNoCumplimiento, HistorialUmbrales, NotificacionHU, Perfil, Restricciones, Umbral
from .forms import CrearUsuario, EditUsuario, InvitationForm, NoCumplimientoForm, RestriccionForm, UmbralForm
from invitations.utils import get_invitation_model


class ConfiguracionIndex(ProyectoMixin, TemplateView):
    template_name = 'configuracion/index.html'
    pass 

class UsuarioView(ProyectoMixin, AdminViewMixin, CreateView):
    template_name = "configuracion/create-user.html"
    form_class = CrearUsuario
    success_message = 'Usuario Creado.'
    success_url = reverse_lazy('crear-usuario')
    
    def form_valid(self, form):
        user_pk = form.instance.pk
        user = User.objects.get(pk=user_pk)
        if user.is_superuser == True:
            return super().form_valid(form)
        else:
            rol = form.cleaned_data['rol_usuario']
            company = form.cleaned_data['empresa']
            cargo = form.cleaned_data['cargo_empresa']
            Perfil.objects.create(
                usuario=user,
                rol_usuario=rol,
                empresa=company,
                cargo_empresa=cargo,
                client=True
            )
            
        return super().form_valid(form)

class UsuarioEdit(ProyectoMixin, AdminViewMixin, UpdateView):
    model = User
    template_name = 'configuracion/edit-user.html'
    success_url = reverse_lazy('listar-usuarios')
    form_class = EditUsuario

    def form_valid(self, form):
        rol = form.cleaned_data['rol_usuario']
        company = form.cleaned_data['empresa']
        cargo = form.cleaned_data['cargo_empresa']
        perfil = Perfil.objects.get(usuario=form.instance)
        perfil.rol_usuario = rol
        perfil.empresa = company
        perfil.cargo_empresa = cargo
        perfil.save()
        return super().form_valid(form)
    
class UsuarioLista(ProyectoMixin, AdminViewMixin, ListView):
    model = User
    template_name = 'configuracion/list-user.html'
    context_object_name = 'usuarios'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["codigo_proyecto"] = self.proyecto.codigo
        return context

class UsuarioDelete(ProyectoMixin, AdminViewMixin, DeleteView):
    model = User
    template_name = 'configuracion/delete-user.html'
    success_url = reverse_lazy('listar-usuarios')
    context_object_name = 'usuario'
    
class UsuarioDetail(ProyectoMixin, AdminViewMixin, DetailView):
    model = User
    template_name = 'configuracion/detail-user.html'
    context_object_name = "usuario"

    def get_context_data(self, **kwargs):
        context = {}
        user = self.get_object()
        grupos = user.groups.all()
        print(grupos)
        context["grupos"] = grupos
        return context

# Añade usuarios al proyecto actual seleccionado
class UsuarioAdd(ProyectoMixin, AdminViewMixin, ListView):
    model = User
    template_name = 'configuracion/add-lista_usuario.html'
    success_message = 'Usuarios añadidos correctamente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_list = []
        all_users = User.objects.all()
        current_users = self.proyecto.participantes.all()
        for user in all_users:
            if not user in current_users:
                user_list.append(user)

        context['users'] = user_list
        return context
    
    def post(self, request, *args, **kwargs):
        usuario_ids = self.request.POST.getlist('id[]')
        for usuario in usuario_ids:
            user = User.objects.get(pk=usuario)
            proyecto_add = self.proyecto
            proyecto_add.participantes.add(user)
        return redirect('listar-usuarios')

class UsuarioRemove(ProyectoMixin, SuperuserViewMixin, ListView):
    template_name = 'configuracion/remove-user.html'
    success_message = 'Usuario(s) eliminados del proyecto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_list = []
        all_users = User.objects.all()
        current_users = self.proyecto.participantes.all()
        for user in all_users:
            if user in current_users:
                user_list.append(user)

        context['users'] = user_list
        return context

    def post(self, request, *args, **kwargs):
        usuario_ids = self.request.POST.getlist('id[]')
        for usuario in usuario_ids:
            user = User.objects.get(pk=usuario)
            proyecto_remove = self.proyecto
            proyecto_remove.participantes.remove(user)
        return redirect('listar-usuarios')

class ProyectoList(ProyectoMixin, AdminViewMixin, ListView):
    context_object_name = 'proyectos'
    template_name = 'configuracion/list-proyecto.html'
    queryset = Proyecto.objects.all().order_by('-fecha_inicio')

class ProyectoDetail(ProyectoMixin, AdminViewMixin, DetailView):
    template_name='configuracion/detail-proyecto.html'       
    context_object_name = 'proyecto'

class ProyectoEdit(ProyectoMixin, SuperuserViewMixin, UpdateView):
    template_name = 'configuracion/edit-proyecto.html'
    form_class = ProyectoForm
    success_url = reverse_lazy('lista-proyecto')
    success_message = 'Información del Proyecto Actualizada'

class ProyectoDelete(ProyectoMixin, SuperuserViewMixin, DeleteView):
    template_name = 'configuracion/delete-proyecto.html'
    success_message = 'Proyecto Eliminado'
    success_url = reverse_lazy('lista-proyecto')

    def delete(self, request, *args, **kwargs):
        objeto = self.get_object()
        if objeto == self.proyecto:
            messages.add_message(request, messages.ERROR, 'No se puede eliminar el proyecto seleccionado.')
            return redirect('lista-proyecto')
        else:  
            return super(ProyectoDelete, self).delete(request, *args, **kwargs)

class ProyectoCreate(ProyectoMixin, SuperuserViewMixin, CreateView):
    template_name = 'configuracion/create-proyecto.html'
    success_message = 'Proyecto Creado correctamente'
    success_url = reverse_lazy('lista-proyecto')
    form_class = ProyectoForm

class InvitationView(ProyectoMixin, SuperuserViewMixin, FormView):
    template_name = 'configuracion/invitation_form.html'
    success_message = 'Invitación enviada correctamente'
    success_url = reverse_lazy('listar-usuarios')
    form_class = InvitationForm

    def form_valid(self, form):
        invitation = get_invitation_model()
        response = super().form_valid(form)
        nombre = form.cleaned_data['nombres']
        correo = form.cleaned_data['correo']
        invite = invitation.create(correo, inviter=self.request.user)
        invite.send_invitation(self.request)
        return response 

class UmbralesView(ProyectoMixin, TemplateView):


    ###################################################
    #                                                 #
    #                                                 #
    #   PRIMER GRÁFICO DE ESTADOS DE LOS DOCUMENTOS   #
    #                                                 #
    #                                                 #
    ###################################################

    def get_cambio_revision(self):
        lista_inicial = []
        lista_final = []

        documentos = Documento.objects.filter(proyecto=self.request.session.get('proyecto'))
        

    ###################################################
    #                                                 #
    #                                                 #
    #            METODO PARA EXPLAYAR INFO            #
    #                                                 #
    #                                                 #
    ###################################################

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)

    #     context['lista_final'] = self.reporte_general()
    #     context['lista_final_largo'] = len(self.reporte_total_documentos())
    #     context['lista_final_largo'] = len(self.reporte_general()) 
    #     context['lista_emisiones'] = self.reporte_emisiones()
    #     context['lista_emisiones_largo'] = len(self.reporte_emisiones()) 
    #     context['lista_total_documentos_emitidos'] = self.reporte_total_documentos_emitidos()
    #     context['lista_total_documentos_emitidos_largo'] = len(self.reporte_total_documentos_emitidos()) 
    #     context['lista_total_documentos'] = self.reporte_total_documentos()
    #     context['lista_total_documentos_largo'] = len(self.reporte_total_documentos()) 
    #     context['lista_curva_s_avance_real'] = self.reporte_curva_s_avance_real()
    #     context['lista_curva_s_avance_real_largo'] = len(self.reporte_curva_s_avance_real()) 
    #     context['lista_curva_s_avance_esperado'] = self.reporte_curva_s_avance_esperado()
    #     context['lista_curva_s_avance_esperado_largo'] = len(self.reporte_curva_s_avance_esperado()) 
    #     context['lista_curva_s_fechas'] = self.reporte_curva_s_fechas()
    #     context['lista_curva_s_fechas_largo'] = len(self.reporte_curva_s_fechas()) 
    #     context['tamano_grafico_uno'] = self.valor_eje_x_grafico_uno()
    #     context['espacios_grafico_uno'] = self.espacios_eje_x_grafico_uno()
    #     context['tamano_grafico_tres'] = self.valor_eje_x_grafico_tres()
    #     context['espacios_grafico_tres'] = self.espacios_eje_x_grafico_tres()
    #     context['documentos_atrasados'] = self.documentos_atrasados()
    #     context['proyeccion'] = self.proyeccion()
    #     context['proyeccion_largo'] = len(self.proyeccion()) 


    #     return context

class RestriccionesView(ProyectoMixin,  FormView):
    http_method_names = ['get', 'post']
    form_class = RestriccionForm
    template_name = 'configuracion/add-restriccion.html'
    success_url = reverse_lazy('restriccion')
    success_message = 'Restriccion creada Correctamente.'


    def get_queryset(self):
        qs = Restricciones.objects.filter(proyecto=self.proyecto)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["restricciones"] = self.get_queryset()
        return context

    def form_valid(self, form):
        restriccion = form.save(commit=False)
        restriccion.proyecto = self.proyecto
        restriccion.save()
        return super().form_valid(form)
    
class NoCumplimientoView(ProyectoMixin, FormView):
    http_method_names = ['get', 'post']
    form_class = NoCumplimientoForm
    template_name = 'configuracion/add-no_cumplimiento.html'
    success_url = reverse_lazy('no-cumplimiento')
    success_message = 'Causa de no Cumplimiento creada Correctamente.'

    def get_queryset(self):
        qs = CausasNoCumplimiento.objects.filter(proyecto=self.proyecto)
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["no_cumplimientos"] = self.get_queryset()
        return context

    def form_valid(self, form):
        no_cumplimiento = form.save(commit=False)
        no_cumplimiento.proyecto = self.proyecto
        no_cumplimiento.save()
        return super().form_valid(form)

class RestriccionesEdit(ProyectoMixin, UpdateView):
    template_name = "configuracion/restriccion-edit.html"
    form_class = RestriccionForm
    success_url = reverse_lazy('restriccion')
    success_message = 'Restriccion editada correctamente'
class NoCumplimientoEdit(ProyectoMixin, UpdateView):
    template_name = "configuracion/no_cumplimiento-edit.html"
    form_class = NoCumplimientoForm
    success_url = reverse_lazy('no-cumplimiento')
    success_message = 'Causa de No Cumplimiento editada correctamente'

class RestriccionesDelete(ProyectoMixin, DeleteView):
    template_name = "configuracion/restriccion-delete.html"
    success_url = reverse_lazy('restriccion')
    success_message = 'Restriccion eliminada correctamente'


class NoCumplimientoDelete(ProyectoMixin, DeleteView):
    template_name = "configuracion/no_cumplimiento-delete.html"
    success_url = reverse_lazy('no-cumplimiento')
    success_message = 'Causa de No Cumplimiento eliminada correctamente'

class UmbralIndexList(ProyectoMixin, ListView):
    template_name = 'configuracion/umbral-list.html'
    context_object_name = 'umbrales'

    def get_queryset(self):
        qs = HistorialUmbrales.objects.filter(proyecto=self.proyecto)
        return qs

class UmbralesEdit(ProyectoMixin, UpdateView):
    model = HistorialUmbrales
    form_class = UmbralForm
    template_name = 'configuracion/edit-umbrales.html'
    success_url = reverse_lazy('list-umbrales')
    success_message = 'Umbral editado correctamente'

class UmbralesNotificados(ProyectoMixin, ListView):
    model = NotificacionHU
    template_name = 'configuracion/umbral-notif-list.html'
    context_object_name = 'umbrales_notificados'

    def get_queryset(self):
        umrales = HistorialUmbrales.objects.filter(proyecto=self.proyecto)
        n_hu = NotificacionHU.objects.filter(h_umbral__in=umrales)
        return n_hu

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notif_umbrales = self.get_queryset()
        list_umbral_1 = []
        list_umbral_2 = []
        list_umbral_3 = []
        list_umbral_4 = []
        for notif_umbral in notif_umbrales:
            if notif_umbral.h_umbral.umbral.pk == 1:
                list_umbral_1.append(notif_umbral)
            elif notif_umbral.h_umbral.umbral.pk == 2:
                list_umbral_2.append(notif_umbral)
            elif notif_umbral.h_umbral.umbral.pk == 3:
                list_umbral_3.append(notif_umbral)
            elif notif_umbral.h_umbral.umbral.pk ==4:
                list_umbral_4.append(notif_umbral)
                 
        context["umbral_1"] = list_umbral_1
        context["umbral_2"] = list_umbral_2
        context["umbral_3"] = list_umbral_3
        context["umbral_4"] = list_umbral_4
        return context 
        
class UNDetail(ProyectoMixin, DetailView):
    model = NotificacionHU
    template_name = 'configuracion/umbral-notif-detail.html'
    context_object_name = 'umbral_notificado'


    def get_context_data(self, **kwargs):
        un_obj = self.get_object()
        context = super().get_context_data(**kwargs)

        if un_obj.h_umbral.umbral.pk == 2:
            context["nu_umbral"] = 2
        elif un_obj.h_umbral.umbral.pk == 3:
            context["nu_umbral"] = 3

        return context