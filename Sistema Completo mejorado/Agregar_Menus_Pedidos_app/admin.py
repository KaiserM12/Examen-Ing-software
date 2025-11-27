from django.contrib import admin
from django.utils.html import format_html
from .models import Cliente, Mesa, Pedido, Producto, DetallePedido

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    raw_id_fields = ['producto']
    readonly_fields = ['precio_unitario']

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'mesa_numero', 'cliente', 'estado', 'fecha_creacion', 'subtotal')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('cliente__nombre', 'mesa__numero')
    inlines = [DetallePedidoInline]
    readonly_fields = ['subtotal', 'total_items']
    
    def mesa_numero(self, obj):
        return obj.mesa.numero if obj.mesa else '-'
    mesa_numero.short_description = 'MESA'

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'telefono')
    search_fields = ('nombre',)

@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'estado', 'capacidad')
    list_filter = ('estado',)
    search_fields = ('numero',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'categoria', 'disponible', 'imagen_preview')
    list_filter = ('categoria', 'disponible')
    search_fields = ('nombre',)
    
    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.imagen.url)
        return "No hay imagen"
    
    imagen_preview.short_description = 'Previsualización'