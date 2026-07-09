from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Product(models.Model):
    name = models.CharField(max_length=150, db_index=True, verbose_name="චොකලට් නම")
    barcode = models.CharField(
        max_length=64, 
        unique=True, 
        blank=True, 
        null=True, 
        db_index=True,
        verbose_name="බාර්කෝඩ් එක (Barcode)"
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="ඡායාරූපය")
    cost_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name="ගත් මිල (රු.)"
    )
    selling_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name="විකුණුම් මිල (රු.)"
    )
    stock = models.PositiveIntegerField(default=0, db_index=True, verbose_name="තොග ප්‍රමාණය")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="ක්‍රියාකාරී තත්ත්වය")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="ඇතුළත් කළ දිනය")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="යාවත්කාලීන කළ දිනය")

    class Meta:
        ordering = ['-updated_at', 'name']
        verbose_name = "භාණ්ඩය"
        verbose_name_plural = "චොකලට් / භාණ්ඩ"
        indexes = [
            models.Index(fields=['is_active', 'stock']),
            models.Index(fields=['barcode']),
        ]

    def __str__(self):
        return str(self.name)

    @property
    def profit_margin(self):
        if self.selling_price:
            return round(((self.selling_price - self.cost_price) / self.selling_price) * 100, 2)
        return 0


class Order(models.Model):
    order_number = models.CharField(max_length=20, unique=True, editable=False, db_index=True, verbose_name="ඕඩර් අංකය")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="මුළු මුදල (රු.)")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="මුළු පිරිවැය (රු.)")
    cash_received = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="ලැබුණු මුදල (රු.)")
    change_given = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="ඉතිරි මුදල (රු.)")
    created_at = models.DateTimeField(default=timezone.now, db_index=True, verbose_name="දිනය සහ වේලාව")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "ඇණවුම"
        verbose_name_plural = "ඇණවුම් (Orders)"
        indexes = [
            models.Index(fields=['-created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"CP{timezone.now().strftime('%y%m%d%H%M%S')}"
        super().save(*args, **kwargs)

    @property
    def profit(self):
        return self.total_amount - self.total_cost

    def __str__(self):
        return f"Order: {str(self.order_number)}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="ඇණවුම")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="චොකලට් වර්ගය")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="ප්‍රමාණය")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ඒකක මිල")
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ඒකක පිරිවැය")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="ඇතුළත් කළ දිනය")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "ඇණවුම් අයිතමය"
        verbose_name_plural = "ඇණවුම් කරන ලද චොකලට්"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{str(self.product.name)} x {str(self.quantity)}"