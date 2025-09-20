from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, ProductImage, ProductReview


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = (
        "image_preview",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: auto; height: 50px;"/>', obj.image.url
            )
        return "No image"

    image_preview.short_description = "Preview"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")
    ordering = ("-created_at",)
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "image", "is_active")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
        (
            "Audit Information",
            {"fields": ("created_by", "updated_by"), "classes": ("collapse",)},
        ),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "stock_quantity",
        "is_active",
        "is_featured",
        "created_at",
        "updated_at",
    )
    list_filter = ("category", "is_active", "is_featured", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description", "category__name", "sku")
    ordering = ("-created_at",)
    inlines = [ProductImageInline]
    readonly_fields = (
        "created_at",
        "updated_at",
        "discount_percentage_display",
        "is_on_sale_display",
        "is_in_stock_display",
        "created_by",
        "updated_by",
    )

    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "category")}),
        (
            "Pricing",
            {
                "fields": (
                    "price",
                    "compare_price",
                    "discount_percentage_display",
                    "is_on_sale_display",
                )
            },
        ),
        (
            "Inventory",
            {
                "fields": (
                    "sku",
                    "stock_quantity",
                    "is_in_stock_display",
                    "weight",
                    "dimensions",
                )
            },
        ),
        ("Status", {"fields": ("is_active", "is_featured", "is_digital")}),
        (
            "SEO",
            {
                "fields": ("meta_title", "meta_description", "meta_keywords"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
        (
            "Audit Information",
            {"fields": ("created_by", "updated_by"), "classes": ("collapse",)},
        ),
    )

    def discount_percentage_display(self, obj):
        return obj.discount_percentage

    discount_percentage_display.short_description = "Discount %"

    def is_on_sale_display(self, obj):
        return obj.is_on_sale

    is_on_sale_display.boolean = True

    def is_in_stock_display(self, obj):
        return obj.is_in_stock

    is_in_stock_display.boolean = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("category")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "is_primary", "order", "image_preview", "created_at")
    list_filter = ("is_primary", "created_at", "updated_at")
    list_editable = ("is_primary", "order")
    search_fields = ("product__name", "alt_text")
    readonly_fields = (
        "created_at",
        "updated_at",
        "image_preview",
        "created_by",
        "updated_by",
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: auto; height: 50px;"/>', obj.image.url
            )
        return "No image"

    image_preview.short_description = "Preview"


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "customer", "rating", "created_at")
    list_filter = ("rating", "created_at", "updated_at")
    search_fields = ("product__name", "customer__full_name", "title", "comment")
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    fieldsets = (
        (None, {"fields": ("product", "customer", "rating", "title", "comment")}),
        ("Status", {"fields": ("is_approved",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
        (
            "Audit Information",
            {"fields": ("created_by", "updated_by"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product", "customer__user")
