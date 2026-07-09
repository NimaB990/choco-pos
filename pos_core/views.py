import json
from decimal import Decimal, InvalidOperation

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.db import transaction
from django.core.serializers.json import DjangoJSONEncoder

from .models import Product, Order, OrderItem


def pos_page(request):
    products = Product.objects.filter(is_active=True, stock__gt=0).select_related()
    return render(request, 'pos_page.html', {'products': products})


@require_GET
def product_list_api(request):
    products = Product.objects.filter(is_active=True).values(
        'id', 'name', 'barcode', 'selling_price', 'stock', 'image'
    )
    data = [{
        'id': p['id'],
        'name': p['name'],
        'barcode': p['barcode'] or '',
        'price': float(p['selling_price']),
        'stock': p['stock'],
        'image': p['image'] if p['image'] else '',
    } for p in products]
    return JsonResponse({'products': data})


@require_GET
def barcode_lookup_api(request):
    code = request.GET.get('code', '').strip()
    if not code:
        return JsonResponse({'success': False, 'error': 'No barcode provided.'}, status=400)
    
    try:
        product = Product.objects.get(barcode=code, is_active=True)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': f'No product found for barcode {code}.'}, status=404)

    return JsonResponse({
        'success': True,
        'product': {
            'id': product.id,
            'name': product.name,
            'barcode': product.barcode or '',
            'price': float(product.selling_price),
            'stock': product.stock,
            'image': product.image.url if product.image else '',
        }
    })


@csrf_exempt
@require_POST
@transaction.atomic
def checkout_api(request):
    try:
        payload = json.loads(request.body)
        cart = payload.get('cart', [])
        cash_received = Decimal(str(payload.get('cash_received', 0)))

        if not cart:
            return JsonResponse({'success': False, 'error': 'Cart is empty.'}, status=400)

        total_amount = Decimal('0')
        total_cost = Decimal('0')
        order_items = []

        for item in cart:
            product = Product.objects.select_for_update().get(id=item['id'])
            qty = int(item['qty'])

            if qty <= 0:
                return JsonResponse({'success': False, 'error': f'Invalid quantity for {product.name}.'}, status=400)
            if product.stock < qty:
                return JsonResponse({'success': False, 'error': f'Insufficient stock for {product.name}.'}, status=400)

            subtotal = product.selling_price * qty
            total_amount += subtotal
            total_cost += product.cost_price * qty

            order_items.append((product, qty))

        if cash_received < total_amount:
            return JsonResponse({'success': False, 'error': 'Cash received is less than total amount.'}, status=400)

        change_given = cash_received - total_amount

        order = Order.objects.create(
            total_amount=total_amount,
            total_cost=total_cost,
            cash_received=cash_received,
            change_given=change_given,
        )

        for product, qty in order_items:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                unit_price=product.selling_price,
                unit_cost=product.cost_price,
            )
            product.stock -= qty
            product.save(update_fields=['stock'])

        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'total_amount': float(total_amount),
            'cash_received': float(cash_received),
            'change_given': float(change_given),
            'timestamp': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'items': [{
                'name': p.name,
                'qty': q,
                'unit_price': float(p.selling_price),
                'subtotal': float(p.selling_price * q),
            } for p, q in order_items],
        })

    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found.'}, status=404)
    except (InvalidOperation, ValueError, KeyError, TypeError) as e:
        return JsonResponse({'success': False, 'error': f'Invalid data: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

from django.http import JsonResponse
from .models import Product

from django.http import JsonResponse
from .models import Product

def get_live_stock_api(request):
    try:
        # ⚡ හැම ප්‍රොඩක්ට් එකකම අලුත්ම ස්ටොක් ගණන් ටික ගන්නවා
        products = Product.objects.all()
        stock_list = []
        
        for p in products:
            stock_list.append({
                'id': p.id,
                'stock': p.stock  # ⚠️ ඔයාගේ Product model එකේ stock පෙන්වන field එකේ නම 'stock' ම නේද කියලා ෂුවර් කරගන්න!
            })
            
        return JsonResponse({'success': True, 'stocks': stock_list})
    except Exception as e:
        # 🐛 මොකක් හරි අවුලක් ආවොත් සර්වර් එක crash වෙන්නේ නැතුව error එක පෙන්වනවා
        return JsonResponse({'success': False, 'error': str(e)}, status=500)