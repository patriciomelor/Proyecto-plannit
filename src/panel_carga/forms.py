from django import forms
import django.forms.widgets
from .models import Proyecto, Documento, Revision
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit



class UploadFileForm(forms.Form):
    importfile = forms.FileField()

class ProyectoSelectForm(forms.Form):
    proyectos =  forms.ModelChoiceField(queryset=Proyecto.objects.all())

class ProyectoForm(forms.ModelForm):
    nombre = forms.CharField( max_length=50, required=True)
    fecha_inicio = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), input_formats=['%Y-%m-%d'])
    fecha_termino = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), input_formats=['%Y-%m-%d'])
    descripcion = forms.CharField(widget=forms.Textarea, max_length=100, required=True)
    class Meta:
        model = Proyecto
        exclude = ['encargado']

# class MultipleSearching(forms.Form):
#     proyecto = forms.ModelChoiceField(queryset=Proyecto.objects.all(), widget=Select(attrs={
#             'class': 'form-control select2'
#         }))
    
#     documentos = forms.ModelChoiceField(queryset=Documento.objects.all(), widget=Select(attrs={
#         'class': 'form-control select2'
#     }))

class DocumentoForm(forms.ModelForm):

    Especialidad = forms.CharField( max_length=50, required=True)
    Descripcion = forms.CharField( max_length=150, required=True)
    Codigo_documento = forms.CharField( max_length=100, required=True)
    Numero_documento_interno = forms.CharField(max_length=30, required=False)
    archivo = forms.FileField(required=False)
    fecha_Emision_B = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'})) 
    fecha_Emision_0 =  forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    

    class Meta:
        model = Documento
        exclude = ['tipo','owner','emision','proyecto', 'ultima_edicion']

class RevisionForm(forms.ModelForm):
    tipo = forms.IntegerField( required=True)
    estado_cliente = forms.IntegerField(required=True)
    estado_contratista = forms.IntegerField(required=True)
    emitida_para = forms.CharField(widget=forms.Textarea, max_length=150, required=True)
    fecha = forms.DateField(required=True)
    
    class Meta:
        model = Revision
        fields = ['owner']