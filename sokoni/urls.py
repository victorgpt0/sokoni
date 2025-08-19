"""
URL configuration for sokoni project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),

    # Main apps
    path('products/', include('products.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('coupons/', include('coupons.urls')),
    path('payments/', include('payments.urls')),
    path('wishlist/', include('wishlist.urls', namespace='wishlist')),
]

# Custom admin site headers
admin.site.site_header = "Ecommerce Admin"
admin.site.site_title = "Ecommerce Admin Portal"
admin.site.index_title = "Welcome to Ecommerce Administration"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)