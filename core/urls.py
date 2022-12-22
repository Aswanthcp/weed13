from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace="accounts")),
    path('store/', include('store.urls', namespace="store")),
    path('cart/', include('cart.urls', namespace="cart")),
    path('orders/', include('orders.urls', namespace="orders")),
    path('wishlist/', include('wishlist.urls', namespace="wishlists")),
    path('admins/',include('customadmin.urls', namespace="customadmin")),
    path('', views.home, name='home'),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
