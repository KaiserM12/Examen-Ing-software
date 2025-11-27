# views.py (Fragmento de api_modificar_pedido)

        if accion == 'sumar' and not producto.disponible:
             return JsonResponse({'error': f'{producto.nombre} no disponible.'}, status=400)