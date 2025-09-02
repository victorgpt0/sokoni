from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Category, ProductImage
from django.utils.text import slugify
import uuid

class ProductForm(forms.ModelForm):
    """Form for creating and editing products"""
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'price', 'compare_price',
            'stock_quantity', 'weight', 'dimensions', 'is_active',
            'is_featured', 'is_digital', 'meta_title', 'meta_description',
            'meta_keywords'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter product description'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'compare_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'dimensions': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 10x5x2 inches'
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO title (optional)'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'SEO description (optional)'
            }),
            'meta_keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO keywords (optional)'
            }),
        }
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise ValidationError('Price must be greater than zero.')
        return price
    
    def clean_compare_price(self):
        compare_price = self.cleaned_data.get('compare_price')
        price = self.cleaned_data.get('price')
        
        if compare_price and price and compare_price <= price:
            raise ValidationError('Compare price must be greater than the regular price.')
        return compare_price
    
    def clean_stock_quantity(self):
        stock_quantity = self.cleaned_data.get('stock_quantity')
        if stock_quantity and stock_quantity < 0:
            raise ValidationError('Stock quantity cannot be negative.')
        return stock_quantity

class ProductImageForm(forms.ModelForm):
    """Form for adding product images"""
    
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_primary', 'order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alt text for accessibility'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (5MB limit)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Image file size must be less than 5MB.')
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if image.content_type not in allowed_types:
                raise ValidationError('Only JPEG, PNG, GIF, and WebP images are allowed.')
        
        return image

class ProductImageFormSet(forms.BaseModelFormSet):
    """Formset for managing multiple product images"""
    
    def clean(self):
        super().clean()
        
        # Check if at least one image is marked as primary
        primaries = [
            form.cleaned_data.get("is_primary")
            for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get("DELETE", False)
        ]
        if primaries.count(True) == 0:
            raise ValidationError("At least one image must be marked as primary.")
        elif primaries.count(True) > 1:
            raise ValidationError("Only one image can be marked as primary.")


# Create formset factory
ProductImageFormSet = forms.modelformset_factory(
    ProductImage,
    form=ProductImageForm,
    formset=ProductImageFormSet,
    extra=1,
    can_delete=True
)
