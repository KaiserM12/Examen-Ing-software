from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='gestion_mesas'),
    path('api/crear_cliente/', views.api_crear_cliente, name='api_crear_cliente'),
    path('api/crear_mesa/', views.api_crear_mesa, name='api_crear_mesa'),
    path('api/eliminar_mesa/', views.api_eliminar_mesa, name='api_eliminar_mesa'),
    path('api/iniciar_atencion/', views.iniciar_atencion, name='iniciar_atencion'),
    path('api/liberar_mesa/', views.api_liberar_mesa, name='api_liberar_mesa'),
    path('api/pedido_listo/', views.api_pedido_listo, name='api_pedido_listo'),
    path('pedido/<int:pedido_id>/', views.vista_toma_pedido, name='toma_pedido'),
    path('pedido/<int:pedido_id>/modificar/', views.api_modificar_pedido, name='api_modificar'),
    path('pedido/<int:pedido_id>/confirmar/', views.confirmar_pedido, name='confirmar_pedido'),
    path('api/producto/<int:producto_id>/', views.api_info_producto, name='api_info_prod'),
    path('pedido/<int:pedido_id>/agregar/', views.api_modificar_pedido, name='agregar_producto'),
    path('pedido/<int:pedido_id>/restar/', views.api_modificar_pedido, name='modificar_producto'),
    path('producto/<int:producto_id>/info/', views.api_info_producto, name='info_producto'),
    path('cocina/', views.historial_cocina, name='historial_cocina'),
]