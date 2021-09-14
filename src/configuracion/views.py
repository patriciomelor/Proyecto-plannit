from email.mime import text
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from bandeja_es.models import *
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import (Group, Permission, PermissionsMixin,
                                        User)
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseRedirect, request
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  ListView, UpdateView)
from django.views.generic.base import RedirectView, TemplateView, View
from django.views.generic.edit import FormMixin
from invitations.utils import get_invitation_model
from panel_carga.forms import ProyectoForm
from panel_carga.models import *
from panel_carga.views import ProyectoMixin
from status_encargado import forms
from tools.objects import (AdminViewMixin, SuperuserViewMixin, is_admin_check,
                           is_superuser_check)

from .forms import (CrearUsuario, EditUsuario, InvitationForm,
                    NoCumplimientoForm, RestriccionForm, UmbralForm,
                    EditProfile)
from .models import (CausasNoCumplimiento, HistorialUmbrales, NotificacionHU,
                     Perfil, Restricciones, Umbral)
from .roles import ROLES
from .user_token import token_generator
from notifications.emails import send_email
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.urls import reverse


class ConfiguracionIndex(ProyectoMixin, TemplateView):
    template_name = 'configuracion/index.html'
    pass 

class UsuarioView(ProyectoMixin, AdminViewMixin, CreateView):
    template_name = "configuracion/create-user.html"
    form_class = CrearUsuario
    success_message = 'Usuario Creado.'
    success_url = reverse_lazy('crear-usuario')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user.perfil.rol_usuario
        return kwargs

    def form_valid(self, form):
        usuario = form.save(commit=False)

        if usuario.is_superuser == True:
            usuario.save()
            return super().form_valid(form)
        else:
            usuario.is_active = False
            usuario.save()
            rol = form.cleaned_data['rol_usuario']
            company = form.cleaned_data['empresa']
            cargo = form.cleaned_data['cargo_empresa']

            perfil =Perfil(
                usuario=usuario,
                rol_usuario=rol,
                empresa=company,
                cargo_empresa=cargo,
                client=True
            )
            perfil.save()
            self.proyecto.participantes.add(usuario)

            ######## Creación de Token, captura de sitio y envío de correo a usuario registrado ########
            sitio = get_current_site(self.request).domain
            uidb64 = urlsafe_base64_encode(force_bytes(usuario.pk))
            url = reverse('validate-usuario', kwargs={
                'uidb64': uidb64,
                'token': token_generator.make_token(user=usuario),
            })
            #busqueda rol usuarios
            nuevo_rol = ""
            if rol == 1:
                nuevo_rol = "Administrador Cliente"
            elif rol == 2:
                nuevo_rol = "Revisor Cliente"
            elif rol == 3:
                nuevo_rol = "Vizualizador Cliente"
            elif rol == 4:
                nuevo_rol = "Administrador Contratista"
            elif rol == 5:
                nuevo_rol = "Revisor Contratista"
            elif rol == 6:
                nuevo_rol = "Vizualizador Contratista"

            send_email(
                html = "tools/confirmacion.html",
                context = {
                    "usuario": usuario,
                    "proyecto": self.proyecto,
                    "perfil": perfil,
                    "rol": nuevo_rol,
                    "sitio": sitio,
                    "url": sitio+url,
                },
                subject = "Confirmación de Correo Electrónico",
                recipients= ["{email}".format(email=usuario.email)]
            )

        return super().form_valid(form)

class UserValidation(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            usuario = User.objects.get(pk=id)
            # if usuario.is_active:
            #     return redirect('login')
        except Exception as error:
            messages.error(request, 'Ha ocurrido un error al intentar activar tu cuenta. Porfavor, ponte en contato con tu proveedor para arreglar la situación')
            usuario = None
            return redirect('account_login'+'?message='+'Ha ocurrido un error al intentar activar tu cuenta. Porfavor, ponte en contato con tu proveedor para arreglar la situación')
        
        if usuario is not None and token_generator.check_token(usuario, token):
            usuario.is_active = True
            usuario.save()
            login(request, usuario, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Cuenta activada Exitosamente')
            return redirect('cambiar-contrasena')
        else:
            return redirect('account_login')

class UsuarioEdit(ProyectoMixin, AdminViewMixin, UpdateView):
    model = User
    template_name = 'configuracion/edit-user.html'
    success_url = reverse_lazy('listar-usuarios')
    form_class = EditUsuario

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user.perfil.rol_usuario
        return kwargs

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

    def get_queryset(self):
        rol = self.request.user.perfil.rol_usuario
        if rol == 1:
            qs = self.proyecto.participantes.prefetch_related("perfil").all().filter(perfil__rol_usuario__in=[1,2,3,4,5,6], is_superuser=False, is_active=True).order_by('perfil__empresa')
        elif rol == 4:
            qs = self.proyecto.participantes.prefetch_related("perfil").all().filter(perfil__rol_usuario__in=[4,5,6], is_superuser=False, is_active=True).order_by('perfil__empresa')
        # else:
        #     qs = self.proyecto.participantes.prefetch_related("perfil").exclude(is_superuser=True)
        if self.request.user.is_superuser:
            qs = self.proyecto.participantes.prefetch_related("perfil").all()

        return qs
    
class UsuarioDelete(ProyectoMixin, AdminViewMixin, View):
    model = User
    template_name = 'configuracion/delete-user.html'
    success_message = 'Usuario deshabilitado correctamente.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["usuario"] = User.objects.get(pk=self.kwargs["pk"])
        return context

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs["pk"]
        user = User.objects.get(pk=user_id)
        user.is_active = False
        user.save()
        return redirect('listar-usuarios')
    
class UsuarioDetail(ProyectoMixin, UpdateView):
    model = User
    form_class = EditProfile
    template_name = 'configuracion/perfil.html'
    success_url = reverse_lazy('listar-usuarios')
    success_message = "Datos Actualizados correctamente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["usuario"] = User.objects.get(pk=self.kwargs["pk"])
        return context

class PrimeraContrasenaView(LoginRequiredMixin, auth_views.PasswordChangeView):
    form_class = SetPasswordForm
    template_name='configuracion/password_change.html'
    success_message = "Contraseña actualizada correctamente"
    success_url = reverse_lazy('account_login')

# Añade usuarios al proyecto actual seleccionado
class UsuarioAdd(ProyectoMixin, AdminViewMixin, ListView):
    model = User
    template_name = 'configuracion/add-lista_usuario.html'
    success_message = 'Usuarios añadidos correctamente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_list = []
        all_users = User.objects.all()
        current_users = self.proyecto.participantes.prefetch_related("perfil").all()
        for user in all_users:
            if user.is_superuser:
                pass
            else:
                if not user in current_users:
                    user_list.append(user)

        context['users'] = user_list
        return context
    
    def post(self, request, *args, **kwargs):
        usuario_ids = self.request.POST.getlist('user')
        if usuario_ids:
            for usuario in usuario_ids:
                user = User.objects.get(pk=usuario)
                proyecto_add = self.proyecto
                proyecto_add.participantes.add(user)
            messages.success(self.request, "Usuarios añadidos correctamente al proyecto")

            return redirect('listar-usuarios')
        else:
            messages.info(self.request, "No se ha seleccionado ningun usuario. Intente otra vez.")
            return redirect('add-user-proyecto')

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

class ProyectoEdit(ProyectoMixin, UpdateView):
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

    def form_valid(self, form):
        proyecto = form.save(commit=False)
        thresholds = Umbral.objects.all()
        superusers = User.objects.filter(is_superuser=True)
        proyecto.save()
        proyecto.participantes.add(proyecto.encargado)
        proyecto.participantes.add(*superusers)

        for umbral in thresholds:
            HistorialUmbrales.objects.create(
                umbral=umbral,
                proyecto=proyecto,
                last_checked=timezone.now()
            )

        return super(ProyectoCreate, self).form_valid(form)

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

class NoCumplimientoView(ProyectoMixin, CreateView):
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
        qs = HistorialUmbrales.objects.filter(proyecto=self.proyecto).order_by('pk')
        return qs

class UmbralesEdit(ProyectoMixin, UpdateView):
    model = HistorialUmbrales
    form_class = UmbralForm
    template_name = 'configuracion/edit-umbrales.html'
    success_url = reverse_lazy('list-umbrales')
    success_message = 'Umbral editado correctamente'

    def get_form_kwargs(self):
        user = self.request.user
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = user
        h_umbral = self.get_object()
        umbral_pk = h_umbral.umbral.pk
        print(umbral_pk)
        kwargs["umbral_pk"] = umbral_pk
        return kwargs

class UmbralesNotificados(ProyectoMixin, ListView):
    model = NotificacionHU
    template_name = 'configuracion/umbral-notif-list.html'

    def get_queryset(self):
        # if self.request.user.perfil.rol_usuario == 4:
        n_hu = NotificacionHU.objects.select_related("h_umbral", "h_umbral__umbral").filter(h_umbral__proyecto=self.proyecto, notificacion__usuario=self.request.user).order_by("date")
        return n_hu

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["umbrales_notificados"] = self.get_queryset()
        return context
        
class UNDetail(ProyectoMixin, DetailView):
    model = NotificacionHU
    template_name = 'configuracion/umbral-notif-detail.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        un_obj = self.get_object()
        if un_obj.porcentaje_atraso != None:
            context["atrasos"] = True
        context["umbral_notificado"] = un_obj
        return context
