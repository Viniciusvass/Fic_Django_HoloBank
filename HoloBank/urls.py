from django.contrib import admin
from django.urls import path, include
from .views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('usuarios/', include('apps.usuarios.urls')),
    path('contas/', include('apps.contas.urls')),
    path('creditos/', include('apps.creditos.urls')),
    
]
