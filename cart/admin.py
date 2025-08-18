from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('total_price', 'created_at', 'updated_at', 'created_by', 'updated_by',)
    fields = ('product', 'quantity', 'total_price', 'created_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_owner', 'total_items', 'subtotal', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('customer__user__username', 'customer__user__email', 'session_key')
    readonly_fields = ('total_items', 'subtotal', 'created_at', 'updated_at', 'created_by', 'updated_by',)
    inlines = [CartItemInline]
    
    fieldsets = (
        (None, {
            'fields': ('customer', 'session_key')
        }),
        ('Summary', {
            'fields': ('total_items', 'subtotal')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def cart_owner(self, obj):
        if obj.customer:
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                obj.customer.full_name,
                obj.customer.user.email
            )
        return format_html(
            '<em>Anonymous</em><br><small>{}</small>',
            obj.session_key[:20] + '...' if obj.session_key and len(obj.session_key) > 20 else obj.session_key
        )
    cart_owner.short_description = 'Owner'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer__user')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart_owner', 'product', 'quantity', 'total_price', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('cart__customer__user__username', 'product__name', 'cart__session_key')
    readonly_fields = ('total_price', 'created_at', 'updated_at', 'created_by', 'updated_by',)
    
    fieldsets = (
        (None, {
            'fields': ('cart', 'product', 'quantity')
        }),
        ('Pricing', {
            'fields': ('total_price',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def cart_owner(self, obj):
        if obj.cart.customer:
            return obj.cart.customer.full_name
        return f"Anonymous ({obj.cart.session_key[:8]}...)"
    cart_owner.short_description = 'Cart Owner'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cart__customer__user', 'product')