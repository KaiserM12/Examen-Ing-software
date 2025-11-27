# views.py (Fragmento de api_pedido_listo)

            pedido.estado = 'LISTO' 
            pedido.save()
            return JsonResponse({'success': True})