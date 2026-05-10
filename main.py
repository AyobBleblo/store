import os
import django
import random
from decimal import Decimal
from faker import Faker

# إعداد بيئة Django
# استبدل 'your_project_name' باسم مجلد مشروعك الذي يحتوي على settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store.settings')
django.setup()

from store_.models import (
    Customer, Store, Collection, Product, 
    Promotion, Order, OrderItem, Address
)

fake = Faker()

def seed_db():
    count = 200
    print(f"Starting to seed {count} records for each model...")

    # 1. Promotions
    promotions = [
        Promotion(description=fake.sentence(), discount=Decimal(random.uniform(5, 50)))
        for _ in range(20) # 20 خصم كافية لتوزيعها
    ]
    Promotion.objects.bulk_create(promotions)
    all_promotions = list(Promotion.objects.all())

    # 2. Customers
    customers = [
        Customer(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            phone=fake.phone_number()[:20],
            birth_date=fake.date_of_birth(minimum_age=18, maximum_age=70),
            membership=random.choice(['B', 'S', 'G'])
        ) for _ in range(count)
    ]
    Customer.objects.bulk_create(customers)
    all_customers = list(Customer.objects.all())

    # 3. Addresses
    addresses = [
        Address(
            user=random.choice(all_customers),
            city=fake.city(),
            street=fake.street_name(),
            house_number=fake.building_number(),
            is_default=True
        ) for _ in range(count)
    ]
    Address.objects.bulk_create(addresses)

    # 4. Stores
    stores = [
        Store(
            name=f"{fake.company()} Tech Store",
            owner=random.choice(all_customers)
        ) for _ in range(count)
    ]
    Store.objects.bulk_create(stores)
    all_stores = list(Store.objects.all())

    # 5. Collections
    collections = [
        Collection(
            title=fake.word().capitalize(),
            store=random.choice(all_stores)
        ) for _ in range(50) # 50 مجموعة كافية
    ]
    Collection.objects.bulk_create(collections)
    all_collections = list(Collection.objects.all())

    # 6. Products
    products = []
    for i in range(count):
        title = fake.catch_phrase()
        products.append(Product(
            title=title,
            slug=f"{i}-{fake.slug()}", # نضمن slug فريد بإضافة الـ i
            description=fake.text(),
            unit_price=Decimal(random.uniform(10, 1000)),
            inventory=random.randint(1, 100),
            store=random.choice(all_stores),
            collection=random.choice(all_collections),
            is_featured=random.choice([True, False])
        ))
    Product.objects.bulk_create(products)
    all_products = list(Product.objects.all())

    # إضافة Promotions عشوائية للمنتجات (M2M Relationship)
    for product in all_products:
        product.promotions.add(*random.sample(all_promotions, k=random.randint(0, 3)))

    # 7. Orders
    orders = [
        Order(
            customer=random.choice(all_customers),
            payment_status=random.choice(['P', 'C', 'F'])
        ) for _ in range(count)
    ]
    Order.objects.bulk_create(orders)
    all_orders = list(Order.objects.all())

    # 8. Order Items
    order_items = [
        OrderItem(
            order=random.choice(all_orders),
            product=random.choice(all_products),
            quantity=random.randint(1, 5),
            unit_price=random.choice(all_products).unit_price
        ) for _ in range(count * 2) # إنشاء 400 عنصر طلب لتكون البيانات غنية
    ]
    OrderItem.objects.bulk_create(order_items)

    print("Success! Database has been seeded with 200 records per table.")

if __name__ == "__main__":
    seed_db()