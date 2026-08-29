"""
Run once to populate the database with sample categories/products and an
admin account, so you have something to click through immediately:

    python seed.py
"""
from app import create_app
from extensions import db
from models import User, Category, Product

app = create_app()

with app.app_context():
    db.create_all()

    if not User.query.filter_by(email="admin@example.com").first():
        admin = User(name="Admin", email="admin@example.com", is_admin=True)
        admin.set_password("admin123")
        db.session.add(admin)
        print("Created admin user: admin@example.com / admin123")

    categories_data = [
        ("Bikes", "bikes", "bike"),
        ("Cameras", "cameras", "camera"),
        ("Gaming Consoles", "gaming-consoles", "gamepad"),
        ("Projectors", "projectors", "projector"),
        ("Party Speakers", "party-speakers", "speaker"),
    ]

    slug_to_category = {}
    for name, slug, icon in categories_data:
        cat = Category.query.filter_by(slug=slug).first()
        if not cat:
            cat = Category(name=name, slug=slug, icon=icon)
            db.session.add(cat)
            db.session.flush()
            print(f"Created category: {name}")
        slug_to_category[slug] = cat

    products_data = [
        ("Royal Enfield Classic 350", "royal-enfield-classic-350", "bikes", 799, 3,
         "A smooth, torquey cruiser perfect for weekend rides."),
        ("Honda Activa 6G", "honda-activa-6g", "bikes", 299, 5,
         "Reliable city scooter, easy on fuel and easy to ride."),
        ("Canon EOS R10", "canon-eos-r10", "cameras", 899, 2,
         "Mirrorless camera great for events, travel, and video."),
        ("DJI Mini 4 Pro Drone", "dji-mini-4-pro", "cameras", 1499, 1,
         "Compact drone with 4K stabilized footage."),
        ("Sony PlayStation 5", "sony-ps5", "gaming-consoles", 599, 4,
         "Latest-gen console with two controllers included."),
        ("BenQ Full HD Projector", "benq-full-hd-projector", "projectors", 699, 2,
         "Bright 1080p projector, ideal for movie nights and presentations."),
        ("JBL PartyBox 310", "jbl-partybox-310", "party-speakers", 999, 2,
         "Powerful party speaker with lights, great for events."),
    ]

    for name, slug, cat_slug, price, qty, desc in products_data:
        if not Product.query.filter_by(slug=slug).first():
            product = Product(
                name=name,
                slug=slug,
                description=desc,
                price_per_day=price,
                quantity_available=qty,
                category_id=slug_to_category[cat_slug].id,
                image_url=f"https://placehold.co/600x400?text={name.replace(' ', '+')}",
                is_active=True,
            )
            db.session.add(product)
            print(f"Created product: {name}")

    db.session.commit()
    print("\nSeeding complete.")
