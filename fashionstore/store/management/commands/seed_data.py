import hashlib
import random
from django.core.management.base import BaseCommand
from store.models import User, Category, Product, Order, OrderItem, PromoCode


def h(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


class Command(BaseCommand):
    help = 'Seed database with dummy data'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Seeding database...')

        # PROMO CODES
        PromoCode.objects.get_or_create(code='CHIC10', defaults={'discount_pct': 10})
        PromoCode.objects.get_or_create(code='LUXE20', defaults={'discount_pct': 20})
        PromoCode.objects.get_or_create(code='SAVE15', defaults={'discount_pct': 15})
        self.stdout.write('✅ Promo codes created')

        # CATEGORIES
        cats = [
            ('Women', 'women'),
            ('Men', 'men'),
            ('Kids', 'kids'),
            ('Accessories', 'accessories'),
        ]
        cat_objs = {}
        for name, slug in cats:
            obj, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name})
            cat_objs[slug] = obj
        self.stdout.write('✅ Categories created')

        # USERS (dummy customers)
        users_data = [
            ('Sarah Jenkins', 'sarah.j@email.com', 'sarah_j', 'sarah123'),
            ('Michael Chen', 'm.chen@email.com', 'michael_c', 'michael123'),
            ('Elena Rodriguez', 'elena.rod@email.com', 'elena_r', 'elena123'),
            ('John Smith', 'jsmith@email.com', 'john_smith', 'john123'),
            ('Emma Wilson', 'emma.w@email.com', 'emma_w', 'emma123'),
            ('James Parker', 'james.p@email.com', 'james_p', 'james123'),
            ('Olivia Brown', 'olivia.b@email.com', 'olivia_b', 'olivia123'),
            ('Liam Johnson', 'liam.j@email.com', 'liam_j', 'liam123'),
        ]
        user_objs = []
        for name, email, username, password in users_data:
            u, _ = User.objects.get_or_create(
                email=email,
                defaults={'name': name, 'username': username, 'password': h(password), 'role': 'customer'}
            )
            user_objs.append(u)
        # Block one user for demo
        User.objects.filter(email='elena.rod@email.com').update(status='blocked')
        self.stdout.write(f'✅ {len(user_objs)} customers created')

        # PRODUCTS
        products_data = [
            # Women
            ('Midnight Silk Gown', 'women', 129.00, 185.00, True, False, 'SALE-30%', 'S,M,L,XL', 'Black,Navy,Silver', 4.8, 42, 35),
            ('Floral Summer Maxi', 'women', 89.00, 110.00, False, True, 'SALE-20%', 'XS,S,M,L', 'Blush,White,Green', 4.6, 18, 22),
            ('Velvet Night Cocktail', 'women', 145.00, 199.00, True, False, 'POPULAR', 'S,M,L', 'Burgundy,Black,Navy', 4.9, 56, 18),
            ('Chiffon Petal Mini', 'women', 75.00, 150.00, False, False, 'SALE-50%', 'XS,S,M,L,XL', 'White,Cream,Blush', 4.5, 24, 40),
            ('Lace Meadows Maxi', 'women', 110.00, 165.00, False, True, '', 'S,M,L', 'White,Ivory', 4.7, 12, 15),
            ('Rosé Champagne Gown', 'women', 199.00, 249.00, True, True, '', 'XS,S,M,L', 'Rose,Champagne,Blush', 4.9, 89, 10),
            ('Emerald Silk Wrap', 'women', 155.00, 200.00, True, True, 'NEW', 'S,M,L,XL', 'Emerald,Forest,Teal', 4.7, 31, 20),
            ('Classic Velvet Mini', 'women', 120.00, 160.00, False, False, '', 'XS,S,M,L', 'Black,Midnight,Navy', 4.6, 28, 30),
            ('Bridal Lace Maxi', 'women', 199.00, 280.00, True, True, 'EXCLUSIVE', 'S,M,L', 'Ivory,White,Champagne', 5.0, 15, 8),
            ('Boho Sundress', 'women', 79.00, 99.00, False, True, 'NEW', 'XS,S,M,L,XL,XXL', 'Terracotta,Olive,Sand', 4.4, 67, 50),
            # Men
            ('Classic Linen Suit', 'men', 249.00, 320.00, False, True, 'NEW', 'S,M,L,XL,XXL', 'Navy,Charcoal,Beige', 4.7, 22, 25),
            ('Slim Fit Blazer', 'men', 189.00, 240.00, True, False, 'SALE-20%', 'S,M,L,XL', 'Black,Navy,Grey', 4.6, 18, 30),
            # Kids
            ('Fairy Princess Dress', 'kids', 49.00, 65.00, False, True, 'NEW', 'XS,S,M', 'Pink,Lilac,Yellow', 4.9, 45, 40),
            ('Party Tuxedo Set', 'kids', 59.00, 75.00, False, False, '', 'XS,S,M,L', 'Black,Navy', 4.7, 22, 35),
            # Accessories
            ('Leather Tote Bag', 'accessories', 89.00, 120.00, True, False, 'SALE-25%', '', 'Black,Brown,Tan', 4.5, 88, 45),
            ('Pearl Earrings Set', 'accessories', 35.00, 50.00, False, True, 'NEW', '', 'Gold,Silver,Rose Gold', 4.8, 134, 80),
        ]

        prod_objs = []
        for data in products_data:
            name, cat_slug, price, orig_price, is_trending, is_new, badge, sizes, colors, rating, reviews, stock = data
            p, _ = Product.objects.get_or_create(
                name=name,
                defaults={
                    'description': f'Premium quality {name}. Crafted from high-grade materials with exceptional attention to detail. Perfect for special occasions and everyday elegance.',
                    'category': cat_objs.get(cat_slug),
                    'price': price,
                    'original_price': orig_price,
                    'is_trending': is_trending,
                    'is_new_arrival': is_new,
                    'badge': badge,
                    'sizes': sizes or 'S,M,L,XL',
                    'colors': colors,
                    'rating': rating,
                    'review_count': reviews,
                    'stock': stock,
                    'status': 'active',
                }
            )
            prod_objs.append(p)
        self.stdout.write(f'✅ {len(prod_objs)} products created')

        # ORDERS
        statuses = ['pending', 'shipped', 'delivered', 'delivered', 'shipped']
        payments = ['card', 'upi', 'cod', 'card', 'card']
        cities = ['Los Angeles', 'New York', 'Chicago', 'Houston', 'Phoenix', 'Miami', 'Seattle']
        order_names = [
            ('Sarah Jenkins', 'sarah.j@email.com'),
            ('Michael Chen', 'm.chen@email.com'),
            ('Emma Wilson', 'emma.w@email.com'),
            ('James Smith', 'j.smith88@email.com'),
            ('Elena Rodriguez', 'elena.rod@email.com'),
            ('Liam Johnson', 'liam.j@email.com'),
            ('Olivia Brown', 'olivia.b@email.com'),
            ('Alex Turner', 'alex.t@email.com'),
        ]

        for i in range(12):
            cust = order_names[i % len(order_names)]
            prod = prod_objs[i % len(prod_objs)]
            oid = f'ORD-{9000 + i}'
            if not Order.objects.filter(order_id=oid).exists():
                user = user_objs[i % len(user_objs)]
                subtotal = float(prod.price) * random.randint(1, 2)
                shipping = 0 if subtotal >= 200 else 12
                tax = round(subtotal * 0.08, 2)
                total = round(subtotal + shipping + tax, 2)
                order = Order.objects.create(
                    order_id=oid,
                    user=user,
                    customer_name=cust[0],
                    customer_email=cust[1],
                    shipping_address=f'{random.randint(100, 999)} Fashion Ave, Apt {random.randint(1, 50)}',
                    city=cities[i % len(cities)],
                    pincode=f'{random.randint(10000, 99999)}',
                    payment_method=payments[i % len(payments)],
                    subtotal=subtotal,
                    shipping_cost=shipping,
                    tax=tax,
                    total=total,
                    status=statuses[i % len(statuses)],
                )
                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    product_name=prod.name,
                    size=random.choice(['S', 'M', 'L']),
                    color=prod.get_colors()[0],
                    quantity=random.randint(1, 2),
                    price=prod.price,
                )

        self.stdout.write('✅ 12 sample orders created')
        self.stdout.write(self.style.SUCCESS('\n🎉 Database seeded successfully!'))
        self.stdout.write('\n📋 LOGIN CREDENTIALS:')
        self.stdout.write('   Admin  → username: admin  | password: admin')
        self.stdout.write('   User 1 → username: sarah_j | password: sarah123')
        self.stdout.write('   User 2 → username: michael_c | password: michael123')
        self.stdout.write('   User 3 → username: emma_w | password: emma123')
