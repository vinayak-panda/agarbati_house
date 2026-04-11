from django.urls import path
from . import views

urlpatterns = [
    path('', lambda r: __import__('django.shortcuts', fromlist=['redirect']).redirect('dashboard'), name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Products
    path('products/', views.products, name='products'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('api/products/<int:pk>/', views.product_api, name='product_api'),
    path('api/products/search/', views.search_products_api, name='search_products_api'),

    # Categories
    path('categories/', views.categories, name='categories'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),

    # Raw Materials
    path('raw-materials/', views.raw_materials, name='raw_materials'),
    path('raw-materials/add/', views.add_raw_material, name='add_raw_material'),
    path('raw-materials/edit/<int:pk>/', views.edit_raw_material, name='edit_raw_material'),
    path('raw-materials/delete/<int:pk>/', views.delete_raw_material, name='delete_raw_material'),

    # Suppliers
    path('suppliers/', views.suppliers, name='suppliers'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/edit/<int:pk>/', views.edit_supplier, name='edit_supplier'),
    path('suppliers/delete/<int:pk>/', views.delete_supplier, name='delete_supplier'),

    # Customers
    path('customers/', views.customers, name='customers'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),

    # Orders
    path('orders/', views.orders, name='orders'),
    path('orders/new/', views.new_order, name='new_order'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/pdf/', views.order_pdf, name='order_pdf'),

    # Purchase Orders
    path('purchase-orders/', views.purchase_orders, name='purchase_orders'),
    path('purchase-orders/add/', views.add_purchase_order, name='add_purchase_order'),
    path('purchase-orders/<int:pk>/receive/', views.receive_purchase_order, name='receive_purchase_order'),
    path('purchase-orders/<int:pk>/cancel/', views.cancel_purchase_order, name='cancel_purchase_order'),

    # Production
    path('production/', views.production, name='production'),
    path('production/add/', views.add_production, name='add_production'),

    # Expenses
    path('expenses/', views.expenses, name='expenses'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/delete/<int:pk>/', views.delete_expense, name='delete_expense'),

    # Workers
    path('workers/', views.workers, name='workers'),
    path('workers/add/', views.add_worker, name='add_worker'),
    path('workers/edit/<int:pk>/', views.edit_worker, name='edit_worker'),
    path('workers/delete/<int:pk>/', views.delete_worker, name='delete_worker'),

    # Reports
    path('reports/', views.reports, name='reports'),
]
