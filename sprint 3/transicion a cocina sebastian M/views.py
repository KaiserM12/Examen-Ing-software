# views.py (Fragmento de confirmar_pedido)

        pedido.estado = 'EN_COCINA'
        pedido.save()
        return JsonResponse({'success': True})