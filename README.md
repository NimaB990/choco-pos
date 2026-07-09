# Choco Paradise POS System

Production-ready Web Point of Sale system built with Django, Bootstrap 5, and JavaScript.

## Features

- **Modern Billing UI**: Clean dashboard with sidebar receipt layout
- **Real-time Calculations**: Instant cash & change calculator (දුන් මුදල & ඉතිරි මුදල)
- **Thermal Printer Support**: Receipt formatting via `@media print` for 80mm thermal printers
- **Barcode Scanning**: Hardware scanner integration with instant product lookup
- **Stock Management**: Automatic stock deduction on checkout, profit tracking
- **Product Management**: ImageField support, cost/selling price, profit margin metrics
- **Order History**: Complete order tracking with item details and timestamps

## Tech Stack

- **Backend**: Django 5.0+ (PostgreSQL via dj-database-url / Supabase)
- **Frontend**: Bootstrap 5.3, JavaScript Fetch API
- **Database**: PostgreSQL (configured via DATABASE_URL environment variable)
- **Media**: Django media files for product images

## Project Structure

```
choco_project/
├── settings.py          # Production-ready Django settings
├── urls.py              # URL routing
├── wsgi.py              # WSGI application
├── asgi.py              # ASGI application
pos_core/
├── models.py            # Product, Order, OrderItem models with optimizations
├── views.py             # JSON APIs for checkout, barcode lookup, products
├── admin.py             # Django admin interface for management
├── templates/
│   └── pos_page.html    # Modern POS UI with Bootstrap 5
├── migrations/          # Database migrations
templates/               # Project-wide templates
manage.py               # Django management script
```

## Installation & Setup

### 1. Clone or Navigate to Project
```bash
cd f:\Choco Pos
```

### 2. Create Virtual Environment (Already Done)
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install django dj-database-url pillow
```

### 4. Database Configuration

**Option A: Local SQLite (Development)**
```bash
python manage.py migrate
```

**Option B: Supabase PostgreSQL (Production)**
Set environment variable:
```bash
$env:DATABASE_URL="postgresql://user:password@db.supabase.co:5432/postgres"
python manage.py migrate
```

### 5. Create Superuser (Admin Access)
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Visit: `http://localhost:8000`

Admin Panel: `http://localhost:8000/admin`

## API Endpoints

### `GET /api/products/`
Returns all active products in JSON format.

### `GET /api/barcode/?code=<barcode>`
Lookup product by barcode code.

### `POST /api/checkout/`
Process order checkout with cart items.

**Request:**
```json
{
  "cart": [{"id": 1, "qty": 2}, {"id": 2, "qty": 1}],
  "cash_received": 5000
}
```

**Response:**
```json
{
  "success": true,
  "order_number": "CP2501041234567",
  "total_amount": 4500,
  "cash_received": 5000,
  "change_given": 500,
  "timestamp": "2025-01-04 12:34:56",
  "items": [...]
}
```

## Environment Variables

```bash
DEBUG=True                                          # Development only
SECRET_KEY=your-secret-key                         # Change in production!
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
DATABASE_URL=postgresql://user:pass@host/db
CSRF_TRUSTED_ORIGINS=http://localhost,http://yourdomain.com
```

## Production Deployment

### Gunicorn Setup
```bash
pip install gunicorn
gunicorn choco_project.wsgi:application --bind 0.0.0.0:8000
```

### Nginx Configuration (reverse proxy)
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Security Checklist
- Set `DEBUG=False`
- Use strong `SECRET_KEY`
- Enable `CSRF_COOKIE_SECURE=True`
- Enable `SESSION_COOKIE_SECURE=True`
- Use HTTPS only
- Configure `ALLOWED_HOSTS` properly

## Admin Panel Features

- **Products**: Add/edit products with images, pricing, stock
- **Orders**: View complete order history with profit metrics
- **Profit Analysis**: See profit margins and daily profits
- **Stock Tracking**: Monitor inventory levels with color-coded alerts

## Thermal Printer Setup

The receipt layout is optimized for 80mm thermal printers:

1. **Windows**: Printer auto-detected
2. **Linux**: Configure CUPS printer
3. **Mac**: System Preferences → Printers

Receipt prints via browser `Ctrl+P` (or `Cmd+P` on Mac).

## Database Models

### Product
- `name`, `barcode` (unique), `image`
- `cost_price`, `selling_price`
- `stock`, `is_active`
- `profit_margin` (calculated property)

### Order
- `order_number` (auto-generated: CP + timestamp)
- `total_amount`, `total_cost`
- `cash_received`, `change_given`
- `profit` (calculated property)

### OrderItem
- Links `Order` ↔ `Product`
- Stores `quantity`, `unit_price`, `unit_cost`
- `subtotal` (calculated property)

## Performance Optimizations

- **Database Indexing**: Strategic indexes on frequently queried fields
- **Query Optimization**: `select_for_update()` for concurrent transactions
- **Caching**: Built-in Django ORM caching via `@property` methods
- **Media Handling**: Pillow-optimized image processing
- **API Responses**: Minimal JSON serialization

## Troubleshooting

**No products showing?**
- Check `is_active=True` and `stock > 0`
- Verify images are in `/media/products/`

**Barcode scan not working?**
- Ensure barcode field is populated in product
- Test with direct URL: `/api/barcode/?code=123`

**Database connection error?**
- Verify `DATABASE_URL` environment variable
- Test connection: `python manage.py dbshell`

**Receipt not printing?**
- Check printer is set as default
- Try `Ctrl+Shift+P` for print preview

## Support

For issues or enhancements, check Django documentation:
- https://docs.djangoproject.com
- https://getbootstrap.com/docs
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
