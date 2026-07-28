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
        
        # 📉 Frontend එකෙන් එවන Discount දත්ත කියවා ගැනීම
        discount_value = Decimal(str(payload.get('discount_value', 0)))
        discount_type = payload.get('discount_type', 'cash')

        if not cart:
            return JsonResponse({'success': False, 'error': 'Cart is empty.'}, status=400)

        total_amount = Decimal('0')
        total_cost = Decimal('0')
        order_items = []

        for item in cart:
            qty = int(item['qty'])
            if qty <= 0:
                return JsonResponse({'success': False, 'error': 'Invalid quantity.'}, status=400)

            if item.get('is_custom'):
                # ➕ අතින් ඇතුළත් කළ භාණ්ඩයක් නම් (Custom Item)
                c_name = item.get('name', 'Custom Item')
                c_price = Decimal(str(item.get('price', 0)))
                c_cost = c_price  # Custom භාණ්ඩ සඳහා පිරිවැය සහ විකුණුම් මිල සමාන කළා

                total_amount += c_price * qty
                total_cost += c_cost * qty

                order_items.append((None, c_name, c_price, c_cost, qty))
            else:
                # 🍫 ඩේටාබේස් එකේ පවතින සාමාන්‍ය නිෂ්පාදනයක් නම්
                product = Product.objects.select_for_update().get(id=int(item['id']))
                
                if product.stock < qty:
                    return JsonResponse({'success': False, 'error': f'Insufficient stock for {product.name}.'}, status=400)

                subtotal = product.selling_price * qty
                total_amount += subtotal
                total_cost += product.cost_price * qty

                order_items.append((product, None, product.selling_price, product.cost_price, qty))

        # 📉 සර්වර් එක ඇතුළතදී වට්ටම (Discount) ගණනය කිරීම
        discount_amount = Decimal('0')
        if discount_type == 'percent':
            discount_amount = (total_amount * discount_value) / Decimal('100')
        else:
            discount_amount = discount_value

        # වට්ටම මුළු එකතුවට වඩා වැඩි විය නොහැක
        if discount_amount > total_amount:
            discount_amount = total_amount

        # බිලේ නෙට් එකතුව (Net Total) සකස් කිරීම
        net_total_amount = total_amount - discount_amount

        if cash_received < net_total_amount:
            return JsonResponse({'success': False, 'error': 'Cash received is less than total amount.'}, status=400)

        change_given = cash_received - net_total_amount

        # Order Record එක සෑදීම
        order = Order.objects.create(
            total_amount=net_total_amount,
            total_cost=total_cost,
            cash_received=cash_received,
            change_given=change_given,
        )

        # Order Items ටේබල් එකට දත්ත ඇතුළත් කිරීම සහ ස්ටොක් අඩු කිරීම
        response_items = []
        for product, custom_name, unit_price, unit_cost, qty in order_items:
            OrderItem.objects.create(
                order=order,
                product=product,
                custom_name=custom_name,
                quantity=qty,
                unit_price=unit_price,
                unit_cost=unit_cost,
            )
            
            if product:
                product.stock -= qty
                product.save(update_fields=['stock'])
                display_name = product.name
            else:
                display_name = custom_name

            response_items.append({
                'name': display_name,
                'qty': qty,
                'unit_price': float(unit_price),
                'subtotal': float(unit_price * qty),
            })

        # ⚡ මෙතනට 'gross_total' සහ 'discount_amount' එකතු කළා, එවිට Frontend (JavaScript) එකට රිසිට් එක සිංහලෙන් ප්‍රින්ට් කරන්න ලේසියි.
        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'gross_total': float(total_amount),
            'discount_amount': float(discount_amount),
            'total_amount': float(net_total_amount),
            'cash_received': float(cash_received),
            'change_given': float(change_given),
            'timestamp': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'items': response_items,
        })

    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found.'}, status=404)
    except (InvalidOperation, ValueError, KeyError, TypeError) as e:
        return JsonResponse({'success': False, 'error': f'Invalid data: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
def get_live_stock_api(request):
    try:
        products = Product.objects.all()
        stock_list = []
        
        for p in products:
            stock_list.append({
                'id': p.id,
                'stock': p.stock
            })
            
        return JsonResponse({'success': True, 'stocks': stock_list})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)