from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView as BasePasswordChangeView
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, ListView, DeleteView, DetailView
from .forms import CustomerRegistrationForm, CustomerProfileForm, CustomerAddressForm
from .models import Customer, CustomerAddress
from orders.models import Order
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from .mixins import CustomerMixin, CustomerAddressQuerysetMixin

class CustomLoginView(LoginView):
    template_name = 'accounts/auth/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse('accounts:dashboard')
    
class CustomLogoutView(LogoutView):
    next_page = 'home'
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)

class RegisterView(CreateView):
    form_class = CustomerRegistrationForm
    template_name = 'accounts/auth/register.html'
    success_url = reverse_lazy('accounts:dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)

        Customer.objects.create(user=self.object)

        login(self.request, self.object)
        messages.success(self.request, 'Welcome! Your account has been created successfully.')

        return response

class PasswordChangeView(CustomerMixin, BasePasswordChangeView):
    template_name = 'accounts/auth/password_change.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed successfully.')
        return super().form_valid(form)
    
class ProfileView(CustomerMixin, TemplateView):
    template_name = 'accounts/profile/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_customer()
        context['customer'] = customer
        context['recent_orders'] = Order.objects.filter(customer=customer).order_by('-created_at')[:5]
        return context

class ProfileEditView(CustomerMixin, UpdateView):
    model = Customer
    form_class = CustomerProfileForm
    template_name = 'accounts/profile/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        customer = self.get_customer()
        return customer

    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully.')
        return super().form_valid(form)
    
class AddressListView(CustomerAddressQuerysetMixin, ListView):
    model = CustomerAddress
    form_class = CustomerAddressForm
    template_name = 'accounts/address/address_list.html'
    success_url = reverse_lazy('accounts:address_list')

    def form_valid(self, form):
        customer = self.get_customer()
        form.instance.customer = customer

        if form.instance.is_default or not CustomerAddress.objects.filter(customer=customer).exists():
            CustomerAddress.objects.filter(
                customer=customer, 
                type=form.instance.type,
                is_default=True
                ).update(is_default=False)
            form.instance.is_default = True

        messages.success(self.request, 'Address has been added successfully.')
        return super().form_valid(form)

class AddressUpdateView(CustomerAddressQuerysetMixin, UpdateView):
    model = CustomerAddress
    form_class = CustomerAddressForm
    template_name = 'accounts/address/address_form.html'
    success_url = reverse_lazy('accounts:address_list')

    def form_valid(self, form):
        if form.instance.is_default:
            CustomerAddress.objects.filter(
                customer=form.instance.customer, 
                type=form.instance.type,
                is_default=True
            ).exclude(pk=form.instance.pk).update(is_default=False)
        
        messages.success(self.request, 'Address has been updated successfully.')
        return super().form_valid(form)

class AddressDeleteView(CustomerAddressQuerysetMixin, DeleteView):
    model = CustomerAddress
    template_name = 'accounts/address/address_confirm_delete.html'
    success_url = reverse_lazy('accounts:address_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Address has been deleted successfully.')
        return super().delete(request, *args, **kwargs)
    
class SetDefaultAddressView(CustomerMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        customer = self.get_customer()
        address = get_object_or_404(CustomerAddress, pk=kwargs['pk'], customer=customer)

        CustomerAddress.objects.filter(
            customer=customer, 
            type=address.type,
            is_default=True
        ).update(is_default=False)

        address.is_default = True
        address.save()
        
        messages.success(request, f'{address.type.title()} address has been set successfully.')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        

        return redirect('accounts:address_list')
    
class OrderHistoryView(CustomerMixin, ListView):
    model = Order
    template_name = 'accounts/orders/order_history.html'
    context_object_name = 'orders'

    def get_queryset(self):
        customer = self.get_customer()
        return Order.objects.filter(customer=customer).order_by('-created_at')
    

class OrderDetailView(CustomerMixin, DetailView):
    model = Order
    template_name = 'accounts/orders/order_detail.html'
    context_object_name = 'order'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'
    
    def get_queryset(self):
        customer = self.get_customer()
        return Order.objects.filter(customer=customer)

class DashboardView(CustomerMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_customer()
        context.update({
            'customer': customer,
            'recent_orders': Order.objects.filter(customer=customer).order_by('-created_at')[:5],
            'total_orders': Order.objects.filter(customer=customer).count(),
            'pending_orders': Order.objects.filter(
                customer=customer,
                status__in=['pending', 'processing']
            ).count(),
            'default_billing': CustomerAddress.objects.filter(
                customer=customer, 
                type='billing',
                is_default=True
            ).first(),
            'default_shipping': CustomerAddress.objects.filter(
                customer=customer, 
                type='shipping',
                is_default=True
            ).first()
        })

        return context