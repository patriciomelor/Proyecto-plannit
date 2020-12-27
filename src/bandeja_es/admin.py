from django.contrib import admin
from .models import Paquete
from .models import Version
from .models import PaqueteDocumento
#import borradores
from .models import BorradorVersion
from .models import BorradorPaquete
from .models import BorradorDocumento
#import preview
from .models import PrevVersion
from .models import PrevPaquete
from .models import PrevPaqueteDocumento
# Register your models here.



admin.site.register(Paquete)
admin.site.register(Version)
admin.site.register(PaqueteDocumento)
#Registrar Borradores
admin.site.register(BorradorVersion)
admin.site.register(BorradorPaquete)
admin.site.register(BorradorDocumento)
#Register previw
admin.site.register(PrevVersion)
admin.site.register(PrevPaquete)
admin.site.register(PrevPaqueteDocumento)
