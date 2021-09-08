from django import forms
from django.forms import BaseFormSet, fields
from django.forms import (formset_factory, modelformset_factory)
import django.forms.widgets
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from panel_carga.models import Documento, Proyecto
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import HistorialUmbrales, Perfil, Restricciones, CausasNoCumplimiento
from .roles import *


class CrearUsuario(UserCreationForm):
    rol_usuario = forms.ChoiceField(choices=ROLES, required=True, label='Rol del Usuario')
    empresa = forms.CharField(max_length=128, required=True, label='Nombre Empresa')
    cargo_empresa = forms.CharField(max_length=128, required=True, label='Cargo')

    def __init__(self, *args, **kwargs):
        self.rol =  kwargs.pop("usuario")
        super().__init__(*args, **kwargs)
        if self.rol >= 4 and self.rol <=6:
            self.fields["rol_usuario"].choices = ROLES[3:]
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']

class EditUsuario(UserChangeForm):
    rol_usuario = forms.ChoiceField(choices=ROLES, required=True, label='Rol del Usuario')
    empresa = forms.CharField(max_length=128, required=True, label='Nombre Empresa')
    cargo_empresa = forms.CharField(max_length=128, required=True, label='Cargo')

    def __init__(self, *args, **kwargs):
        self.rol =  kwargs.pop("usuario")
        super().__init__(*args, **kwargs)
        if self.rol >= 4 and self.rol <=6:
            self.fields["rol_usuario"].choices = ROLES[3:]

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        exclude = ['password1', 'password2']
        

class EditProfile(UserChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password"].widget = forms.HiddenInput()
        # self.fields["password2"].widget = forms.HiddenInput()


    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        exclude = ['password1', 'password2']
class InvitationForm(forms.Form):
    nombres = forms.CharField(max_length=30)
    correo = forms.CharField(max_length=30)



class RestriccionForm(forms.ModelForm):
    class Meta:
        model = Restricciones
        fields = ["nombre"]
class NoCumplimientoForm(forms.ModelForm):
    class Meta:
        model = CausasNoCumplimiento
        fields = ["nombre"]


class UmbralForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        self.umbral_pk = kwargs.pop('umbral_pk', None)
        current_rol = self.usuario.perfil.rol_usuario
        #### recorre a todos los participantes e incluye en un listado solo el equipo de la empresa
        super(UmbralForm, self).__init__(*args, **kwargs)
        if current_rol == 1:
            self.fields["contratista_tiempo_control"].widget = forms.HiddenInput()
            self.fields["contratista_variable_atraso"].widget = forms.HiddenInput()

        if current_rol == 4:
            self.fields["cliente_tiempo_control"].widget = forms.HiddenInput()
            self.fields["cliente_variable_atraso"].widget = forms.HiddenInput()

        if self.umbral_pk == 4:
            self.fields["cliente_variable_atraso"].label = "Desviación Porcentual (%)"
            self.fields["contratista_variable_atraso"].label = "Desviación Porcentual (%)"

    class Meta:
        model = HistorialUmbrales
        exclude = ["umbral", "proyecto", "last_checked"]
