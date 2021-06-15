<<<<<<< HEAD
from django.contrib import admin
from .models import Paquete
from .models import Version
from .models import PaqueteDocumento
#import borradores
from .models import BorradorPaquete
#import preview
from .models import PrevVersion
from .models import PrevPaquete
from .models import PrevPaqueteDocumento
# Register your models here.



admin.site.register(Paquete)
admin.site.register(Version)
admin.site.register(PaqueteDocumento)
#Registrar Borradores
admin.site.register(BorradorPaquete)
#Register previw
admin.site.register(PrevVersion)
admin.site.register(PrevPaquete)
admin.site.register(PrevPaqueteDocumento)
=======
from django.contrib import admin
from .models import Paquete
from .models import Version
from .models import PaqueteDocumento
#import borradores
from .models import BorradorPaquete
#import preview
from .models import PrevVersion
from .models import PrevPaquete
from .models import PrevPaqueteDocumento
# Register your models here.
from django_summernote.admin import SummernoteModelAdmin


admin.site.register(Paquete)
admin.site.register(Version)
admin.site.register(PaqueteDocumento)
#Registrar Borradores
admin.site.register(BorradorPaquete)
#Register previw
admin.site.register(PrevVersion)
admin.site.register(PrevPaquete)
admin.site.register(PrevPaqueteDocumento)
>>>>>>> dmp-beta
