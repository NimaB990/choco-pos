from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Sum
from .models import Product, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'barcode', 'cost_price_display', 'selling_price_display', 'profit_margin_display', 'stock_display', 'is_active']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['name', 'barcode']
    readonly_fields = ['created_at', 'updated_at', 'profit_margin']
    fieldsets = (
        ('භාණ්ඩයේ විස්තර (Product Info)', {
            'fields': ('name', 'barcode', 'image')
        }),
        ('මිල ගණන් (Pricing)', {
            'fields': ('cost_price', 'selling_price', 'profit_margin')
        }),
        ('තොග විස්තර (Stock)', {
            'fields': ('stock', 'is_active')
        }),
    )

    def cost_price_display(self, obj):
        return f"Rs. {str(obj.cost_price)}"
    cost_price_display.short_description = 'ගත් මිල (රු.)'

    def selling_price_display(self, obj):
        return f"Rs. {str(obj.selling_price)}"
    selling_price_display.short_description = 'විකුණුම් මිල (රු.)'

    def profit_margin_display(self, obj):
        margin = obj.profit_margin
        color = 'green' if margin > 0 else 'red'
        margin_str = f"{str(margin)}%"
        return format_html('<span style="color: {};">{}</span>', color, margin_str)
    profit_margin_display.short_description = 'ලාභ ප්‍රතිශතය'

    def stock_display(self, obj):
        color = 'green' if obj.stock > 10 else 'orange' if obj.stock > 0 else 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, str(obj.stock))
    stock_display.short_description = 'තොගය'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'unit_price', 'unit_cost']
    can_delete = False
    verbose_name = "ඇණවුම් අයිතමය"
    verbose_name_plural = "ඇණවුම් කරන ලද... "


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'total_amount_display', 'total_cost_display', 'profit_display', 'created_at_formatted']
    list_filter = ['created_at']
    search_fields = ['order_number']
    readonly_fields = ['order_number', 'total_amount', 'total_cost', 'cash_received', 'change_given', 'profit', 'created_at']
    inlines = [OrderItemInline]

    def total_amount_display(self, obj):
        return f"Rs. {str(obj.total_amount)}"
    total_amount_display.short_description = 'මුළු මුදල (රු.)'

    def total_cost_display(self, obj):
        return f"Rs. {str(obj.total_cost)}"
    total_cost_display.short_description = 'මුළු පිරිවැය (රු.)'

    def profit_display(self, obj):
        profit = obj.profit
        color = 'green' if profit > 0 else 'red'
        profit_str = f"Rs. {str(profit)}"
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, profit_str)
    profit_display.short_description = 'ලැබුණු ලාභය (රු.)'

    def created_at_formatted(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')
        return "-"
    created_at_formatted.short_description = 'ඇණවුම් දිනය'

    # 📊 ඩෑෂ්බෝඩ් එක උඩින් "අද දවසේ මුළු ලාභය" පෙන්වන්න හදපු විශේෂ කොටස
    def changelist_view(self, request, extra_context=None):
        today = timezone.now().date()
        
        # අද දවසේ ඕඩර්ස් ටික විතරක් ෆිල්ටර් කරගැනීම
        today_orders = Order.objects.filter(created_at__date=today)
        
        # මුළු විකුණුම් එකතුව සහ මුළු පිරිවැය එකතුව ඩේටාබේස් එකෙන් කාස්ට් කරගැනීම
        aggregates = today_orders.aggregate(
            total_sales=Sum('total_amount'),
            total_cost=Sum('total_cost')
        )
        
        day_sales = aggregates['total_sales'] or 0
        day_cost = aggregates['total_cost'] or 0
        day_profit = day_sales - day_cost # දවසේ ශුද්ධ ලාභය

        # HTML කාඩ් එකක් විදිහට ලස්සනට උඩින්ම පෙන්වීමට සකස් කිරීම
        summary_html = format_html(
            '<div style="padding: 15px; margin-bottom: 20px; background: #264653; border-radius: 8px; color: white; font-family: sans-serif;">'
            '<h3 style="margin: 0 0 10px 0; color: #e9c46a; font-weight: bold;">📊 අද දවසේ සාරාංශය (Today\'s Summary)</h3>'
            '<div style="display: flex; gap: 40px; font-size: 16px;">'
            '<div>💰 මුළු විකුණුම්: <strong style="color: #f4a261;">Rs. {}</strong></div>'
            '<div>📈 අද දවසේ ශුද්ධ ලාභය: <strong style="color: #2a9d8f; background: #fff; padding: 2px 8px; border-radius: 4px;">Rs. {}</strong></div>'
            '</div>'
            '</div>',
            str(day_sales),
            str(day_profit)
        )

        extra_context = extra_context or {}
        extra_context['today_summary_block'] = summary_html
        return super().changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False