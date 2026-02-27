from django.db import models


class User(models.Model):
    ROLE_CHOICES = [('admin', 'Admin'), ('customer', 'Customer')]
    STATUS_CHOICES = [('active', 'Active'), ('blocked', 'Blocked')]

    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.role})"

    class Meta:
        db_table = 'store_user'


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'store_category'
        verbose_name_plural = 'Categories'


class Product(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('hidden', 'Hidden'), ('out_of_stock', 'Out of Stock')]
    SIZE_CHOICES = ['XS', 'S', 'M', 'L', 'XL', 'XXL']

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    image2 = models.ImageField(upload_to='products/', null=True, blank=True)
    image3 = models.ImageField(upload_to='products/', null=True, blank=True)
    stock = models.IntegerField(default=0)
    sizes = models.CharField(max_length=100, default='S,M,L,XL')
    colors = models.CharField(max_length=200, default='Black,White,Pink')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    review_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_trending = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    badge = models.CharField(max_length=50, blank=True)  # e.g. SALE-30%, POPULAR
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_sizes(self):
        return [s.strip() for s in self.sizes.split(',')]

    def get_colors(self):
        return [c.strip() for c in self.colors.split(',')]

    def discount_pct(self):
        if self.original_price and self.original_price > self.price:
            return int((1 - self.price / self.original_price) * 100)
        return 0

    class Meta:
        db_table = 'store_product'


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [('card', 'Card'), ('upi', 'UPI'), ('cod', 'Cash on Delivery')]

    order_id = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    shipping_address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='card')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    promo_code = models.CharField(max_length=50, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"#{self.order_id} — {self.customer_name}"

    class Meta:
        db_table = 'store_order'
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    size = models.CharField(max_length=10)
    color = models.CharField(max_length=50)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.price * self.quantity

    class Meta:
        db_table = 'store_order_item'


class Cart(models.Model):
    session_key = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=10, default='M')
    color = models.CharField(max_length=50, default='Black')
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"Cart: {self.product.name} x{self.quantity}"

    class Meta:
        db_table = 'store_cart'


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_pct = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} — {self.discount_pct}% off"

    class Meta:
        db_table = 'store_promo'
