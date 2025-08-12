from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),

    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),

    # Address management
    path('addresses/', views.AddressListView.as_view(), name='address_list'),
    # path('addresses/add/', views.AddressCreateView.as_view(), name='address_add'),
    path('addresses/<int:pk>/edit/', views.AddressUpdateView.as_view(), name='address_edit'),
    path('addresses/<int:pk>/delete/', views.AddressDeleteView.as_view(), name='address_delete'),
    path('addresses/<int:pk>/set-default/', views.SetDefaultAddressView.as_view(), name='address_set_default'),

    # Orders
    path('orders/', views.OrderHistoryView.as_view(), name='order_history'),
    path('orders/<slug:order_number>/', views.OrderDetailView.as_view(), name='order_detail'),

    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]