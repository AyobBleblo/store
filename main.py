import os
import django
import random
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.utils.text import slugify
from faker import Faker

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store.settings')
django.setup()

from django.contrib.auth import get_user_model
from store_.models import (
    Customer, Store, Collection, Product, 
    Promotion, Order, OrderItem, Address, Review
)

User = get_user_model()
fake = Faker()

# High-quality hand-crafted products to start with
PREMIUM_PRODUCTS = [
    # Laptops & Computers
    {
        "title": "MacBook Pro 16\" (M3 Max)",
        "category": "Laptops & Computers",
        "description": "The ultimate professional laptop. Features a gorgeous 16-inch Liquid Retina XDR display, Apple M3 Max chip with 16-core CPU and 40-core GPU, 36GB unified memory, and 1TB ultra-fast SSD storage. Perfect for video editing, software development, and 3D rendering.",
        "min_price": 2499,
        "max_price": 3499
    },
    {
        "title": "Dell XPS 15 OLED",
        "category": "Laptops & Computers",
        "description": "Stunning 15.6-inch 3.5K OLED touch display, 13th Gen Intel Core i7 processor, 32GB DDR5 RAM, and NVIDIA GeForce RTX 4060 graphics. Sleek aluminum chassis with carbon fiber palm rest.",
        "min_price": 1899,
        "max_price": 2299
    },
    {
        "title": "ASUS ROG Zephyrus G14",
        "category": "Laptops & Computers",
        "description": "Powerful yet ultra-portable gaming laptop. Features AMD Ryzen 9 processor, NVIDIA GeForce RTX 4070, 16GB DDR5 RAM, and a beautiful 14-inch 120Hz ROG Nebula HDR display.",
        "min_price": 1599,
        "max_price": 1799
    },
    {
        "title": "Lenovo ThinkPad X1 Carbon Gen 11",
        "category": "Laptops & Computers",
        "description": "The benchmark for business professionals. Ultra-light carbon fiber chassis, Intel Evo vPro platform with 13th Gen Core i7, 16GB RAM, legendary spill-resistant keyboard, and robust security features.",
        "min_price": 1699,
        "max_price": 1999
    },
    # Smartphones & Tablets
    {
        "title": "iPhone 15 Pro Max",
        "category": "Smartphones & Tablets",
        "description": "Forged in titanium. Features the groundbreaking A17 Pro chip, customizable Action button, the most powerful iPhone camera system ever with 5x optical zoom, and outstanding battery life.",
        "min_price": 1199,
        "max_price": 1499
    },
    {
        "title": "Samsung Galaxy S24 Ultra",
        "category": "Smartphones & Tablets",
        "description": "Welcome to the era of mobile AI. 200MP camera, built-in S Pen, Snapdragon 8 Gen 3, and a stunning flat 6.8-inch Dynamic AMOLED 2X display with titanium frame.",
        "min_price": 1299,
        "max_price": 1599
    },
    {
        "title": "Google Pixel 8 Pro",
        "category": "Smartphones & Tablets",
        "description": "The all-pro phone engineered by Google. Features the Google Tensor G3 chip, best-in-class camera with advanced AI photo and video editing (Magic Eraser, Best Take), and Gemini Nano AI built-in.",
        "min_price": 999,
        "max_price": 1199
    },
    {
        "title": "iPad Pro 12.9-inch (M2)",
        "category": "Smartphones & Tablets",
        "description": "Astonishing performance with the Apple M2 chip, brilliant Liquid Retina XDR display with ProMotion, and support for Apple Pencil (2nd Gen) and Magic Keyboard. A complete workstation in your hands.",
        "min_price": 1099,
        "max_price": 1399
    },
    # Audio & Headphones
    {
        "title": "Sony WH-1000XM5 ANC Headphones",
        "category": "Audio & Headphones",
        "description": "Industry-leading active noise cancellation, magnificent high-resolution sound quality, smart listening technology, and crystal-clear hands-free calling with 30-hour battery life.",
        "min_price": 349,
        "max_price": 399
    },
    {
        "title": "Apple AirPods Pro (2nd Gen)",
        "category": "Audio & Headphones",
        "description": "Re-engineered sound. Up to 2x more Active Noise Cancellation, Adaptive Audio, Transparency mode, and personalized Spatial Audio. Charging case features USB-C and speaker for Find My locator.",
        "min_price": 229,
        "max_price": 249
    },
    {
        "title": "Bose QuietComfort Ultra",
        "category": "Audio & Headphones",
        "description": "World-class noise cancelling headphones with customisable sound, modern design, and immersive spatial audio that makes your music feel more real than ever.",
        "min_price": 379,
        "max_price": 429
    },
    {
        "title": "Sonos Era 300 Smart Speaker",
        "category": "Audio & Headphones",
        "description": "With six optimally positioned drivers all around, Era 300 projects sound from wall to wall and ceiling to floor, wrapping you in an immersive Dolby Atmos spatial audio experience.",
        "min_price": 449,
        "max_price": 449
    },
    # Smart Home Devices
    {
        "title": "Google Nest Hub Max",
        "category": "Smart Home Devices",
        "description": "Smart display with Google Assistant, built-in Nest Cam for home security, and a gorgeous 10-inch HD screen. Control your smart home, make video calls, and stream your favorite content.",
        "min_price": 229,
        "max_price": 229
    },
    {
        "title": "Philips Hue Starter Kit",
        "category": "Smart Home Devices",
        "description": "Set the perfect mood with millions of colors. Includes the Hue Bridge router and three color-changing smart LED bulbs. Fully compatible with Alexa, Apple Home, and Google Home.",
        "min_price": 179,
        "max_price": 199
    },
    {
        "title": "Ring Video Doorbell 4",
        "category": "Smart Home Devices",
        "description": "1080p HD video doorbell with improved dual-band Wi-Fi, color Pre-Roll video previews, custom privacy zones, and rechargeable battery pack or hardwired connection.",
        "min_price": 149,
        "max_price": 159
    },
    {
        "title": "Ecobee Smart Thermostat Premium",
        "category": "Smart Home Devices",
        "description": "Save on heating and cooling energy bills with smart scheduling and occupancy detection. Includes a smart room sensor and features a built-in indoor air quality monitor.",
        "min_price": 249,
        "max_price": 249
    },
    # Gaming & Consoles
    {
        "title": "PlayStation 5 Slim",
        "category": "Gaming & Consoles",
        "description": "Experience lightning-fast loading with an ultra-high speed SSD, deeper immersion with support for haptic feedback, adaptive triggers, and 3D Audio, and an all-new generation of incredible PlayStation games.",
        "min_price": 449,
        "max_price": 499
    },
    {
        "title": "Xbox Series X",
        "category": "Gaming & Consoles",
        "description": "The fastest, most powerful Xbox ever. Explore rich new worlds with 12 teraflops of raw graphic processing power, DirectX ray tracing, custom 1TB SSD, and 4K gaming at up to 120FPS.",
        "min_price": 449,
        "max_price": 499
    },
    {
        "title": "Nintendo Switch OLED Model",
        "category": "Gaming & Consoles",
        "description": "Vibrant 7-inch OLED screen, a wide adjustable stand for tabletop mode, a new dock with a wired LAN port, 64GB of internal storage, and enhanced audio in handheld and tabletop modes.",
        "min_price": 349,
        "max_price": 349
    },
    {
        "title": "Steam Deck 512GB OLED",
        "category": "Gaming & Consoles",
        "description": "The ultimate portable gaming PC. Features a high-contrast HDR OLED screen, longer battery life, faster Wi-Fi 6E, and incredibly comfortable console-grade controls for your entire Steam library.",
        "min_price": 549,
        "max_price": 549
    },
    # Wearable Tech
    {
        "title": "Apple Watch Ultra 2",
        "category": "Wearable Tech",
        "description": "The ultimate sports and adventure watch. Rugged 49mm titanium case, up to 36-hour battery life, dual-frequency GPS, cellular connectivity, and Apple's brightest-ever Always-On Retina display.",
        "min_price": 799,
        "max_price": 799
    },
    {
        "title": "Samsung Galaxy Watch 6 Pro",
        "category": "Wearable Tech",
        "description": "Personalised heart rate zones, advanced sleep coaching, body composition analysis, and a sleek modern sapphire crystal glass design with rotating bezel.",
        "min_price": 299,
        "max_price": 349
    },
    {
        "title": "Garmin Fenix 7X Pro Solar",
        "category": "Wearable Tech",
        "description": "Premium multisport GPS watch with solar charging lens, built-in LED flashlight, advanced training metrics, and preloaded TopoActive maps for ultimate outdoor navigation.",
        "min_price": 799,
        "max_price": 899
    },
    {
        "title": "Fitbit Charge 6 NFC",
        "category": "Wearable Tech",
        "description": "Advanced health and fitness tracker with Google apps integration, built-in GPS, 24/7 heart rate monitoring, sleep score tracking, and up to 7 days of battery life.",
        "min_price": 149,
        "max_price": 159
    }
]

# Curated electronic lists for dynamic generation
BRANDS = [
    "Apple", "Samsung", "Sony", "Dell", "HP", "Lenovo", "ASUS", "Bose", 
    "Sennheiser", "Logitech", "Razer", "Microsoft", "Google", "Xiaomi", 
    "Anker", "Garmin", "Sonos", "GoPro", "Intel", "AMD", "NVIDIA", 
    "OnePlus", "Huawei", "Fitbit", "JBL", "Marshall", "Corsair"
]

ADJECTIVES = [
    "Pro", "Ultra", "Max", "Air", "Elite", "Plus", "Prime", "Extreme", 
    "Core", "Essential", "Wireless", "Smart", "Studio", "Carbon", 
    "Signature", "Super", "Quantum", "Nexus", "Matrix", "Apex"
]

PRODUCT_TYPES = {
    "Laptops & Computers": [
        ("Laptop", 700, 2500), 
        ("Desktop PC", 800, 3000), 
        ("All-in-One PC", 900, 2200), 
        ("Gaming Rig", 1200, 4000), 
        ("Ultrabook", 800, 1800), 
        ("Chromebook", 200, 600)
    ],
    "Smartphones & Tablets": [
        ("Smartphone", 300, 1200), 
        ("Tablet", 250, 1000), 
        ("Foldable Phone", 1300, 2000), 
        ("E-Reader", 90, 250)
    ],
    "Audio & Headphones": [
        ("Wireless Headphones", 80, 450), 
        ("Noise Cancelling Earbuds", 50, 300), 
        ("Soundbar", 150, 800), 
        ("Bluetooth Speaker", 40, 400), 
        ("Studio Monitor Speakers", 200, 1200)
    ],
    "Smart Home Devices": [
        ("Smart Thermostat", 120, 280), 
        ("Security Camera", 50, 300), 
        ("Smart Light Bulb Pack", 30, 150), 
        ("Smart Plug Duo", 15, 50), 
        ("Voice Assistant Hub", 50, 250)
    ],
    "Gaming & Consoles": [
        ("Console", 299, 499), 
        ("Gaming Controller", 50, 180), 
        ("VR Headset", 300, 1000), 
        ("Mechanical Keyboard", 80, 250), 
        ("Gaming Mouse", 40, 150)
    ],
    "Wearable Tech": [
        ("Smartwatch", 150, 800), 
        ("Fitness Tracker", 50, 200), 
        ("GPS Sports Watch", 200, 900), 
        ("Smart Ring", 250, 400)
    ],
    "Cameras & Drones": [
        ("Mirrorless Camera", 800, 3000), 
        ("Action Camera", 200, 500), 
        ("Quadcopter Drone", 400, 2000), 
        ("Gimbal Stabilizer", 80, 250)
    ],
    "Accessories & Gadgets": [
        ("Power Bank", 20, 80), 
        ("USB-C Hub", 30, 120), 
        ("Wireless Charger", 15, 75), 
        ("External SSD", 70, 300), 
        ("Ergonomic Office Chair", 150, 600)
    ]
}

STORE_NAMES = [
    "TechVibe Electronics", "GizmoPlanet", "PixelCraft Systems", "Apex Gaming Hub",
    "SoundSphere Audio", "ElectroMart", "CyberSpace Solutions", "Quantum Computing Co.",
    "Omega Tech Plaza", "Alpha Digital Hub", "Matrix Devices"
]

PROMOTION_TEMPLATES = [
    ("Summer Sale Special", 10),
    ("Black Friday Deal", 25),
    ("Cyber Monday Madness", 20),
    ("New User Welcome Discount", 15),
    ("Holiday Clearance Event", 30),
    ("Spring Renewal Discount", 12),
    ("Back to School Offer", 15),
    ("VIP Exclusive Saving", 18),
    ("Weekly Flash Sale", 10),
    ("Bundle & Save Discount", 5)
]

def seed_db():
    # Target record counts
    count = 200
    
    print("==================================================")
    print("  SEEDING DJANGO DATABASE WITH REALISTIC DUMMY DATA  ")
    print("==================================================")
    
    # 0. Clean Existing Data to avoid constraint/uniqueness errors
    print("Cleaning up old generated records to avoid conflicts...")
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    Address.objects.all().delete()
    Review.objects.all().delete()
    
    # Break circular dependencies for Collections
    Collection.objects.update(featured_product=None)
    Product.objects.all().delete()
    Collection.objects.all().delete()
    Store.objects.all().delete()
    Customer.objects.all().delete()
    
    # Delete generated users but preserve superusers and staff!
    staff_and_supers = User.objects.filter(is_superuser=True) | User.objects.filter(is_staff=True)
    preserved_ids = list(staff_and_supers.values_list('id', flat=True))
    
    User.objects.exclude(id__in=preserved_ids).delete()
    print("Cleanup completed successfully.")
    
    # 1. Promotions
    print("\nGenerating promotions...")
    # Delete existing promotions to ensure fresh templates
    Promotion.objects.all().delete()
    promotions = [
        Promotion(
            description=f"{template[0]} - Save {template[1]}% on your purchase!",
            discount=Decimal(template[1])
        )
        for template in PROMOTION_TEMPLATES
    ]
    Promotion.objects.bulk_create(promotions)
    all_promotions = list(Promotion.objects.all())
    print(f"Created {len(all_promotions)} realistic promotions.")
    
    # 2. Users and Customers
    print("\nGenerating users and customers...")
    customers = []
    
    # Pre-generate emails to avoid Faker collisions
    fake_emails = set()
    while len(fake_emails) < count:
        fake_emails.add(fake.unique.email())
    emails_list = list(fake_emails)
    
    for i in range(count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = f"{first_name.lower()}_{last_name.lower()}_{random.randint(100, 999)}"
        email = emails_list[i]
        
        # Create core User
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password='password123'
        )
        
        # Create Customer associated with the User
        customer = Customer(
            user=user,
            phone=fake.phone_number()[:20],
            birth_date=fake.date_of_birth(minimum_age=18, maximum_age=70),
            membership=random.choice(['B', 'S', 'G'])
        )
        customers.append(customer)
        
    Customer.objects.bulk_create(customers)
    all_customers = list(Customer.objects.all())
    print(f"Created {len(all_customers)} Users and linked Customer records (Password: password123).")
    
    # 3. Addresses
    print("\nGenerating customer addresses...")
    addresses = [
        Address(
            user=customer,
            city=fake.city(),
            street=fake.street_name(),
            house_number=fake.building_number(),
            zip_code=fake.postcode(),
            is_default=True
        ) for customer in all_customers
    ]
    Address.objects.bulk_create(addresses)
    print(f"Created {len(addresses)} billing/shipping addresses.")
    
    # 4. Stores
    print("\nGenerating retail stores...")
    stores = []
    for name in STORE_NAMES:
        owner = random.choice(all_customers)
        stores.append(Store(name=name, owner=owner))
    Store.objects.bulk_create(stores)
    all_stores = list(Store.objects.all())
    print(f"Created {len(all_stores)} tech retail stores.")
    
    # 5. Collections
    print("\nGenerating product collections...")
    collections = []
    categories = list(PRODUCT_TYPES.keys())
    
    for category in categories:
        store = random.choice(all_stores)
        collections.append(Collection(title=category, store=store))
    Collection.objects.bulk_create(collections)
    all_collections = list(Collection.objects.all())
    print(f"Created {len(all_collections)} product collections matching tech categories.")
    
    # Map Collection title to its object for easier product seeding
    collection_map = {col.title: col for col in all_collections}
    
    # 6. Products
    print("\nGenerating premium products...")
    products = []
    slug_set = set()
    
    # Add high-quality Premium products first
    for i, item in enumerate(PREMIUM_PRODUCTS):
        title = item["title"]
        category = item["category"]
        description = item["description"]
        
        price = Decimal(round(random.uniform(item["min_price"], item["max_price"]), 2))
        inventory = random.randint(5, 50)
        store = random.choice(all_stores)
        collection = collection_map[category]
        
        base_slug = slugify(title)
        slug = base_slug
        suffix = 1
        while slug in slug_set:
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        slug_set.add(slug)
        
        products.append(Product(
            title=title,
            slug=slug,
            description=description,
            unit_price=price,
            inventory=inventory,
            store=store,
            collection=collection,
            is_featured=random.choice([True, False])
        ))
        
    # Generate remaining products to reach count
    remaining_count = count - len(PREMIUM_PRODUCTS)
    for i in range(remaining_count):
        category = random.choice(categories)
        collection = collection_map[category]
        store = random.choice(all_stores)
        
        brand = random.choice(BRANDS)
        adj = random.choice(ADJECTIVES)
        type_info = random.choice(PRODUCT_TYPES[category])
        type_name, min_p, max_p = type_info
        
        title = f"{brand} {adj} {type_name}"
        if any(p.title == title for p in products):
            title = f"{brand} {adj} {type_name} {random.randint(100, 999)}"
            
        description = f"Experience the future with the {title}. This premium quality {type_name.lower()} is designed for exceptional performance and built to last. Perfect for professional, home, and on-the-go use. Features state of the art specifications and a sleek modern aesthetic."
        
        price = Decimal(round(random.uniform(min_p, max_p), 2))
        inventory = random.randint(0, 100)
        
        base_slug = slugify(title)
        slug = base_slug
        suffix = 1
        while slug in slug_set:
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        slug_set.add(slug)
        
        products.append(Product(
            title=title,
            slug=slug,
            description=description,
            unit_price=price,
            inventory=inventory,
            store=store,
            collection=collection,
            is_featured=random.choice([True, False])
        ))
        
    Product.objects.bulk_create(products)
    all_products = list(Product.objects.all())
    print(f"Created {len(all_products)} highly realistic e-commerce products.")
    
    # Add Promotions to Products (M2M Relationship)
    print("Assigning random promotions to products...")
    for product in all_products:
        if random.random() < 0.35:
            k = random.randint(1, 2)
            promos = random.sample(all_promotions, k=k)
            product.promotions.add(*promos)
            
    # Set a featured product for each collection
    print("Setting a featured product for each collection...")
    for collection in all_collections:
        col_products = [p for p in all_products if p.collection_id == collection.id]
        if col_products:
            collection.featured_product = random.choice(col_products)
            collection.save()
            
    # 7. Orders and OrderItems
    print("\nGenerating orders and purchase history...")
    orders = []
    
    for _ in range(count):
        customer = random.choice(all_customers)
        status = random.choices(
            ['C', 'P', 'F'],
            weights=[70, 20, 10],
            k=1
        )[0]
        orders.append(Order(customer=customer, payment_status=status))
        
    Order.objects.bulk_create(orders)
    all_orders = list(Order.objects.all())
    
    # 8. Order Items
    order_items = []
    for order in all_orders:
        num_items = random.randint(1, 4)
        purchased_products = random.sample(all_products, k=num_items)
        
        for prod in purchased_products:
            order_items.append(OrderItem(
                order=order,
                product=prod,
                quantity=random.randint(1, 3),
                unit_price=prod.unit_price
            ))
            
    OrderItem.objects.bulk_create(order_items)
    print(f"Created {len(all_orders)} customer orders containing a total of {len(order_items)} items.")
    
    # 9. Reviews
    print("\nGenerating product reviews...")
    reviews = []
    review_comments = {
        5: [
            "Absolutely amazing! Exceeded all my expectations.",
            "Best purchase I've made this year. High quality and works perfectly.",
            "Unbelievable value for money. Highly recommend to everyone!",
            "Outstanding performance! Very sleek design and easy to use.",
            "Excellent build quality and premium feel. Worth every penny!"
        ],
        4: [
            "Great product, works as advertised. Very solid build.",
            "Very satisfied with the quality. Decent price and fast delivery.",
            "Solid performance and does exactly what I needed it for.",
            "Really good value. Minor cosmetic details could be improved, but otherwise great.",
            "Works very well, would definitely buy again!"
        ],
        3: [
            "It's decent, but has a few minor flaws. Satisfactory for the price.",
            "Average quality. Nothing exceptional but gets the job done.",
            "Good, but could be better. The interface takes some getting used to.",
            "Standard product. It's okay, but feels a bit expensive for what it is."
        ],
        2: [
            "Somewhat disappointed. Build quality feels a bit cheap.",
            "Not worth the premium price. Had some connectivity issues.",
            "Wouldn't really recommend it unless it's on a deep discount.",
            "The performance is sub-par compared to cheaper alternatives."
        ],
        1: [
            "Extremely disappointed. Stopped working after three days of light use.",
            "Terrible experience. The item feels very fragile and cheap.",
            "Waste of money. Would not recommend to anyone. Returning it immediately.",
            "Absolute junk. Falsely advertised and poorly built."
        ]
    }
    
    for _ in range(150):
        product = random.choice(all_products)
        rating = random.choices([5, 4, 3, 2, 1], weights=[55, 25, 12, 5, 3])[0]
        name = fake.name()
        description = random.choice(review_comments[rating])
        reviews.append(Review(
            product=product,
            name=name,
            description=description,
            rating=rating
        ))
    Review.objects.bulk_create(reviews)
    print(f"Created {len(reviews)} realistic product reviews.")
    
    # 10. Update timestamps for Orders to spread them realistically over the last 30 days
    print("\nSpreading orders over the last 30 days for realistic sales timelines...")
    now = timezone.now()
    for order in all_orders:
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        historical_date = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        Order.objects.filter(pk=order.pk).update(placed_at=historical_date)
        
    print("\n==================================================")
    print("SUCCESS: Database has been successfully populated!")
    print("==================================================")
    print(f"- Preserved Admin Logins : {len(preserved_ids)}")
    print(f"- New Active Customers   : {Customer.objects.count()}")
    print(f"- Tech Retail Stores     : {Store.objects.count()}")
    print(f"- Active Product Ranges  : {Product.objects.count()}")
    print(f"- Purchase Orders Seeded : {Order.objects.count()}")
    print(f"- Total Items Ordered    : {OrderItem.objects.count()}")
    print(f"- Customer Reviews       : {Review.objects.count()}")
    print("==================================================")

if __name__ == "__main__":
    seed_db()