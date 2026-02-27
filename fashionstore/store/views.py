from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.utils import timezone
import json, hashlib, random, string
from .models import User, Product, Category, Order, OrderItem, Cart, PromoCode


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

def login_required_customer(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

def login_required_admin(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get('role') != 'admin':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

def generate_order_id():
    return 'ORD-' + ''.join(random.choices(string.digits, k=6))


# ─── AUTH VIEWS ───────────────────────────────────────────────────────────────

def login_view(request):
    if request.session.get('user_id'):
        if request.session.get('role') == 'admin':
            return redirect('admin_dashboard')
        return redirect('home')

    if request.method == 'POST':
        action = request.POST.get('action', 'login')

        if action == 'register':
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered.')
                return render(request, 'store/login.html', {'tab': 'register'})
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken.')
                return render(request, 'store/login.html', {'tab': 'register'})
            user = User.objects.create(
                name=name, email=email, username=username,
                password=hash_password(password), role='customer'
            )
            request.session['user_id'] = user.id
            request.session['user_name'] = user.name
            request.session['role'] = 'customer'
            return redirect('home')

        # LOGIN
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Special admin credentials
        if username == 'admin' and password == 'admin':
            request.session['user_id'] = 0
            request.session['user_name'] = 'Admin'
            request.session['role'] = 'admin'
            return redirect('admin_dashboard')

        try:
            user = User.objects.get(username=username, password=hash_password(password))
            if user.status == 'blocked':
                messages.error(request, 'Your account has been blocked. Contact support.')
                return render(request, 'store/login.html', {})
            request.session['user_id'] = user.id
            request.session['user_name'] = user.name
            request.session['role'] = user.role
            if user.role == 'admin':
                return redirect('admin_dashboard')
            return redirect('home')
        except User.DoesNotExist:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'store/login.html', {})


def logout_view(request):
    request.session.flush()
    return redirect('login')


def register_view(request):
    return redirect('login')


# ─── CUSTOMER VIEWS ───────────────────────────────────────────────────────────

@login_required_customer
def home(request):
    categories = Category.objects.all()
    trending = Product.objects.filter(is_trending=True, status='active')[:4]
    new_arrivals = Product.objects.filter(is_new_arrival=True, status='active')[:4]
    return render(request, 'store/home.html', {
        'categories': categories,
        'trending': trending,
        'new_arrivals': new_arrivals,
    })


@login_required_customer
def shop(request):
    products = Product.objects.filter(status='active')
    categories = Category.objects.all()

    # Filters
    category_id = request.GET.get('category')
    size = request.GET.get('size')
    color = request.GET.get('color')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort', 'newest')
    search = request.GET.get('q', '')

    if category_id:
        products = products.filter(category_id=category_id)
    if size:
        products = products.filter(sizes__icontains=size)
    if color:
        products = products.filter(colors__icontains=color)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if search:
        products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))

    sort_options = {
        'newest': '-created_at',
        'price_asc': 'price',
        'price_desc': '-price',
        'rating': '-rating',
    }
    products = products.order_by(sort_options.get(sort, '-created_at'))

    total_count = products.count()

    return render(request, 'store/shop.html', {
        'products': products,
        'categories': categories,
        'total_count': total_count,
        'selected_category': category_id,
        'selected_size': size,
        'sort': sort,
        'search': search,
    })


@login_required_customer
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, status='active')
    related = Product.objects.filter(category=product.category, status='active').exclude(pk=pk)[:4]
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related': related,
        'sizes': product.get_sizes(),
        'colors': product.get_colors(),
    })


@login_required_customer
def cart_view(request):
    session_key = get_session_key(request)
    cart_items = Cart.objects.filter(session_key=session_key).select_related('product')
    subtotal = sum(item.subtotal() for item in cart_items)
    shipping = 0 if subtotal >= 200 else 12
    tax = round(float(subtotal) * 0.08, 2)
    total = float(subtotal) + shipping + tax

    # Apply promo if in session
    discount = 0
    promo = request.session.get('promo_code', '')
    if promo:
        try:
            p = PromoCode.objects.get(code=promo, is_active=True)
            discount = round(float(subtotal) * p.discount_pct / 100, 2)
            total -= discount
        except PromoCode.DoesNotExist:
            pass

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': round(total, 2),
        'discount': discount,
        'promo': promo,
    })


@login_required_customer
def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk)
    session_key = get_session_key(request)
    size = request.POST.get('size', 'M')
    color = request.POST.get('color', 'Black')

    item, created = Cart.objects.get_or_create(
        session_key=session_key, product=product, size=size, color=color,
        defaults={'quantity': 1}
    )
    if not created:
        item.quantity += 1
        item.save()

    messages.success(request, f'"{product.name}" added to cart!')
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


@login_required_customer
def cart_update(request, item_id):
    item = get_object_or_404(Cart, pk=item_id, session_key=get_session_key(request))
    qty = int(request.POST.get('quantity', 1))
    if qty < 1:
        item.delete()
    else:
        item.quantity = qty
        item.save()
    return redirect('cart')


@login_required_customer
def cart_remove(request, item_id):
    item = get_object_or_404(Cart, pk=item_id, session_key=get_session_key(request))
    item.delete()
    return redirect('cart')


@login_required_customer
def apply_promo(request):
    code = request.POST.get('promo_code', '').strip().upper()
    try:
        promo = PromoCode.objects.get(code=code, is_active=True)
        request.session['promo_code'] = code
        messages.success(request, f'Promo code applied! {promo.discount_pct}% discount.')
    except PromoCode.DoesNotExist:
        messages.error(request, 'Invalid or expired promo code.')
    return redirect('cart')


@login_required_customer
def checkout_view(request):
    session_key = get_session_key(request)
    cart_items = Cart.objects.filter(session_key=session_key).select_related('product')
    if not cart_items.exists():
        return redirect('cart')

    subtotal = sum(item.subtotal() for item in cart_items)
    shipping = 0 if subtotal >= 200 else 12
    tax = round(float(subtotal) * 0.08, 2)
    discount = 0
    promo = request.session.get('promo_code', '')
    if promo:
        try:
            p = PromoCode.objects.get(code=promo, is_active=True)
            discount = round(float(subtotal) * p.discount_pct / 100, 2)
        except PromoCode.DoesNotExist:
            pass
    total = round(float(subtotal) + shipping + tax - discount, 2)

    if request.method == 'POST':
        name = request.POST.get('full_name', '')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        pincode = request.POST.get('pincode', '')
        payment = request.POST.get('payment_method', 'card')

        order_id = generate_order_id()
        while Order.objects.filter(order_id=order_id).exists():
            order_id = generate_order_id()

        user_id = request.session.get('user_id')
        user = None
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                pass

        order = Order.objects.create(
            order_id=order_id,
            user=user,
            customer_name=name,
            customer_email=user.email if user else '',
            shipping_address=address,
            city=city,
            pincode=pincode,
            payment_method=payment,
            subtotal=subtotal,
            shipping_cost=shipping,
            tax=tax,
            discount=discount,
            total=total,
            promo_code=promo,
            status='pending'
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                size=item.size,
                color=item.color,
                quantity=item.quantity,
                price=item.product.price,
            )
        cart_items.delete()
        if 'promo_code' in request.session:
            del request.session['promo_code']

        return redirect('order_confirm')

    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
        'discount': discount,
    })


@login_required_customer
def order_confirm(request):
    user_id = request.session.get('user_id')
    last_order = None
    if user_id:
        try:
            user = User.objects.get(pk=user_id)
            last_order = Order.objects.filter(user=user).order_by('-created_at').first()
        except User.DoesNotExist:
            pass
    return render(request, 'store/order_confirm.html', {'order': last_order})


@login_required_customer
def user_orders(request):
    user_id = request.session.get('user_id')
    orders = []
    if user_id:
        try:
            user = User.objects.get(pk=user_id)
            orders = Order.objects.filter(user=user).prefetch_related('items')
        except User.DoesNotExist:
            pass
    return render(request, 'store/user_orders.html', {'orders': orders})


# ─── ADMIN VIEWS ──────────────────────────────────────────────────────────────

@login_required_admin
def admin_dashboard(request):
    total_orders = Order.objects.count()
    total_users = User.objects.filter(role='customer').count()
    total_products = Product.objects.count()
    monthly_revenue = Order.objects.filter(
        status__in=['shipped', 'delivered']
    ).aggregate(rev=Sum('total'))['rev'] or 0

    # Revenue by month for chart
    from django.db.models.functions import TruncMonth
    monthly_data = (
        Order.objects.filter(status__in=['shipped', 'delivered'])
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('total'))
        .order_by('month')
    )
    chart_labels = [d['month'].strftime('%b') if d['month'] else '' for d in monthly_data]
    chart_data = [float(d['total']) for d in monthly_data]

    recent_orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')[:10]

    return render(request, 'store/admin_dashboard.html', {
        'total_orders': total_orders,
        'total_users': total_users,
        'total_products': total_products,
        'monthly_revenue': monthly_revenue,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'recent_orders': recent_orders,
    })


@login_required_admin
def admin_products(request):
    products = Product.objects.select_related('category').order_by('-created_at')
    categories = Category.objects.all()
    search = request.GET.get('q', '')
    if search:
        products = products.filter(name__icontains=search)

    total = Product.objects.count()
    out_of_stock = Product.objects.filter(status='out_of_stock').count()
    monthly_sales = Order.objects.filter(
        status__in=['shipped', 'delivered']
    ).aggregate(rev=Sum('total'))['rev'] or 0
    avg_price = Product.objects.aggregate(avg=models_avg('price'))['avg'] or 0

    return render(request, 'store/admin_products.html', {
        'products': products,
        'categories': categories,
        'total': total,
        'out_of_stock': out_of_stock,
        'monthly_sales': monthly_sales,
        'avg_price': round(float(avg_price), 2),
        'search': search,
    })


def models_avg(field):
    from django.db.models import Avg
    return Avg(field)


@login_required_admin
def admin_product_add(request):
    if request.method == 'POST':
        cat_id = request.POST.get('category')
        category = Category.objects.get(pk=cat_id) if cat_id else None
        sizes = ','.join(request.POST.getlist('sizes'))
        product = Product(
            name=request.POST.get('name'),
            description=request.POST.get('description', ''),
            price=request.POST.get('price'),
            original_price=request.POST.get('original_price') or None,
            category=category,
            stock=request.POST.get('stock', 0),
            sizes=sizes or 'S,M,L,XL',
            colors=request.POST.get('colors', 'Black,White'),
            status=request.POST.get('status', 'active'),
            is_trending=request.POST.get('is_trending') == 'on',
            is_new_arrival=request.POST.get('is_new_arrival') == 'on',
        )
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        product.save()
        messages.success(request, 'Product added successfully!')
        return redirect('admin_products')
    categories = Category.objects.all()
    return render(request, 'store/admin_products.html', {'categories': categories, 'form_mode': 'add'})


@login_required_admin
def admin_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        cat_id = request.POST.get('category')
        product.name = request.POST.get('name')
        product.description = request.POST.get('description', '')
        product.price = request.POST.get('price')
        product.original_price = request.POST.get('original_price') or None
        product.category = Category.objects.get(pk=cat_id) if cat_id else None
        product.stock = request.POST.get('stock', 0)
        product.sizes = ','.join(request.POST.getlist('sizes'))
        product.colors = request.POST.get('colors', 'Black,White')
        product.status = request.POST.get('status', 'active')
        product.is_trending = request.POST.get('is_trending') == 'on'
        product.is_new_arrival = request.POST.get('is_new_arrival') == 'on'
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        product.save()
        messages.success(request, 'Product updated!')
        return redirect('admin_products')
    categories = Category.objects.all()
    return render(request, 'store/admin_products.html', {
        'product': product, 'categories': categories, 'form_mode': 'edit'
    })


@login_required_admin
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, 'Product deleted.')
    return redirect('admin_products')


@login_required_admin
def admin_orders(request):
    orders = Order.objects.prefetch_related('items').order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)

    pending = Order.objects.filter(status='pending').count()
    shipped = Order.objects.filter(status='shipped').count()
    delivered = Order.objects.filter(status='delivered').count()
    revenue_today = Order.objects.filter(
        created_at__date=timezone.now().date()
    ).aggregate(rev=Sum('total'))['rev'] or 0

    return render(request, 'store/admin_orders.html', {
        'orders': orders,
        'pending': pending,
        'shipped': shipped,
        'delivered': delivered,
        'revenue_today': revenue_today,
        'status_filter': status_filter,
    })


@login_required_admin
def admin_order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.status = request.POST.get('status', order.status)
        order.save()
        messages.success(request, f'Order #{order.order_id} updated to {order.status}.')
    return redirect('admin_orders')


@login_required_admin
def admin_users(request):
    users = User.objects.filter(role='customer').order_by('-created_at')
    search = request.GET.get('q', '')
    if search:
        users = users.filter(Q(name__icontains=search) | Q(email__icontains=search))

    total_users = users.count()
    active_users = users.filter(status='active').count()
    blocked_users = users.filter(status='blocked').count()

    return render(request, 'store/admin_users.html', {
        'users': users,
        'total_users': total_users,
        'active_users': active_users,
        'blocked_users': blocked_users,
        'search': search,
    })


@login_required_admin
def admin_user_toggle(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.status = 'blocked' if user.status == 'active' else 'active'
    user.save()
    messages.success(request, f'User {user.name} is now {user.status}.')
    return redirect('admin_users')


@login_required_admin
def admin_user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    messages.success(request, 'User deleted.')
    return redirect('admin_users')
