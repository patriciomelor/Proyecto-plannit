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
    empresa = forms.CharField(max_length=128, required=True, label='Nombre de la Empresa')
    cargo_empresa = forms.CharField(max_length=128, required=True, label='Cargo en la Empresa')
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']

class EditUsuario(UserChangeForm):
    rol_usuario = forms.ChoiceField(choices=ROLES, required=True, label='Rol del Usuario')
    empresa = forms.CharField(max_length=128, required=True, label='Nombre de la Empresa')
    cargo_empresa = forms.CharField(max_length=128, required=True, label='Cargo en la Empresa')

    def __init__(self, *args, **kwargs):
        self.rol =  kwargs.pop("usuario")
        super().__init__(*args, **kwargs)
        if self.rol >= 4 and self.rol <=6:
            self.fields["rol_usuario"].choices = ROLES[3:]

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
    class Meta:
        model = HistorialUmbrales
        fields = ["tiempo_control", "variable_atraso"]
