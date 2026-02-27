# 👗 LuxeDress — Fashion E-Commerce Platform
A complete Django + MySQL fashion e-commerce project with 10 screens, custom auth, and admin dashboard.

---

## 🚀 QUICK SETUP (5 Steps)

### Step 1 — Install Requirements
```bash
pip install -r requirements.txt
```

### Step 2 — Create MySQL Database
Open MySQL and run:
```sql
CREATE DATABASE fashionstore_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 3 — Update Database Settings
Open `fashionstore/settings.py` and update your MySQL password:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fashionstore_db',
        'USER': 'root',
        'PASSWORD': 'your_mysql_password',   # ← CHANGE THIS
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Step 4 — Run Migrations
```bash
python manage.py migrate
```

### Step 5 — Seed Dummy Data
```bash
python manage.py seed_data
```

### Step 6 — Run Server
```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000` in your browser.

---

## 🔐 LOGIN CREDENTIALS

| Role     | Username    | Password    | Redirects To       |
|----------|-------------|-------------|-------------------|
| **Admin**| `admin`     | `admin`     | Admin Dashboard   |
| Customer | `sarah_j`   | `sarah123`  | Homepage          |
| Customer | `michael_c` | `michael123`| Homepage          |
| Customer | `emma_w`    | `emma123`   | Homepage          |
| Customer | `liam_j`    | `liam123`   | Homepage          |

> ⚠️ Django's default admin (`/admin/`) is NOT used. All admin pages are custom-built.

---

## 📄 10 SCREENS / PAGES

| Screen | URL | Description |
|--------|-----|-------------|
| 1 | `/` or `/login/` | Login & Register page |
| 2 | `/home/` | Homepage — Hero, Categories, Trending |
| 3 | `/shop/` | Product listing with filters & sort |
| 4 | `/product/<id>/` | Product detail — sizes, colors, add to cart |
| 5 | `/cart/` | Shopping cart with promo codes |
| 6 | `/checkout/` | Checkout — shipping & payment |
| 7 | `/admin-dashboard/` | Admin dashboard with revenue chart |
| 8 | `/admin-products/` | Product management — add/edit/delete |
| 9 | `/admin-orders/` | Orders management — status updates |
| 10 | `/admin-users/` | User management — block/unblock |

---

## 🛠️ TECH STACK
- **Frontend**: HTML5, CSS3, Bootstrap 5.3, JavaScript
- **Backend**: Python 3.x, Django 4.2
- **Database**: MySQL (via mysqlclient)
- **Auth**: Custom session-based (no Django default admin)
- **Charts**: Chart.js (admin dashboard)
- **Icons**: Bootstrap Icons

---

## 🧪 PROMO CODES (for testing)
| Code    | Discount |
|---------|----------|
| CHIC10  | 10% off  |
| LUXE20  | 20% off  |
| SAVE15  | 15% off  |

---

## 📁 PROJECT STRUCTURE
```
fashionstore/
├── manage.py
├── requirements.txt
├── fashionstore/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/
│   ├── models.py          # User, Product, Category, Order, Cart
│   ├── views.py           # All views (customer + admin)
│   ├── urls.py            # All URL routes
│   ├── context_processors.py
│   ├── migrations/
│   ├── templatetags/
│   │   └── custom_tags.py
│   ├── management/commands/
│   │   └── seed_data.py   # python manage.py seed_data
│   └── templates/store/
│       ├── base.html
│       ├── navbar.html
│       ├── footer.html
│       ├── admin_sidebar.html
│       ├── login.html
│       ├── home.html
│       ├── shop.html
│       ├── product_detail.html
│       ├── cart.html
│       ├── checkout.html
│       ├── order_confirm.html
│       ├── user_orders.html
│       ├── admin_dashboard.html
│       ├── admin_products.html
│       ├── admin_orders.html
│       └── admin_users.html
└── media/                 # Uploaded product images
```
