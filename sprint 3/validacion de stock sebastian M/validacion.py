# views.py (Bloque de código a añadir en confirmar_pedido ANTES de cambiar el estado)

        for detalle in pedido.detalles.all():
            if not detalle.producto.disponible:
                return JsonResponse(
                    {'success': False, 'error': f'El producto "{detalle.producto.nombre}" no está disponible. Stock agotado.'}, 
                    status=400
                )