from django import forms
from django.forms import BaseFormSet
from django.forms import (formset_factory, modelformset_factory)
import django.forms.widgets
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from panel_carga.models import Documento
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Perfil
from .roles import *


class CrearUsuario(UserCreationForm):
    rol_usuario = forms.ChoiceField(choices=ROLES, required=True, label='Rol del Usuario')
    empresa = forms.CharField(max_length=128, min_length=64, required=True, label='Nombre de la Empresa')
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']

class EditUsuario(UserChangeForm):
    rol_usuario = forms.ChoiceField(choices=ROLES, required=True, label='Rol del Usuario')
    empresa = forms.CharField(max_length=128, required=True, label='Nombre de la Empresa')
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        exclude = ['password1', 'password2']
        
        
class InvitationForm(forms.Form):
    nombres = forms.CharField(max_length=30)
    correo = forms.CharField(max_length=30)
