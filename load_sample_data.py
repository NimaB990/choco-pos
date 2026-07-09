import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'choco_project.settings')
django.setup()

from pos_core.models import Product
from decimal import Decimal

SAMPLE_PRODUCTS = [
    {
        'name': 'Dark Chocolate Bar',
        'barcode': 'CP001',
        'cost_price': Decimal('150'),
        'selling_price': Decimal('250'),
        'stock': 50,
    },
    {
        'name': 'Milk Chocolate Truffle',
        'barcode': 'CP002',
        'cost_price': Decimal('200'),
        'selling_price': Decimal('350'),
        'stock': 40,
    },
    {
        'name': 'Choco Chip Cookie',
        'barcode': 'CP003',
        'cost_price': Decimal('50'),
        'selling_price': Decimal('100'),
        'stock': 100,
    },
    {
        'name': 'Hazelnut Chocolate Spread',
        'barcode': 'CP004',
        'cost_price': Decimal('400'),
        'selling_price': Decimal('650'),
        'stock': 20,
    },
    {
        'name': 'White Chocolate Mousse',
        'barcode': 'CP005',
        'cost_price': Decimal('120'),
        'selling_price': Decimal('200'),
        'stock': 35,
    },
    {
        'name': 'Choco Fudge Cake Slice',
        'barcode': 'CP006',
        'cost_price': Decimal('180'),
        'selling_price': Decimal('300'),
        'stock': 60,
    },
    {
        'name': 'Premium Cocoa Powder',
        'barcode': 'CP007',
        'cost_price': Decimal('300'),
        'selling_price': Decimal('500'),
        'stock': 25,
    },
    {
        'name': 'Choco Brownie',
        'barcode': 'CP008',
        'cost_price': Decimal('80'),
        'selling_price': Decimal('150'),
        'stock': 75,
    },
]

def load_sample_data():
    print("Loading sample products...")
    for product_data in SAMPLE_PRODUCTS:
        product, created = Product.objects.get_or_create(
            barcode=product_data['barcode'],
            defaults={
                'name': product_data['name'],
                'cost_price': product_data['cost_price'],
                'selling_price': product_data['selling_price'],
                'stock': product_data['stock'],
                'is_active': True,
            }
        )
        status = "Created" if created else "Already exists"
        print(f"  {status}: {product.name} (Barcode: {product.barcode})")
    
    print(f"\nTotal products: {Product.objects.count()}")
    print("Sample data loaded successfully!")

if __name__ == '__main__':
    load_sample_data()
