from django.contrib import admin
from .models import Category, RawMaterial, Product, Supplier, Customer, Order, OrderItem, PurchaseOrder, PurchaseOrderItem, ProductionBatch, Expense, Worker

admin.site.register(Category)
admin.site.register(RawMaterial)
admin.site.register(Product)
admin.site.register(Supplier)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderItem)
admin.site.register(ProductionBatch)
admin.site.register(Expense)
admin.site.register(Worker)

admin.site.site_header = "Agarbatti House Admin"
admin.site.site_title = "Agarbatti House"
