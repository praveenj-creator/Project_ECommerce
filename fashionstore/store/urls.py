from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Customer pages
    path('home/', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/confirm/', views.order_confirm, name='order_confirm'),
    path('orders/', views.user_orders, name='user_orders'),
    path('apply-promo/', views.apply_promo, name='apply_promo'),

    # Admin pages
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-products/', views.admin_products, name='admin_products'),
    path('admin-products/add/', views.admin_product_add, name='admin_product_add'),
    path('admin-products/edit/<int:pk>/', views.admin_product_edit, name='admin_product_edit'),
    path('admin-products/delete/<int:pk>/', views.admin_product_delete, name='admin_product_delete'),
    path('admin-orders/', views.admin_orders, name='admin_orders'),
    path('admin-orders/update/<int:pk>/', views.admin_order_update, name='admin_order_update'),
    path('admin-users/', views.admin_users, name='admin_users'),
    path('admin-users/toggle/<int:pk>/', views.admin_user_toggle, name='admin_user_toggle'),
    path('admin-users/delete/<int:pk>/', views.admin_user_delete, name='admin_user_delete'),
]
