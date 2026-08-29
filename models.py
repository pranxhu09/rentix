from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship("Booking", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    icon = db.Column(db.String(50), default="box")  # icon key for frontend

    products = db.relationship("Product", backref="category", lazy=True)


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    slug = db.Column(db.String(160), unique=True, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(300))
    price_per_day = db.Column(db.Float, nullable=False)
    quantity_available = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    booking_items = db.relationship("BookingItem", backref="product", lazy=True)

    def is_available_between(self, start_date, end_date, exclude_booking_id=None):
        """Check how many units are free for a date range (naive overlap check)."""
        overlapping = BookingItem.query.join(Booking).filter(
            BookingItem.product_id == self.id,
            Booking.status.in_(["pending", "confirmed"]),
            Booking.start_date < end_date,
            Booking.end_date > start_date,
        )
        if exclude_booking_id:
            overlapping = overlapping.filter(Booking.id != exclude_booking_id)
        reserved = sum(item.quantity for item in overlapping)
        return self.quantity_available - reserved


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    subtotal = db.Column(db.Float, nullable=False, default=0)
    deposit_amount = db.Column(db.Float, nullable=False, default=0)
    total_amount = db.Column(db.Float, nullable=False, default=0)
    status = db.Column(
        db.String(20), default="pending"
    )  # pending, confirmed, cancelled, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship(
        "BookingItem", backref="booking", lazy=True, cascade="all, delete-orphan"
    )
    payment = db.relationship("Payment", backref="booking", uselist=False)

    @property
    def rental_days(self):
        return max((self.end_date - self.start_date).days, 1)


class BookingItem(db.Model):
    __tablename__ = "booking_items"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price_per_day = db.Column(db.Float, nullable=False)  # snapshot at booking time

    @property
    def line_total(self):
        return self.quantity * self.price_per_day


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    razorpay_order_id = db.Column(db.String(100))
    razorpay_payment_id = db.Column(db.String(100))
    razorpay_signature = db.Column(db.String(255))
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default="INR")
    status = db.Column(db.String(20), default="created")  # created, paid, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
