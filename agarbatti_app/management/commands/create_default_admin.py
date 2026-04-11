from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from agarbatti_app.models import Category, Supplier, RawMaterial, Product, Customer, Worker
from datetime import date


class Command(BaseCommand):
    help = 'Creates default admin user and sample data'

    def handle(self, *args, **kwargs):
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                password='admin123',
                email='admin@agarbattihouse.com',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('✅ Admin user created: admin / admin123'))
        else:
            self.stdout.write('ℹ️  Admin already exists')

        # Create staff user
        if not User.objects.filter(username='staff').exists():
            User.objects.create_user(
                username='staff',
                password='staff123',
                email='staff@agarbattihouse.com',
                first_name='Staff',
                last_name='Member'
            )
            self.stdout.write(self.style.SUCCESS('✅ Staff user created: staff / staff123'))

        # Categories
        categories = ['Premium', 'Economy', 'Floral', 'Religious', 'Herbal', 'Exotic']
        for name in categories:
            Category.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS('✅ Categories created'))

        # Supplier
        sup, _ = Supplier.objects.get_or_create(
            name='Agarwal Raw Materials',
            defaults={
                'contact_person': 'Ramesh Agarwal',
                'phone': '9876543210',
                'email': 'agarwal@rawmaterials.com',
                'address': 'Surat, Gujarat',
                'gst_number': '24AABCA1234C1Z5'
            }
        )
        self.stdout.write(self.style.SUCCESS('✅ Supplier created'))

        # Raw Materials
        materials = [
            ('Bamboo Sticks', 'bundle', 500, 120.00),
            ('Charcoal Powder', 'kg', 50, 80.00),
            ('Jigat Powder (Binder)', 'kg', 30, 200.00),
            ('Rose Fragrance Oil', 'litre', 5, 850.00),
            ('Sandalwood Fragrance Oil', 'litre', 4, 1200.00),
            ('Jasmine Fragrance Oil', 'litre', 6, 750.00),
            ('Packaging Boxes', 'box', 200, 15.00),
            ('Color Powder', 'kg', 10, 150.00),
        ]
        for name, unit, qty, price in materials:
            RawMaterial.objects.get_or_create(
                name=name,
                defaults={'unit': unit, 'quantity': qty, 'purchase_price': price, 'supplier': sup}
            )
        self.stdout.write(self.style.SUCCESS('✅ Raw materials created'))

        # Products
        cat_floral = Category.objects.get(name='Floral')
        cat_premium = Category.objects.get(name='Premium')
        cat_religious = Category.objects.get(name='Religious')
        cat_herbal = Category.objects.get(name='Herbal')

        products = [
            ('Rose Agarbatti', cat_floral, 'Rose', 20, 45, 10, 150, 8.00, 20.00),
            ('Sandalwood Agarbatti', cat_premium, 'Sandalwood', 22, 50, 10, 200, 12.00, 30.00),
            ('Jasmine Agarbatti', cat_floral, 'Jasmine', 20, 40, 10, 120, 7.00, 18.00),
            ('Guggul Dhoop', cat_religious, 'Guggul', 15, 30, 20, 80, 15.00, 40.00),
            ('Neem Herbal Agarbatti', cat_herbal, 'Neem', 20, 45, 10, 5, 9.00, 22.00),
            ('Lavender Agarbatti', cat_premium, 'Lavender', 22, 50, 10, 60, 11.00, 28.00),
        ]
        for name, cat, frag, length, burn, sticks, stock, pp, sp in products:
            Product.objects.get_or_create(
                name=name,
                defaults={
                    'category': cat, 'fragrance': frag,
                    'length_cm': length, 'burn_time_min': burn,
                    'sticks_per_pack': sticks, 'packs_in_stock': stock,
                    'purchase_price': pp, 'selling_price': sp
                }
            )
        self.stdout.write(self.style.SUCCESS('✅ Products created'))

        # Customers
        customers = [
            ('Sharma Puja Store', '9898989898', 'sharma@pujastore.com', 'Andheri, Mumbai'),
            ('Gupta Traders', '8787878787', 'gupta@traders.com', 'Pune, Maharashtra'),
            ('Krishna Bhandar', '7676767676', None, 'Nashik, Maharashtra'),
        ]
        for name, phone, email, address in customers:
            Customer.objects.get_or_create(
                name=name, defaults={'phone': phone, 'email': email, 'address': address}
            )
        self.stdout.write(self.style.SUCCESS('✅ Customers created'))

        # Workers
        workers = [
            ('Ramesh Kumar', '9111111111', 'Stick Roller', 12000),
            ('Sunita Devi', '9222222222', 'Packer', 10000),
            ('Mohan Lal', '9333333333', 'Mixer', 13000),
            ('Priya Sharma', '9444444444', 'Quality Check', 11000),
        ]
        for name, phone, role, salary in workers:
            Worker.objects.get_or_create(
                name=name, defaults={'phone': phone, 'role': role, 'salary': salary}
            )
        self.stdout.write(self.style.SUCCESS('✅ Workers created'))
        self.stdout.write(self.style.SUCCESS('\n🪔 Agarbatti House setup complete!'))
        self.stdout.write(self.style.SUCCESS('Login: admin / admin123'))
