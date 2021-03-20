from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic import FormView, CreateView, DeleteView, UpdateView, ListView, DetailView
from panel_carga.views import ProyectoMixin
from django.contrib.auth.models import User, Group, Permission, PermissionsMixin
from .roles import ROLES
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.conf import settings 
from django.template.loader import render_to_string
from django.core.mail import send_mail 
from panel_carga.models import *
from panel_carga.forms import ProyectoForm
from bandeja_es.models import *

from analitica import *

from .models import Perfil
from .forms import CrearUsuario, EditUsuario, InvitationForm

from invitations.utils import get_invitation_model

# Create your views here.
class UsuarioView(ProyectoMixin, CreateView):
    template_name = "configuracion/create-user.html"
    form_class = CrearUsuario
    success_message = 'Usuario Creado.'
    success_url = reverse_lazy('crear-usuario')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nombre = self.proyecto.codigo
        grupo = Group.objects.get(name=nombre)
        print(grupo)
        context["grupo"] = grupo
        return context
    
    def form_valid(self, form):
        context = {}
        response = super().form_valid(form)
        user_pk = form.instance.pk
        user = User.objects.get(pk=user_pk)
        rol = form.cleaned_data['rol_usuario']
        grupo = Group.objects.get(name= self.proyecto.codigo)
        user.groups.add(grupo)
        passwrd1 =  form.cleaned_data['password2']
        email = form.cleaned_data['email']
        print("contraseña: ", passwrd1)
        print("email: ", email)
        context['password'] = passwrd1
        context['email'] = email
        perfil = Perfil.objects.get_or_create(
            usuario= user,
            rol_usuario= rol,
            cliente= form.cleaned_data['cliente']
            )
        nombre = self.proyecto.codigo
        grupo = Group.objects.get(name=nombre)
        msg_plano = render_to_string('configuracion/nuervo-user-email.txt', context=context)
        msg_html = render_to_string('configuracion/nuervo-user-email.html', context=context)
        subject = 'Usuario y contraseña' 
        send_mail(
            subject=subject,
            message=msg_plano,
            html_message=msg_html
        )
        #Otorgar permisos para administrador

        #permission_required = ('polls.view_choice', 'polls.change_choice')
        Permisos = ['add_documento', 'change_documento']
        permission_list_administrador = []
        
        #a los permisos de administrador y revisor, les falta el status y buscador, netamente para probar con distintos paneles al mismo tiempo
        permission_required_administrador = ('panel_carga.add_documento','panel_carga.change_documento','panel_carga.edit_documento','panel_carga.delete_documento', 'analitica.view_all','bandeja_es.edit_paquete','bandeja_es.view_paquete','bandeja_es.add_paquete', 'bandeja_es.delete_paquete', 'configuracion.view_user','configuracion.edit_user', 'configuracion.add_user','configuracion.delete_user')
        permission_required_revisor = ('panel_carga.add_documento','panel_carga.change_documento','panel_carga.edit_documento','panel_carga.delete_documento', 'analitica.view_all','bandeja_es.edit_paquete','bandeja_es.view_paquete','bandeja_es.add_paquete','bandeja_es.delete_paquete')
        permission_required_visualizador = ('analitica.view', 'buscador.view') #Status no se ha definido completamente no?

        if rol=='1':

            for permisos in Permisos:

                content_type = ContentType.objects.get_for_model(Documento)
                permission = Permission.objects.get(
                    codename= permisos, 
                    content_type = content_type, 
                )

                permission_list_administrador.append(permission)
            
            for per in permission_list_administrador:
                user.user_permissions.add(per)

        #Otorgar permisos para revisor
        Permisos = ['add_documento', 'change_documento']
        permission_list_revisor = []

        if rol=='2':

            for permisos in Permisos:

                content_type = ContentType.objects.get_for_model(Documento)
                permission = Permission.objects.get(
                    codename= permisos, 
                    content_type = content_type, 
                )

                permission_list_revisor.append(permission)

            for per in permission_list_revisor:
                user.user_permissions.add(per)

        #Otorgar permisos para visualizador
        Permisos = ['add_paquete', 'change_paquete']
        permission_list_visualizador = []

        if rol=='3':

            for permisos in Permisos:

                content_type = ContentType.objects.get_for_model(Paquete)
                permission = Permission.objects.get(
                    codename= permisos, 
                    content_type = content_type, 
                )

                permission_list_visualizador.append(permission)
        
            for per in permission_list_visualizador:
                user.user_permissions.add(per)

        return response

class UsuarioEdit(ProyectoMixin, UpdateView):
    model = User
    template_name = 'configuracion/edit-user.html'
    success_url = reverse_lazy('listar-usuarios')
    form_class = EditUsuario

    def form_valid(self, form):
        response = super().form_valid(form)
        user_pk = form.instance.pk
        user = User.objects.get(pk=user_pk)
        rol = form.cleaned_data['rol_usuario']

        perfil = Perfil.objects.get_or_create(
            usuario=user,
            rol_usuario= rol,
            cliente= form.cleaned_data['cliente']
        )

        #Otorgar permisos para administrador
        Permisos = ['add_documento', 'change_documento']
        permission_list_administrador = []

        if rol=='1':

            for permisos in Permisos:

                content_type = ContentType.objects.get_for_model(Documento)
                permission = Permission.objects.get(
                    codename= permisos, 
                    content_type = content_type, 
                )

                permission_list_administrador.append(permission)
            
            for per in permission_list_administrador:
                user.user_permissions.add(per)

        #Otorgar permisos para revisor
        Permisos = ['add_documento', 'change_documento']
        permission_list_revisor = []

        if rol=='2':

            for permisos in Permisos:

                content_type = ContentType.objects.get_for_model(Documento)
                permission = Permission.objects.get(
                    codename= permisos, 
                    content_type = content_type, 
                )

                permission_list_revisor.append(permission)

            for per in permission_list_revisor:
                user.user_permissions.add(per)

        #Otorgar permisos para visualizador
        Permisos = ['add_paquete', 'change_paquete']
        permission_list_visualizador = []

        if rol=='3':

            for permisos in Permisos:

                content_type = ContentType.objects.get_for_model(Paquete)
                permission = Permission.objects.get(
                    codename= permisos, 
                    content_type = content_type, 
                )

                permission_list_visualizador.append(permission)
        
            for per in permission_list_visualizador:
                user.user_permissions.add(per)

        return response
    
class UsuarioLista(ProyectoMixin, ListView):
    model = User
    template_name = 'configuracion/list-user.html'
    context_object_name = 'usuarios'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["codigo_proyecto"] = self.proyecto.codigo
        return context

class UsuarioDelete(ProyectoMixin, DeleteView):
    model = User
    template_name = 'configuracion/delete-user.html'
    success_url = reverse_lazy('listar-usuarios')
    context_object_name = 'usuario'
    
class UsuarioDetail(ProyectoMixin, DetailView):
    model = User
    template_name = 'configuracion/detail-user.html'
    context_object_name = "usuario"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        grupos = user.groups.all()
        print(grupos)
        context["grupos"] = grupos
        return context

# Añade usuarios al proyecto actual seleccionado
class UsuarioAdd(ProyectoMixin, ListView):
    model = User
    template_name = 'configuracion/add-lista_usuario.html'

    def get_context_data(self, **kwargs):
        user_list = []
        codigo = self.proyecto.codigo
        grupo = Group.objects.get(name=codigo)
        context = super().get_context_data(**kwargs)
        users = User.objects.all()
        for user in users:
            if not grupo in user.groups.all():
                user_list.append(user)
        context['users'] = user_list
        return context
    
    def post(self, request, *args, **kwargs):
        usuario_ids = self.request.POST.getlist('id[]')
        for usuario in usuario_ids:
            user = User.objects.get(pk=usuario)
            codigo = self.proyecto.codigo
            grupo = Group.objects.get(name=codigo)
            user.groups.add(grupo)
        return redirect('listar-usuarios')

class ProyectoList(ProyectoMixin, ListView):
    context_object_name = 'proyectos'
    template_name = 'configuracion/list-proyecto.html'
    queryset = Proyecto.objects.all().order_by('-fecha_inicio')

class ProyectoDetail(ProyectoMixin, DetailView):
    template_name='configuracion/detail-proyecto.html'       
    context_object_name = 'proyecto'

class ProyectoEdit(ProyectoMixin, UpdateView):
    template_name = 'configuracion/edit-proyecto.html'
    form_class = ProyectoForm
    success_url = reverse_lazy('lista-proyecto')
    success_message = 'Información del Proyecto Actualizada'

class ProyectoDelete(ProyectoMixin, DeleteView):
    template_name = 'configuracion/delete-proyecto.html'
    success_message = 'Proyecto Eliminado'
    success_url = reverse_lazy('lista-proyecto')

    def delete(self, request, *args, **kwargs):
        objeto = self.get_object()
        if objeto == proyecto:
            messages.add_message(request, messages.ERROR, 'No se puede eliminar el proyecto seleccionado.')
            return redirect('lista-proyecto')
        else:  
            proyect_group= Group.objects.get(name=objeto.codigo)
            proyect_group.delete()
            return super(ProyectoDelete, self).delete(request, *args, **kwargs)

class ProyectoCreate(ProyectoMixin, CreateView):
    template_name = 'configuracion/create-proyecto.html'
    success_message = 'Proyecto Creado correctamente'
    success_url = reverse_lazy('lista-proyecto')
    form_class = ProyectoForm

    def form_valid(self, form):
        form.instance.encargado = self.request.user
        response = super().form_valid(form)
        nombre = form.instance.codigo
        grupo = Group.objects.create(name=nombre)
        return response

class InvitationView(ProyectoMixin, FormView):
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




        