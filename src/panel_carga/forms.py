from django import forms
import django.forms.widgets
from .models import Proyecto, Documento, Revision
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit



class UploadFileForm(forms.Form):
    importfile = forms.FileField()

class ProyectoSelectForm(forms.Form):
    proyectos = forms.ModelChoiceField(queryset=Proyecto.objects.none())
    
    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('proyectos')
        super(ProyectoSelectForm, self).__init__(*args, **kwargs)
        self.fields['proyectos'].queryset = qs

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = '__all__'
        widgets = {
            'fecha_inicio':forms.TextInput(attrs={'type': 'date'}),
            'fecha_termino':forms.TextInput(attrs={'type': 'date'}),
            'descripcion':forms.Textarea(attrs={'row':'5','style':'height:100px;'}),
        }

class DocumentoForm(forms.ModelForm):

    Especialidad = forms.CharField( max_length=50, required=True)
    Descripcion = forms.CharField( max_length=150, required=True )
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