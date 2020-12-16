from django import forms
from django.forms import BaseFormSet
from django.forms import (formset_factory, modelformset_factory)
import django.forms.widgets
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from panel_carga.models import Documento
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Perfil

class CrearUsuario(UserCreationForm):
    administrador = forms.BooleanField( label="Administrador", required=False)
    revisor = forms.BooleanField(label="Revisor", required=False)
    visualizador = forms.BooleanField(label="Visualizador", required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']

