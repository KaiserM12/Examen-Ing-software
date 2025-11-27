from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from .models import Mesa, Cliente, Pedido, Producto, DetallePedido
import json

def menu_cliente(request):
    return render(request, 'app_pedidos/menu_cliente.html')

def index(request):
    mesas = Mesa.objects.all().order_by('numero')
    clientes = Cliente.objects.all().order_by('-id')
    
    lista_mesas = []
    
    for mesa in mesas:
        pedido_activo = Pedido.objects.filter(
            mesa=mesa
        ).exclude(estado='PAGADO').first()
        
        lista_mesas.append({
            'obj': mesa,
            'pedido': pedido_activo
        })
    
    context = {
        'lista_mesas': lista_mesas,
        'clientes': clientes,
    }
    return render(request, 'app_pedidos/index.html', context)

@csrf_exempt
def api_crear_cliente(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        nombre = data.get('nombre')
        if nombre:
            if Cliente.objects.filter(nombre__iexact=nombre).exists(): 
                return JsonResponse({'success': False, 'error': f'El cliente "{nombre}" ya existe.'}, status=400)
                
            cliente = Cliente.objects.create(nombre=nombre)
            return JsonResponse({'success': True, 'id': cliente.id, 'nombre': cliente.nombre})
    return JsonResponse({'success': False})

@csrf_exempt
def api_crear_mesa(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        numero = data.get('numero')
        if numero:
            if Mesa.objects.filter(numero=numero).exists():
                return JsonResponse({'success': False, 'error': f'La mesa número {numero} ya existe.'}, status=400)
                
            Mesa.objects.create(numero=numero)
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
def api_eliminar_mesa(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        mesa_id = data.get('mesa_id')
        mesa = get_object_or_404(Mesa, pk=mesa_id)
        if mesa.estado == 'OCUPADA':
             return JsonResponse({'success': False, 'error': 'No puedes eliminar una mesa ocupada'})
        mesa.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
def iniciar_atencion(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        mesa_id = data.get('mesa_id')
        cliente_id = data.get('cliente_id')
        
        mesa = get_object_or_404(Mesa, pk=mesa_id)
        cliente = get_object_or_404(Cliente, pk=cliente_id)
        
        if mesa.estado == 'OCUPADA':
            return JsonResponse({'success': False, 'error': 'Mesa ocupada'}, status=400)

        # NUEVA VALIDACIÓN: Verificar si el Cliente ya tiene un pedido activo
        pedido_activo_cliente = Pedido.objects.filter(
            cliente=cliente
        ).exclude(estado__in=['PAGADO', 'CANCELADO']).exists() # Se asume 'CANCELADO' o solo 'PAGADO' como estados finales
        
        if pedido_activo_cliente:
            return JsonResponse({'success': False, 'error': f'El cliente "{cliente.nombre}" ya tiene un pedido activo en otra mesa.'}, status=400)
            
        with transaction.atomic():
            mesa.estado = 'OCUPADA'
            mesa.save()
            pedido = Pedido.objects.create(mesa=mesa, cliente=cliente, estado='CREANDO')
            
        return JsonResponse({'success': True, 'pedido_id': pedido.id})
    return JsonResponse({'success': False}, status=405)

@csrf_exempt
def api_liberar_mesa(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        mesa_id = data.get('mesa_id')
        
        mesa = get_object_or_404(Mesa, pk=mesa_id)
        
        pedido = Pedido.objects.filter(mesa=mesa).exclude(estado='PAGADO').first()
        if pedido:
            pedido.estado = 'PAGADO'
            pedido.save()
        
        mesa.estado = 'LIBRE'
        mesa.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def vista_toma_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    productos = Producto.objects.all().order_by('categoria')
    productos_por_categoria = {}
    for p in productos:
        if p.categoria not in productos_por_categoria:
            productos_por_categoria[p.categoria] = []
        productos_por_categoria[p.categoria].append(p)
    
    context = {
        'pedido': pedido,
        'productos_por_categoria': productos_por_categoria,
        'detalles_pedido': pedido.detalles.all().select_related('producto'),
        'subtotal_pedido': pedido.subtotal
    }
    return render(request, 'app_pedidos/toma_pedido.html', context)

def api_modificar_pedido(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, pk=pedido_id)
        producto_id = request.POST.get('producto_id')
        accion = request.POST.get('accion', 'sumar')
        
        producto = get_object_or_404(Producto, pk=producto_id)

        if accion == 'sumar' and not producto.disponible:
             return JsonResponse({'error': f'{producto.nombre} no disponible.'}, status=400)

        detalle = DetallePedido.objects.filter(pedido=pedido, producto=producto).first()

        if detalle is None:
            if accion in ['restar', 'eliminar']: return JsonResponse({'success': True})
            detalle = DetallePedido(pedido=pedido, producto=producto, cantidad=0, precio_unitario=producto.precio)

        if accion == 'sumar':
            detalle.cantidad += 1
            detalle.save()
        elif accion == 'restar':
            detalle.cantidad -= 1
            if detalle.cantidad <= 0: detalle.delete()
            else: detalle.save()
        elif accion == 'eliminar':
            detalle.delete()

        return JsonResponse({'success': True, 'subtotal': pedido.subtotal})
    return JsonResponse({'error': 'Error'}, status=405)

@csrf_exempt
def confirmar_pedido(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, pk=pedido_id)
        if not pedido.detalles.exists():
             return JsonResponse({'success': False, 'error': 'Pedido vacío'})
        pedido.estado = 'EN_COCINA'
        pedido.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def historial_cocina(request):
    pedidos = Pedido.objects.filter(estado='EN_COCINA').order_by('fecha_actualizacion')
    return render(request, 'app_pedidos/historial.html', {'pedidos': pedidos})

@csrf_exempt
def api_pedido_listo(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pedido = get_object_or_404(Pedido, pk=data.get('pedido_id'))
            
            pedido.estado = 'LISTO'
            pedido.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

@csrf_exempt
def api_liberar_mesa(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mesa = get_object_or_404(Mesa, pk=data.get('mesa_id'))
            
            pedido = Pedido.objects.filter(mesa=mesa).exclude(estado='PAGADO').first()
            
            if pedido:
                pedido.estado = 'PAGADO'
                pedido.save()
            
            mesa.estado = 'LIBRE'
            mesa.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

def api_info_producto(request, producto_id):
    p = get_object_or_404(Producto, pk=producto_id)
    return JsonResponse({
        'nombre': p.nombre,
        'descripcion': p.descripcion,
        'ingredientes': p.ingredientes,
        'precio': p.precio,
        'categoria': p.categoria
    })