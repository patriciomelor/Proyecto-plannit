from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic import FormView, CreateView, DeleteView, UpdateView, ListView, DetailView
from panel_carga.views import ProyectoMixin
from django.contrib.auth.models import User, Group, Permission
from .roles import ROLES
from django.contrib.contenttypes.models import ContentType

from panel_carga.models import *
from panel_carga.forms import ProyectoForm
from bandeja_es.models import *

from .models import Perfil
from .forms import CrearUsuario, EditUsuario

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
        response = super().form_valid(form)
        user_pk = form.instance.pk
        user = User.objects.get(pk=user_pk)
        rol = form.cleaned_data['rol_usuario']

        perfil = Perfil.objects.get_or_create(
            usuario= user,
            rol_usuario= rol
            )
        nombre = self.proyecto.codigo
        grupo = Group.objects.get(name=nombre)
        user.groups.add(grupo)

        # if rol==3:

        #     content_type = ContentType.objects.get_for_model(bandeja_es)
        #     permission = Permission.objects.get(
        #         codename='view_bandeja_es',
        #         content_type = content_type
        #     )
        #     user.user_permissions.add(permission)

        return response
    
class UsuarioLista(ProyectoMixin, ListView):
    model = User
    template_name = 'configuracion/list-user.html'
    context_object_name = 'usuarios'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["codigo_proyecto"] = self.proyecto.codigo
        return context
    

class UsuarioEdit(ProyectoMixin, UpdateView):
    model = User
    template_name = 'configuracion/edit-user.html'
    success_url = reverse_lazy('listar-usuarios')
    form_class = EditUsuario

    def form_valid(self, form):
        response = super().form_valid(form)
        user_pk = form.instance.pk
        user = User.objects.get(pk=user_pk)
        perfil = Perfil.objects.get_or_create(
            usuario=user,
            rol_usuario= form.cleaned_data['rol_usuario']
        )
        return response

class UsuarioDelete(ProyectoMixin, DeleteView):
    model = User
    template_name = 'configuracion/delete-user.html'
    success_url = reverse_lazy('listar-usuarios')
    context_object_name = 'usuario'
    
    def post(self, request, *args, **kwargs):
        self.get_queryset().delete()
        return self.success_url
    
class UsuarioDetail(ProyectoMixin, DetailView):
    model = User
    template_name = 'configuracion/detail-user.html'
    context_object_name = "usuario"

class ProyectoList(ProyectoMixin, ListView):
    model = Proyecto
    context_object_name = 'proyectos'
    template_name='configuracion/list-proyecto.html'

class ProyectoDetail(ProyectoMixin, DetailView):
    model = Proyecto
    template_name='configuracion/detail-proyecto.html'       
    context_object_name = 'proyecto'

class ProyectoEdit(ProyectoMixin, UpdateView):
    model = Proyecto
    template_name = 'configuracion/edit-proyecto.html'
    form_class = ProyectoForm
    success_url = reverse_lazy('lista-proyecto')
    success_message = 'Información del Proyecto Actualizada'

class ProyectoDelete(ProyectoMixin, DeleteView):
    model = Proyecto
    template_name = 'configuracion/delete-proyecto.html'
    success_message = 'Proyecto Eliminado'
    success_url = reverse_lazy('lista-proyecto')
