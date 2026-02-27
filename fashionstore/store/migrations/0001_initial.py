from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='categories/')),
            ],
            options={'db_table': 'store_category', 'verbose_name_plural': 'Categories'},
        ),
        migrations.CreateModel(
            name='PromoCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount_pct', models.IntegerField(default=10)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'db_table': 'store_promo'},
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('email', models.EmailField(unique=True)),
                ('username', models.CharField(max_length=100, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('customer', 'Customer')], default='customer', max_length=20)),
                ('status', models.CharField(choices=[('active', 'Active'), ('blocked', 'Blocked')], default='active', max_length=20)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'store_user'},
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('original_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='products/')),
                ('image2', models.ImageField(blank=True, null=True, upload_to='products/')),
                ('image3', models.ImageField(blank=True, null=True, upload_to='products/')),
                ('stock', models.IntegerField(default=0)),
                ('sizes', models.CharField(default='S,M,L,XL', max_length=100)),
                ('colors', models.CharField(default='Black,White,Pink', max_length=200)),
                ('rating', models.DecimalField(decimal_places=1, default=4.5, max_digits=3)),
                ('review_count', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('active', 'Active'), ('hidden', 'Hidden'), ('out_of_stock', 'Out of Stock')], default='active', max_length=20)),
                ('is_trending', models.BooleanField(default=False)),
                ('is_new_arrival', models.BooleanField(default=False)),
                ('badge', models.CharField(blank=True, max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.category')),
            ],
            options={'db_table': 'store_product'},
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=20, unique=True)),
                ('customer_name', models.CharField(max_length=150)),
                ('customer_email', models.EmailField()),
                ('shipping_address', models.TextField()),
                ('city', models.CharField(max_length=100)),
                ('pincode', models.CharField(max_length=20)),
                ('payment_method', models.CharField(choices=[('card', 'Card'), ('upi', 'UPI'), ('cod', 'Cash on Delivery')], default='card', max_length=20)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('shipping_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tax', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('promo_code', models.CharField(blank=True, max_length=50)),
                ('discount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.user')),
            ],
            options={'db_table': 'store_order', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=200)),
                ('size', models.CharField(max_length=10)),
                ('color', models.CharField(max_length=50)),
                ('quantity', models.IntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='store.order')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.product')),
            ],
            options={'db_table': 'store_order_item'},
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=100)),
                ('size', models.CharField(default='M', max_length=10)),
                ('color', models.CharField(default='Black', max_length=50)),
                ('quantity', models.IntegerField(default=1)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
            options={'db_table': 'store_cart'},
        ),
    ]
