from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Customer, CustomerAddress

class AddressInline(admin.TabularInline):
    model = CustomerAddress
    extra = 0
    fields = ('type', 'first_name', 'last_name', 'company', 'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country', 'is_default')
    readonly_fields = ('type','created_at', 'updated_at', 'created_by', 'updated_by',)

class CustomerInline(admin.StackedInline):
    model = Customer
    fk_name = 'user'
    can_delete = False
    verbose_name_plural = 'Customer Profile'
    fields = ('phone_number', 'date_of_birth', 'gender')

class CustomUserAdmin(UserAdmin):
    inlines = (CustomerInline,)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user_email', 'phone_number', 'date_of_birth', 'created_at')
    list_filter = ('gender', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by',)
    inlines = (AddressInline,)

    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        ('Personal Info', {
            'fields': ('phone_number', 'date_of_birth', 'gender')
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

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'type', 'full_address', 'city', 'state', 'country', 'is_default')
    list_filter = ('type', 'country', 'is_default', 'state', 'created_at')
    search_fields = ('customer__user__username', 'first_name', 'last_name', 'address_line_1', 'city', 'postal_code')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by',)

    fieldsets = (
        (None, {
            'fields': ('customer', 'type', 'is_default')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'company')
        }),
        ('Address Details', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country')
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
    
    def customer_name(self, obj):
        return obj.customer.full_name
    customer_name.short_description = 'Customer Name'
    customer_name.admin_order_field = 'customer__user__last_name'

    def full_address(self, obj):
        return f"{obj.address_line_1}, {obj.address_line_2 or ''}".strip(', ')
    full_address.short_description = 'Address'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer__user')
    
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)