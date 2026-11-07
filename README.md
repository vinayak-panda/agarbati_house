# Agarbatti House - Management System
## Built with Django & SQLite


LINK OF THE APPLICATION : https://agarbati-house-1.onrender.com

---

## Features
- Login with Admin & Staff roles
- Dashboard with sales charts & alerts
- Product management (Agarbatti products)
- Raw material inventory tracking
- Category management
- Sales Order management with PDF invoice
- Customer management & order history
- Supplier management
- Purchase Orders (raw materials, auto stock update)
- Production batch tracking
- Expense management
- Worker management
- Reports: Sales, Profit, Top products, Low stock
- Low stock alerts for products & raw materials

---

## Local Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Migrations
```bash
python manage.py migrate
```

### Step 3: Create Admin & Sample Data
```bash
python manage.py create_default_admin
```

### Step 4: Run Server
```bash
python manage.py runserver
```

### Step 5: Open in Browser
```
http://localhost:8000
```

---

## Login Credentials

| Role  | Username | Password  |
|-------|----------|-----------|
| Admin | `admin`  | `admin123` |
| Staff | `staff`  | `staff123` |

---

## Render Deployment

### Step 1: Push to GitHub

git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/agarbatti-house.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to [render.com](https://render.com) → New → Web Service
2. Connect your GitHub repo
3. Set these values:

| Field | Value |
|-------|-------|
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput && python manage.py create_default_admin` |
| Start Command | `gunicorn agarbatti_project.wsgi:application` |

4. Add environment variable: `SECRET_KEY` (auto-generate)
5. Click **Create Web Service** ✅

---

Project Structure
agarbatti_app/
├── manage.py
├── requirements.txt
├── render.yaml
├── .python-version
├── agarbatti_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── agarbatti_app/
    ├── models.py       # All DB models
    ├── views.py        # All views
    ├── urls.py         # URL routing
    ├── admin.py        # Django admin
    ├── jinja2.py       # Jinja2 setup
    ├── migrations/     # DB migrations
    ├── management/     # Custom commands
    │   └── commands/
    │       └── create_default_admin.py
    └── templates/
        └── agarbatti_app/
            ├── base.html
            ├── login.html
            ├── dashboard.html
            ├── products.html
            ├── categories.html
            ├── raw_materials.html
            ├── suppliers.html
            ├── customers.html
            ├── orders.html
            ├── new_order.html
            ├── order_detail.html
            ├── purchase_orders.html
            ├── production.html
            ├── expenses.html
            ├── workers.html
            └── reports.html

## Tech Stack
- Backend: Django 4.2
- Database: SQLite (local) / PostgreSQL (production)
- Frontend: Bootstrap 5, Chart.js, Font Awesome
- PDF: ReportLab
- Deploy: Gunicorn + WhiteNoise

