from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from pos_core import views as pos_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', pos_views.pos_page, name='pos_page'),
    path('api/products/', pos_views.product_list_api, name='product_list_api'),
    path('api/barcode/', pos_views.barcode_lookup_api, name='barcode_lookup_api'),
    path('api/checkout/', pos_views.checkout_api, name='checkout_api'),
    path('api/live-stock/', pos_views.get_live_stock_api, name='get_live_stock_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
