# views.py (Función historial_cocina)

def historial_cocina(request):
    pedidos = Pedido.objects.filter(estado='EN_COCINA').order_by('fecha_actualizacion')
    return render(request, 'app_pedidos/historial.html', {'pedidos': pedidos})