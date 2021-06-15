<<<<<<< HEAD
"""dmp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls import handler403, handler404, handler500, handler400
from django.conf.urls.static import static
from tools.default_handler import error_400_view, error_403_view, error_404_view, error_500_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('account/', include('allauth.urls')),
    path('invitations/', include('invitations.urls', namespace='invitations')),
    path('notifications/', include('notifications.urls')),
    path('panel_carga/', include('panel_carga.urls')),
    path('bandeja_es/', include('bandeja_es.urls')),
    path('analitica/', include('analitica.urls')),
    path('configuracion/', include('configuracion.urls')),
    path('buscador/', include('buscador.urls')),
    path('status/', include('status.urls')),
    path('status_encargado/', include('status_encargado.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = error_400_view
handler403 = error_403_view
handler404 = error_404_view
=======
"""dmp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls import handler403, handler404, handler500, handler400, url
from django.conf.urls.static import static
from tools.default_handler import error_400_view, error_403_view, error_404_view, error_500_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('account/', include('allauth.urls')),
    path('invitations/', include('invitations.urls', namespace='invitations')),
    path('notifications/', include('notifications.urls')),
    path('panel_carga/', include('panel_carga.urls')),
    path('bandeja_es/', include('bandeja_es.urls')),
    path('analitica/', include('analitica.urls')),
    path('configuracion/', include('configuracion.urls')),
    path('buscador/', include('buscador.urls')),
    path('status/', include('status.urls')),
    path('status_encargado/', include('status_encargado.urls')),
    url('summernote/', include('django_summernote.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = error_400_view
handler403 = error_403_view
handler404 = error_404_view
>>>>>>> dmp-beta
handler500 = error_500_view