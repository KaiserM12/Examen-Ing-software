from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from Agregar_Menus_Pedidos_app import views as app_views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', app_views.menu_cliente, name='menu_cliente'),
    path('pedidos/', include('Agregar_Menus_Pedidos_app.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)