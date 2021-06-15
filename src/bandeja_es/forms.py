from django import forms
from django.forms import BaseFormSet
from django.forms import (formset_factory, modelformset_factory)
from django.urls import (reverse_lazy, reverse)
from crispy_forms.helper import FormHelper
from django.core.exceptions import ValidationError

from crispy_forms.layout import Submit
from panel_carga.models import Documento
from django.contrib.auth.models import User

from .models import Paquete, Version, PrevPaquete, PrevVersion, PrevPaqueteDocumento
from panel_carga.views import ProyectoMixin

from panel_carga.choices import TYPES_REVISION
from panel_carga.models import Documento
#summernote
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget



# class DocumentoListForm(forms.Form):
#     documento = forms.MultipleChoiceField(required=False, label="Escoja los documentos a enviar: ")
#     file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label="Adjunte archivo al los documentos: ")
#     # documento = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False, label="Escoja los documentos a enviar: ")


class BaseArticleFormSet(BaseFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields["destinatario"] = forms.ModelChoiceField(queryset=User.objects.all())
        form.fields["asunto"] = forms.CharField(max_length=250)
        form.fields["descripcion"] = forms.CharField(widget=forms.Textarea,max_length=500)

# ***********************************
#   formularios para crear paquete y versiones, pronto quedarán inactivos
# ***********************************

class CreatePaqueteForm(forms.ModelForm):
    descripcion = forms.CharField(widget=forms.Textarea, max_length=500)
    class Meta:
        model = Paquete
        fields = ['destinatario', 'asunto']
class VersionDocForm(forms.ModelForm):
    class Meta:
        model = Version
        fields = ['documento_fk', 'revision', 'archivo', 'estado_cliente', 'estado_contratista']

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['documento_fk'].queryset = Documento.objects.none()
        
VersionFormset = formset_factory(VersionDocForm, extra=1)




# ***********************************
#formularios para crear la PREVIEW del paquete y versiones, con el debido FORMSET
# ***********************************

class PaquetePreviewForm(forms.ModelForm):
    class Meta:
        model = PrevPaquete
        fields = ['prev_receptor', 'prev_asunto', 'prev_descripcion', 'prev_comentario']
        labels = {
            'prev_receptor': 'Destinatario',
            'prev_comentario': 'Archivo de Comentario'
        }
        widgets = {
            'prev_descripcion': SummernoteInplaceWidget()
        }
        
    def __init__(self, **kwargs):
        user_list = []
        self.usuario = kwargs.pop('usuario')
        self.participantes = kwargs.pop('participantes')
        current_rol = self.usuario.perfil.rol_usuario
        for user in self.participantes:
            try:
                rol = user.perfil.rol_usuario
                if rol >= 1 and rol <= 3:
                    if current_rol >= 1 and current_rol <= 3:
                        user_list.append(user.pk)
                elif rol <= 6 and rol >= 4:
                    if current_rol <= 6 and current_rol >= 4:
                        user_list.append(user.pk)
            except:
                continue
        qs = self.participantes.exclude(pk__in=user_list)
        print(qs)
        super(PaquetePreviewForm, self).__init__(**kwargs)
        self.fields["prev_receptor"] = forms.ModelChoiceField(queryset=qs)
        self.fields["prev_receptor"].label = 'Destinatario'

    def clean(self):
        cleaned_data = super().clean()
        destinatario = cleaned_data.get('prev_receptor')
        if self.usuario == destinatario:
            raise ValidationError('No puedes enviarte un paquete a ti mismo!')
        pass


class PrevVersionForm(forms.ModelForm):
    adjuntar = forms.BooleanField(label="Adjuntar Archivo ?", required=False, widget=forms.CheckboxInput(attrs={'onClick':'disableSending()'}))
    class Meta:
        model = PrevVersion
        fields = ['prev_documento_fk', 'prev_revision' ,'prev_estado_cliente', 'prev_estado_contratista', 'prev_archivo']
        labels = {
            'prev_documento_fk': 'Código Documento',
            'prev_estado_cliente': 'Estado Cliente',
            'prev_estado_contratista': 'Estado Contratista',
            'prev_archivo' : 'Archivo',
        }
        widgets ={
            'prev_documento_fk': forms.Select(attrs={'class': 'select2 form-control col-md-4'}),
            'prev_revision' : forms.Select(attrs={'class' : 'form-control col-md-4 '}),
            'prev_estado_contratista': forms.Select(attrs={'class' : 'form-control col-md-4' }),
            'prev_estado_cliente' : forms.Select(attrs={'class' : 'form-control col-md-4 '}),
            'prev_archivo' : forms.FileInput(attrs={'class' : 'col-md-4 ','disabled':'disabled'}),
        
        }
    
    def __init__(self, **kwargs):
        self.paquete = kwargs.pop('paquete_pk', None)
        self.usuario = kwargs.pop('user', None)
        super(PrevVersionForm, self).__init__(**kwargs)
        if self.usuario.perfil.rol_usuario >= 4 and self.usuario.perfil.rol_usuario <=6:
            self.fields["prev_archivo"].required = True
            
    def clean(self):
        cleaned_data = super().clean()
        #Verifica que el formulario venga con los datos minimos
        doc = cleaned_data.get('prev_documento_fk')
        nombre_documento = doc.Codigo_documento
        nombre_archivo = str(cleaned_data.get('prev_archivo'))
        estado_cliente = cleaned_data.get('prev_estado_cliente')
        estado_contratista = cleaned_data.get('prev_estado_contratista')
        revision = cleaned_data.get('prev_revision')
        revision_str = (dict(TYPES_REVISION).get(revision))

        #Verifica que primero se emita una revisión en B
        try:
            document = Documento.objects.get(Codigo_documento=doc)
            ultima_revision = Version.objects.filter(documento_fk=document)
            if not ultima_revision.exists() and revision > 1:
                raise ValidationError('Se debe emitir una revisión en B primero')
        except AttributeError:
            pass


        #Varifica si existe una version creada en el paquete
        #para el documento selecionado
        try:
            document = Documento.objects.get(Codigo_documento=doc)
            ultima_rev = Version.objects.filter(documento_fk=document).last()
            if ultima_rev.estado_cliente is not None:
                print("La última versión de este Documento Fue emitido por el Cliente")
                if not ultima_rev.estado_cliente == 6 and revision == ultima_rev.revision:
                    raise ValidationError('No se puede mantener la revisión del documento {}, por favor intente con una revisión distinta'.format(document.Codigo_documento))
            else:
                print("La última versión de este Documento Fue emitido por el Contratista")
                
        except (AttributeError, Version.DoesNotExist):
            pass


        #Verificca que no se pueda emitir una revision en número antes de que en letra
        try:
            ultima_revision = Version.objects.filter(documento_fk=doc)
            if not ultima_revision.exists() and revision >= 5:
                raise ValidationError('No se puede emitir una revisión en N° antes que en letra')
        except (AttributeError, Version.DoesNotExist):
            pass


        #Verifica que no se pueda enviar una version igual 
        # o anterior a la última emitida
        try:
            ultima_revision = Version.objects.filter(documento_fk=doc).last()
            if revision < ultima_revision.revision:
                raise ValidationError('No se puede elegir una revisión anterior a la última emitida')
        except AttributeError:
            pass


        #Verifica que el nombre del archivo coincida con
        #el nombre del documento + la version escogida.
        if self.usuario.perfil.rol_usuario >= 1 and self.usuario.perfil.rol_usuario <=3:
            con_archivo = cleaned_data.get("adjuntar")
            print(con_archivo)
            if con_archivo == True:
                if not verificar_nombre_archivo(nombre_documento, revision_str, nombre_archivo):
                    raise ValidationError('El nombre del Documento seleccionado y el del archivo no coinciden, Por favor verifique los datos.')
                print(nombre_archivo)
                if nombre_archivo == '':
                    self.add_error('No se adjuntó archivo')
            if not estado_cliente: 
                raise ValidationError("Debes seleccionar un estado para esta revisión.")
        
        if self.usuario.perfil.rol_usuario >= 4 and self.usuario.perfil.rol_usuario <=6:
            if not verificar_nombre_archivo(nombre_documento, revision_str, nombre_archivo):
                raise ValidationError('El nombre del Documento seleccionado y el del archivo no coinciden, Por favor verifique los datos.')
            if not estado_contratista: 
                raise ValidationError("Debes seleccionar un estado para esta revisión.")

        
        #Verificar que no se pueda emitir para constucción con estados Números
        if revision < 5 and estado_cliente == 5:
            raise ValidationError('No se puede emitir Válido para construcción estando en Letra')





def verificar_nombre_archivo(nombre_documento, revision_str, nombre_archivo):
    try:
        index = nombre_archivo.index('.')
    except ValueError:
        index = len(nombre_archivo)

    cleaned_name = nombre_archivo[:index]
    extencion = nombre_archivo[index:]

    nombre_final = nombre_documento + '-' + revision_str
    print(nombre_final)
    if cleaned_name == nombre_final:
        return True
    else:
        return False