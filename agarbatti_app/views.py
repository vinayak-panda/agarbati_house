from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import date, timedelta
import json
import io

from .models import (
    Category, RawMaterial, Product, Supplier, Customer,
    Order, OrderItem, PurchaseOrder, PurchaseOrderItem,
    ProductionBatch, Expense, Worker
)


def render_jinja(request, template, context=None):
    """Helper to render Jinja2 templates with messages and csrf"""
    from django.middleware.csrf import get_token
    from django.utils.html import format_html
    ctx = context or {}
    ctx['messages_list'] = list(messages.get_messages(request))
    csrf_token_value = get_token(request)
    ctx['csrf_input'] = f'<input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token_value}">'
    return render(request, template, ctx, using='jinja2')


# ===================== AUTH =====================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password!')
    return render_jinja(request, 'agarbatti_app/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ===================== DASHBOARD =====================

@login_required
def dashboard(request):
    today = date.today()
    month_start = today.replace(day=1)

    today_orders = Order.objects.filter(created_at__date=today, status='completed')
    today_sales = today_orders.aggregate(t=Sum('total'))['t'] or 0
    month_orders = Order.objects.filter(created_at__date__gte=month_start, status='completed')
    month_sales = month_orders.aggregate(t=Sum('total'))['t'] or 0

    total_products = Product.objects.count()
    total_customers = Customer.objects.count()
    total_workers = Worker.objects.filter(is_active=True).count()
    low_stock_products = Product.objects.filter(packs_in_stock__lte=20)
    low_stock_materials = RawMaterial.objects.filter(quantity__lte=10)
    month_expenses = Expense.objects.filter(date__gte=month_start).aggregate(t=Sum('amount'))['t'] or 0

    monthly_data = []
    for i in range(5, -1, -1):
        d = today - timedelta(days=i * 30)
        ms = d.replace(day=1)
        me = today if i == 0 else (ms + timedelta(days=32)).replace(day=1)
        sales = Order.objects.filter(
            created_at__date__gte=ms, created_at__date__lte=me, status='completed'
        ).aggregate(t=Sum('total'))['t'] or 0
        monthly_data.append({'month': ms.strftime('%b %Y'), 'sales': float(sales)})

    recent_orders = Order.objects.select_related('customer').order_by('-created_at')[:5]
    recent_batches = ProductionBatch.objects.select_related('product').order_by('-created_at')[:5]

    return render_jinja(request, 'agarbatti_app/dashboard.html', {
        'today_sales': today_sales,
        'today_orders': today_orders.count(),
        'month_sales': month_sales,
        'month_expenses': month_expenses,
        'total_products': total_products,
        'total_customers': total_customers,
        'total_workers': total_workers,
        'low_stock_products': low_stock_products,
        'low_stock_materials': low_stock_materials,
        'monthly_data': json.dumps(monthly_data),
        'recent_orders': recent_orders,
        'recent_batches': recent_batches,
    })


# ===================== PRODUCTS =====================

@login_required
def products(request):
    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    filter_type = request.GET.get('filter', '')
    qs = Product.objects.select_related('category').all()
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(fragrance__icontains=search))
    if category_id:
        qs = qs.filter(category_id=category_id)
    if filter_type == 'low_stock':
        qs = qs.filter(packs_in_stock__lte=20)
    categories = Category.objects.all()
    return render_jinja(request, 'agarbatti_app/products.html', {'products': qs, 'categories': categories})


@login_required
def add_product(request):
    if request.method == 'POST':
        Product.objects.create(
            name=request.POST['name'],
            category_id=request.POST.get('category') or None,
            fragrance=request.POST.get('fragrance'),
            length_cm=float(request.POST.get('length_cm', 20)),
            burn_time_min=int(request.POST.get('burn_time_min', 30)),
            sticks_per_pack=int(request.POST.get('sticks_per_pack', 10)),
            packs_in_stock=int(request.POST.get('packs_in_stock', 0)),
            purchase_price=float(request.POST['purchase_price']),
            selling_price=float(request.POST['selling_price']),
            low_stock_threshold=int(request.POST.get('low_stock_threshold', 20)),
            description=request.POST.get('description'),
        )
        messages.success(request, 'Product added successfully!')
        return redirect('products')
    categories = Category.objects.all()
    return render_jinja(request, 'agarbatti_app/add_product.html', {'categories': categories})


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.name = request.POST['name']
        product.category_id = request.POST.get('category') or None
        product.fragrance = request.POST.get('fragrance')
        product.length_cm = float(request.POST.get('length_cm', 20))
        product.burn_time_min = int(request.POST.get('burn_time_min', 30))
        product.sticks_per_pack = int(request.POST.get('sticks_per_pack', 10))
        product.packs_in_stock = int(request.POST.get('packs_in_stock', 0))
        product.purchase_price = float(request.POST['purchase_price'])
        product.selling_price = float(request.POST['selling_price'])
        product.low_stock_threshold = int(request.POST.get('low_stock_threshold', 20))
        product.description = request.POST.get('description')
        product.save()
        messages.success(request, 'Product updated!')
        return redirect('products')
    categories = Category.objects.all()
    return render_jinja(request, 'agarbatti_app/edit_product.html', {'product': product, 'categories': categories})


@login_required
def delete_product(request, pk):
    if request.user.is_staff:
        get_object_or_404(Product, pk=pk).delete()
        messages.success(request, 'Product deleted!')
    else:
        messages.error(request, 'Access denied!')
    return redirect('products')


@login_required
def product_api(request, pk):
    p = get_object_or_404(Product, pk=pk)
    return JsonResponse({'id': p.id, 'name': p.name, 'price': float(p.selling_price), 'stock': p.packs_in_stock})


@login_required
def search_products_api(request):
    q = request.GET.get('q', '')
    prods = Product.objects.filter(name__icontains=q, packs_in_stock__gt=0)[:10]
    return JsonResponse([{'id': p.id, 'name': p.name, 'price': float(p.selling_price), 'stock': p.packs_in_stock} for p in prods], safe=False)


# ===================== CATEGORIES =====================

@login_required
def categories(request):
    if request.method == 'POST':
        Category.objects.create(name=request.POST['name'], description=request.POST.get('description'))
        messages.success(request, 'Category added!')
    cats = Category.objects.annotate(product_count=Count('product'))
    return render_jinja(request, 'agarbatti_app/categories.html', {'categories': cats})


@login_required
def delete_category(request, pk):
    if request.user.is_staff:
        get_object_or_404(Category, pk=pk).delete()
        messages.success(request, 'Category deleted!')
    return redirect('categories')


# ===================== RAW MATERIALS =====================

@login_required
def raw_materials(request):
    search = request.GET.get('search', '')
    qs = RawMaterial.objects.select_related('supplier').all()
    if search:
        qs = qs.filter(name__icontains=search)
    return render_jinja(request, 'agarbatti_app/raw_materials.html', {'materials': qs})


@login_required
def add_raw_material(request):
    if request.method == 'POST':
        RawMaterial.objects.create(
            name=request.POST['name'],
            unit=request.POST.get('unit', 'kg'),
            quantity=float(request.POST.get('quantity', 0)),
            purchase_price=float(request.POST['purchase_price']),
            low_stock_threshold=float(request.POST.get('low_stock_threshold', 10)),
            supplier_id=request.POST.get('supplier') or None,
            description=request.POST.get('description'),
        )
        messages.success(request, 'Raw material added!')
        return redirect('raw_materials')
    suppliers = Supplier.objects.all()
    return render_jinja(request, 'agarbatti_app/add_raw_material.html', {'suppliers': suppliers})


@login_required
def edit_raw_material(request, pk):
    mat = get_object_or_404(RawMaterial, pk=pk)
    if request.method == 'POST':
        mat.name = request.POST['name']
        mat.unit = request.POST.get('unit', 'kg')
        mat.quantity = float(request.POST.get('quantity', 0))
        mat.purchase_price = float(request.POST['purchase_price'])
        mat.low_stock_threshold = float(request.POST.get('low_stock_threshold', 10))
        mat.supplier_id = request.POST.get('supplier') or None
        mat.description = request.POST.get('description')
        mat.save()
        messages.success(request, 'Raw material updated!')
        return redirect('raw_materials')
    suppliers = Supplier.objects.all()
    return render_jinja(request, 'agarbatti_app/edit_raw_material.html', {'material': mat, 'suppliers': suppliers})


@login_required
def delete_raw_material(request, pk):
    if request.user.is_staff:
        get_object_or_404(RawMaterial, pk=pk).delete()
        messages.success(request, 'Raw material deleted!')
    return redirect('raw_materials')


# ===================== SUPPLIERS =====================

@login_required
def suppliers(request):
    return render_jinja(request, 'agarbatti_app/suppliers.html', {'suppliers': Supplier.objects.all()})


@login_required
def add_supplier(request):
    if request.method == 'POST':
        Supplier.objects.create(
            name=request.POST['name'],
            contact_person=request.POST.get('contact_person'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            gst_number=request.POST.get('gst_number'),
        )
        messages.success(request, 'Supplier added!')
        return redirect('suppliers')
    return render_jinja(request, 'agarbatti_app/add_supplier.html')


@login_required
def edit_supplier(request, pk):
    sup = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        sup.name = request.POST['name']
        sup.contact_person = request.POST.get('contact_person')
        sup.phone = request.POST.get('phone')
        sup.email = request.POST.get('email')
        sup.address = request.POST.get('address')
        sup.gst_number = request.POST.get('gst_number')
        sup.save()
        messages.success(request, 'Supplier updated!')
        return redirect('suppliers')
    return render_jinja(request, 'agarbatti_app/edit_supplier.html', {'supplier': sup})


@login_required
def delete_supplier(request, pk):
    if request.user.is_staff:
        get_object_or_404(Supplier, pk=pk).delete()
        messages.success(request, 'Supplier deleted!')
    return redirect('suppliers')


# ===================== CUSTOMERS =====================

@login_required
def customers(request):
    search = request.GET.get('search', '')
    qs = Customer.objects.all()
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(phone__icontains=search))
    return render_jinja(request, 'agarbatti_app/customers.html', {'customers': qs})


@login_required
def add_customer(request):
    if request.method == 'POST':
        Customer.objects.create(
            name=request.POST['name'],
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            gst_number=request.POST.get('gst_number'),
        )
        messages.success(request, 'Customer added!')
        return redirect('customers')
    return render_jinja(request, 'agarbatti_app/add_customer.html')


@login_required
def customer_detail(request, pk):
    cust = get_object_or_404(Customer, pk=pk)
    orders = cust.orders.all()
    total_spent = orders.aggregate(t=Sum('total'))['t'] or 0
    return render_jinja(request, 'agarbatti_app/customer_detail.html', {
        'customer': cust, 'orders': orders, 'total_spent': total_spent
    })


# ===================== ORDERS =====================

@login_required
def orders(request):
    return render_jinja(request, 'agarbatti_app/orders.html', {
        'orders': Order.objects.select_related('customer').all()
    })


@login_required
def new_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        last = Order.objects.order_by('-id').first()
        num = (last.id + 1) if last else 1
        order_number = f"ORD-{timezone.now().strftime('%Y%m')}-{num:04d}"
        order = Order.objects.create(
            order_number=order_number,
            customer_id=data.get('customer_id') or None,
            customer_name=data.get('customer_name', 'Walk-in Customer'),
            subtotal=data['subtotal'],
            discount=data.get('discount', 0),
            tax=data.get('tax', 0),
            total=data['total'],
            payment_method=data.get('payment_method', 'cash'),
            created_by=request.user,
        )
        for item in data['items']:
            prod = get_object_or_404(Product, pk=item['product_id'])
            if prod.packs_in_stock < item['quantity']:
                order.delete()
                return JsonResponse({'error': f'Insufficient stock for {prod.name}'}, status=400)
            OrderItem.objects.create(
                order=order, product=prod,
                product_name=item['product_name'],
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                total_price=item['total_price'],
            )
            prod.packs_in_stock -= item['quantity']
            prod.save()
        return JsonResponse({'success': True, 'order_id': order.id, 'order_number': order.order_number})

    customers_list = Customer.objects.all()
    return render_jinja(request, 'agarbatti_app/new_order.html', {'customers': customers_list})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render_jinja(request, 'agarbatti_app/order_detail.html', {'order': order})


@login_required
def order_pdf(request, pk):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import inch

    order = get_object_or_404(Order, pk=pk)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    title_style = ParagraphStyle('title', fontSize=22, fontName='Helvetica-Bold', textColor=colors.HexColor('#7d3c0a'), spaceAfter=4)
    sub_style = ParagraphStyle('sub', fontSize=10, fontName='Helvetica', textColor=colors.grey)
    elements.append(Paragraph("Agarbatti House", title_style))
    elements.append(Paragraph("Premium Agarbatti Manufacturer | Ph: +91-9999999999", sub_style))
    from reportlab.platypus import Spacer
    elements.append(Spacer(1, 12))
    info_data = [
        ['Order No:', order.order_number, 'Date:', order.created_at.strftime('%d-%m-%Y %H:%M')],
        ['Customer:', order.customer_name, 'Payment:', order.payment_method.upper()],
    ]
    info_table = Table(info_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))
    table_data = [['#', 'Product', 'Qty (Packs)', 'Unit Price', 'Total']]
    for i, item in enumerate(order.items.all(), 1):
        table_data.append([str(i), item.product_name, str(item.quantity), f'Rs. {item.unit_price}', f'Rs. {item.total_price}'])
    table_data.append(['', '', '', 'Subtotal:', f'Rs. {order.subtotal}'])
    table_data.append(['', '', '', 'Discount:', f'Rs. {order.discount}'])
    table_data.append(['', '', '', 'Tax (GST):', f'Rs. {order.tax}'])
    table_data.append(['', '', '', 'TOTAL:', f'Rs. {order.total}'])
    t = Table(table_data, colWidths=[0.4*inch, 3.0*inch, 1.0*inch, 1.4*inch, 1.2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#7d3c0a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-5), [colors.white, colors.HexColor('#fdf2e9')]),
        ('GRID', (0,0), (-1,-5), 0.5, colors.lightgrey),
        ('FONTNAME', (3,-4), (3,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (3,-1), (4,-1), colors.HexColor('#7d3c0a')),
        ('LINEABOVE', (3,-1), (4,-1), 2, colors.HexColor('#7d3c0a')),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Thank you for choosing Agarbatti House!", ParagraphStyle('thanks', fontSize=10, fontName='Helvetica-Oblique', textColor=colors.grey, alignment=1)))
    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=order_{order.order_number}.pdf'
    return response


# ===================== PURCHASE ORDERS =====================

@login_required
def purchase_orders(request):
    return render_jinja(request, 'agarbatti_app/purchase_orders.html', {
        'orders': PurchaseOrder.objects.select_related('supplier').all()
    })


@login_required
def add_purchase_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        last = PurchaseOrder.objects.order_by('-id').first()
        num = (last.id + 1) if last else 1
        po = PurchaseOrder.objects.create(
            order_number=f"PO-{timezone.now().strftime('%Y%m')}-{num:04d}",
            supplier_id=data['supplier_id'],
            total_amount=data['total_amount'],
            notes=data.get('notes', ''),
        )
        for item in data['items']:
            PurchaseOrderItem.objects.create(
                order=po,
                raw_material_id=item['material_id'],
                material_name=item['material_name'],
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                total_price=item['total_price'],
            )
        return JsonResponse({'success': True})
    suppliers = Supplier.objects.all()
    materials = RawMaterial.objects.all()
    return render_jinja(request, 'agarbatti_app/add_purchase_order.html', {
        'suppliers': suppliers, 'materials': materials
    })


@login_required
def receive_purchase_order(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if order.status == 'pending':
        for item in order.items.all():
            if item.raw_material:
                item.raw_material.quantity += item.quantity
                item.raw_material.save()
        order.status = 'received'
        order.save()
        messages.success(request, 'Order received! Stock updated.')
    return redirect('purchase_orders')


@login_required
def cancel_purchase_order(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    order.status = 'cancelled'
    order.save()
    messages.warning(request, 'Order cancelled.')
    return redirect('purchase_orders')


# ===================== PRODUCTION =====================

@login_required
def production(request):
    return render_jinja(request, 'agarbatti_app/production.html', {
        'batches': ProductionBatch.objects.select_related('product').all()
    })


@login_required
def add_production(request):
    if request.method == 'POST':
        last = ProductionBatch.objects.order_by('-id').first()
        num = (last.id + 1) if last else 1
        prod = get_object_or_404(Product, pk=request.POST['product'])
        qty = int(request.POST['quantity_produced'])
        batch = ProductionBatch.objects.create(
            batch_number=f"BATCH-{timezone.now().strftime('%Y%m')}-{num:04d}",
            product=prod,
            quantity_produced=qty,
            production_cost=float(request.POST.get('production_cost', 0)),
            status=request.POST.get('status', 'completed'),
            notes=request.POST.get('notes'),
            produced_by=request.user,
        )
        if batch.status == 'completed':
            prod.packs_in_stock += qty
            prod.save()
        messages.success(request, f'Production batch {batch.batch_number} created!')
        return redirect('production')
    products_list = Product.objects.all()
    return render_jinja(request, 'agarbatti_app/add_production.html', {'products': products_list})


# ===================== EXPENSES =====================

@login_required
def expenses(request):
    qs = Expense.objects.all()
    total = qs.aggregate(t=Sum('amount'))['t'] or 0
    return render_jinja(request, 'agarbatti_app/expenses.html', {'expenses': qs, 'total': total})


@login_required
def add_expense(request):
    if request.method == 'POST':
        Expense.objects.create(
            title=request.POST['title'],
            category=request.POST.get('category', 'other'),
            amount=float(request.POST['amount']),
            description=request.POST.get('description'),
            date=request.POST.get('date') or date.today(),
            created_by=request.user,
        )
        messages.success(request, 'Expense recorded!')
        return redirect('expenses')
    return render_jinja(request, 'agarbatti_app/add_expense.html')


@login_required
def delete_expense(request, pk):
    if request.user.is_staff:
        get_object_or_404(Expense, pk=pk).delete()
        messages.success(request, 'Expense deleted!')
    return redirect('expenses')


# ===================== WORKERS =====================

@login_required
def workers(request):
    return render_jinja(request, 'agarbatti_app/workers.html', {'workers': Worker.objects.all()})


@login_required
def add_worker(request):
    if request.method == 'POST':
        Worker.objects.create(
            name=request.POST['name'],
            phone=request.POST.get('phone'),
            role=request.POST.get('role'),
            salary=float(request.POST.get('salary', 0)),
            address=request.POST.get('address'),
            joining_date=request.POST.get('joining_date') or date.today(),
        )
        messages.success(request, 'Worker added!')
        return redirect('workers')
    return render_jinja(request, 'agarbatti_app/add_worker.html')


@login_required
def edit_worker(request, pk):
    worker = get_object_or_404(Worker, pk=pk)
    if request.method == 'POST':
        worker.name = request.POST['name']
        worker.phone = request.POST.get('phone')
        worker.role = request.POST.get('role')
        worker.salary = float(request.POST.get('salary', 0))
        worker.address = request.POST.get('address')
        worker.is_active = 'is_active' in request.POST
        worker.save()
        messages.success(request, 'Worker updated!')
        return redirect('workers')
    return render_jinja(request, 'agarbatti_app/edit_worker.html', {'worker': worker})


@login_required
def delete_worker(request, pk):
    if request.user.is_staff:
        get_object_or_404(Worker, pk=pk).delete()
        messages.success(request, 'Worker deleted!')
    return redirect('workers')


# ===================== REPORTS =====================

@login_required
def reports(request):
    period = request.GET.get('period', 'today')
    today = date.today()
    if period == 'today':
        start = today
    elif period == 'week':
        start = today - timedelta(days=7)
    elif period == 'month':
        start = today.replace(day=1)
    else:
        start = today.replace(month=1, day=1)

    orders_qs = Order.objects.filter(created_at__date__gte=start, status='completed')
    total_revenue = orders_qs.aggregate(t=Sum('total'))['t'] or 0
    total_orders = orders_qs.count()
    top_products = OrderItem.objects.filter(
        order__created_at__date__gte=start, order__status='completed'
    ).values('product_name').annotate(
        total_qty=Sum('quantity'), total_revenue=Sum('total_price')
    ).order_by('-total_revenue')[:10]

    expenses_qs = Expense.objects.filter(date__gte=start)
    total_expenses = expenses_qs.aggregate(t=Sum('amount'))['t'] or 0
    profit = float(total_revenue) - float(total_expenses)

    return render_jinja(request, 'agarbatti_app/reports.html', {
        'period': period,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_expenses': total_expenses,
        'profit': profit,
        'top_products': top_products,
        'low_stock_products': Product.objects.filter(packs_in_stock__lte=20),
        'low_stock_materials': RawMaterial.objects.filter(quantity__lte=10),
        'expense_breakdown': expenses_qs.values('category').annotate(total=Sum('amount')),
    })
