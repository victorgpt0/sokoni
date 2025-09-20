from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import PasswordChangeView as BasePasswordChangeView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from cart.models import Cart, CartItem
from orders.models import Order

from .forms import (
    CustomerAddressForm,
    CustomerProfileForm,
    CustomerRegistrationForm,
    UserProfileForm,
)
from .mixins import CustomerAddressQuerysetMixin, CustomerMixin
from .models import Customer, CustomerAddress


class CustomLoginView(LoginView):
    template_name = "accounts/auth/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse("accounts:dashboard")

    def form_valid(self, form):
        # Store session key before login for cart merging
        session_key = self.request.session.session_key

        # Call parent form_valid to perform login
        response = super().form_valid(form)

        # Always create or get user cart
        user_cart, created = Cart.objects.get_or_create(
            customer=self.request.user.customer, defaults={"session_key": None}
        )

        # Merge cart after successful login if anonymous cart exists
        if session_key:
            try:
                anonymous_cart = Cart.objects.get(
                    session_key=session_key, customer=None
                )
                if anonymous_cart.cart_items.exists():
                    # Merge cart items
                    for item in anonymous_cart.cart_items.all():
                        user_item, created = CartItem.objects.get_or_create(
                            cart=user_cart,
                            product=item.product,
                            defaults={"quantity": item.quantity},
                        )

                        if not created:
                            # Add quantities if item already exists
                            user_item.quantity = min(
                                user_item.quantity + item.quantity,
                                getattr(settings, "CART_ITEM_MAX_QUANTITY", 99),
                            )
                            user_item.save()

                    # Delete anonymous cart
                    anonymous_cart.delete()

                    messages.success(
                        self.request, "Your cart items have been merged successfully."
                    )

            except Cart.DoesNotExist:
                pass

        return response


class CustomLogoutView(LogoutView):
    next_page = "home"

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "You have been logged out successfully.")
        return super().dispatch(request, *args, **kwargs)


class RegisterView(CreateView):
    form_class = CustomerRegistrationForm
    template_name = "accounts/auth/register.html"
    success_url = reverse_lazy("accounts:dashboard")

    def form_valid(self, form):
        # Store session key before registration for cart merging
        session_key = self.request.session.session_key

        response = super().form_valid(form)

        Customer.objects.create(user=self.object)

        login(self.request, self.object)

        # Always create or get user cart
        user_cart, created = Cart.objects.get_or_create(
            customer=self.request.user.customer, defaults={"session_key": None}
        )

        # Merge cart after successful registration and login if anonymous cart exists
        if session_key:
            try:
                anonymous_cart = Cart.objects.get(
                    session_key=session_key, customer=None
                )
                if anonymous_cart.cart_items.exists():
                    # Merge cart items
                    for item in anonymous_cart.cart_items.all():
                        user_item, created = CartItem.objects.get_or_create(
                            cart=user_cart,
                            product=item.product,
                            defaults={"quantity": item.quantity},
                        )

                        if not created:
                            # Add quantities if item already exists
                            user_item.quantity = min(
                                user_item.quantity + item.quantity,
                                getattr(settings, "CART_ITEM_MAX_QUANTITY", 99),
                            )
                            user_item.save()

                    # Delete anonymous cart
                    anonymous_cart.delete()

                    messages.success(
                        self.request,
                        "Welcome! Your account has been created successfully and your cart items have been merged.",
                    )
                else:
                    messages.success(
                        self.request,
                        "Welcome! Your account has been created successfully.",
                    )

            except Cart.DoesNotExist:
                messages.success(
                    self.request, "Welcome! Your account has been created successfully."
                )

        return response


class PasswordChangeView(LoginRequiredMixin, CustomerMixin, BasePasswordChangeView):
    template_name = "accounts/auth/password_change.html"
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form):
        messages.success(self.request, "Your password has been changed successfully.")
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, CustomerMixin, TemplateView):
    template_name = "accounts/profile/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_customer()
        context["customer"] = customer
        context["recent_orders"] = Order.objects.filter(customer=customer).order_by(
            "-created_at"
        )[:5]
        return context


class ProfileEditView(LoginRequiredMixin, CustomerMixin, TemplateView):
    template_name = "accounts/profile/profile_edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_customer()

        if self.request.method == "POST":
            user_form = UserProfileForm(self.request.POST, instance=customer.user)
            customer_form = CustomerProfileForm(self.request.POST, instance=customer)
        else:
            user_form = UserProfileForm(instance=customer.user)
            customer_form = CustomerProfileForm(instance=customer)

        context["user_form"] = user_form
        context["customer_form"] = customer_form
        context["customer"] = customer
        return context

    def post(self, request, *args, **kwargs):
        customer = self.get_customer()
        user_form = UserProfileForm(request.POST, instance=customer.user)
        customer_form = CustomerProfileForm(request.POST, instance=customer)

        if user_form.is_valid() and customer_form.is_valid():
            user_form.save()
            customer_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("accounts:profile")

        # If forms are invalid, re-render with errors
        context = self.get_context_data()
        context["user_form"] = user_form
        context["customer_form"] = customer_form
        return self.render_to_response(context)


class AddressListView(CustomerAddressQuerysetMixin, ListView):
    model = CustomerAddress
    template_name = "accounts/address/address_list.html"


class AddressCreateView(CustomerMixin, CreateView):
    model = CustomerAddress
    form_class = CustomerAddressForm
    template_name = "accounts/address/address_form.html"
    success_url = reverse_lazy("accounts:address_list")

    def form_valid(self, form):
        customer = self.get_customer()
        form.instance.customer = customer

        if (
            form.instance.is_default
            or not CustomerAddress.objects.filter(customer=customer).exists()
        ):
            CustomerAddress.objects.filter(
                customer=customer, type=form.instance.type, is_default=True
            ).update(is_default=False)
            form.instance.is_default = True

        messages.success(self.request, "Address has been added successfully.")
        return super().form_valid(form)


class AddressUpdateView(CustomerAddressQuerysetMixin, UpdateView):
    model = CustomerAddress
    form_class = CustomerAddressForm
    template_name = "accounts/address/address_form.html"
    success_url = reverse_lazy("accounts:address_list")

    def form_valid(self, form):
        if form.instance.is_default:
            CustomerAddress.objects.filter(
                customer=form.instance.customer,
                type=form.instance.type,
                is_default=True,
            ).exclude(pk=form.instance.pk).update(is_default=False)

        messages.success(self.request, "Address has been updated successfully.")
        return super().form_valid(form)


class AddressDeleteView(CustomerAddressQuerysetMixin, DeleteView):
    model = CustomerAddress
    template_name = "accounts/address/address_confirm_delete.html"
    success_url = reverse_lazy("accounts:address_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Address has been deleted successfully.")
        return super().delete(request, *args, **kwargs)


class SetDefaultAddressView(CustomerMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        customer = self.get_customer()
        address = get_object_or_404(CustomerAddress, pk=kwargs["pk"], customer=customer)

        CustomerAddress.objects.filter(
            customer=customer, type=address.type, is_default=True
        ).update(is_default=False)

        address.is_default = True
        address.save()

        messages.success(
            request, f"{address.type.title()} address has been set successfully."
        )

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True})

        return redirect("accounts:address_list")


class OrderHistoryView(CustomerMixin, ListView):
    model = Order
    template_name = "accounts/orders/order_history.html"
    context_object_name = "orders"

    def get_queryset(self):
        customer = self.get_customer()
        return Order.objects.filter(customer=customer).order_by("-created_at")


class OrderDetailView(CustomerMixin, DetailView):
    model = Order
    template_name = "accounts/orders/order_detail.html"
    context_object_name = "order"
    slug_field = "order_number"
    slug_url_kwarg = "order_number"

    def get_queryset(self):
        customer = self.get_customer()
        return Order.objects.filter(customer=customer)


class DashboardView(CustomerMixin, TemplateView):
    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_customer()
        context.update(
            {
                "customer": customer,
                "recent_orders": Order.objects.filter(customer=customer).order_by(
                    "-created_at"
                )[:5],
                "total_orders": Order.objects.filter(customer=customer).count(),
                "pending_orders": Order.objects.filter(
                    customer=customer, status__in=["pending", "processing"]
                ).count(),
                "default_billing": CustomerAddress.objects.filter(
                    customer=customer, type="billing", is_default=True
                ).first(),
                "default_shipping": CustomerAddress.objects.filter(
                    customer=customer, type="shipping", is_default=True
                ).first(),
            }
        )

        return context
