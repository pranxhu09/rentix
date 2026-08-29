from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from extensions import db
from models import Product, Booking, BookingItem
import cart as cart_module
from config import Config

booking_bp = Blueprint("booking", __name__, url_prefix="/booking")


def _parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


@booking_bp.route("/cart")
def view_cart():
    raw_cart = cart_module.get_cart()
    dates = cart_module.get_dates()
    items = []
    subtotal = 0

    start_date = end_date = None
    days = 1
    if dates:
        start_date = _parse_date(dates["start"])
        end_date = _parse_date(dates["end"])
        days = max((end_date - start_date).days, 1)

    for pid, qty in raw_cart.items():
        product = Product.query.get(int(pid))
        if not product:
            continue
        line_total = product.price_per_day * qty * days
        subtotal += line_total
        items.append({"product": product, "quantity": qty, "line_total": line_total})

    deposit = round(subtotal * Config.SECURITY_DEPOSIT_PERCENT / 100, 2)
    total = subtotal + deposit

    return render_template(
        "booking/cart.html",
        items=items,
        subtotal=subtotal,
        deposit=deposit,
        total=total,
        start_date=start_date,
        end_date=end_date,
        days=days,
    )


@booking_bp.route("/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get("quantity", 1))
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    if not start_date or not end_date:
        flash("Please choose start and end dates before adding to cart.", "warning")
        return redirect(url_for("catalog.product_detail", slug=product.slug))

    sd = _parse_date(start_date)
    ed = _parse_date(end_date)
    if ed <= sd:
        flash("End date must be after the start date.", "warning")
        return redirect(url_for("catalog.product_detail", slug=product.slug))

    available = product.is_available_between(sd, ed)
    if available < quantity:
        flash(f"Only {available} unit(s) of {product.name} are available for those dates.", "danger")
        return redirect(url_for("catalog.product_detail", slug=product.slug))

    cart_module.set_dates(sd, ed)
    cart_module.add_item(product_id, quantity)
    flash(f"{product.name} added to your cart.", "success")
    return redirect(url_for("booking.view_cart"))


@booking_bp.route("/update/<int:product_id>", methods=["POST"])
def update_cart_item(product_id):
    quantity = int(request.form.get("quantity", 1))
    cart_module.update_item(product_id, quantity)
    return redirect(url_for("booking.view_cart"))


@booking_bp.route("/remove/<int:product_id>", methods=["POST"])
def remove_cart_item(product_id):
    cart_module.remove_item(product_id)
    flash("Item removed from cart.", "info")
    return redirect(url_for("booking.view_cart"))


@booking_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    raw_cart = cart_module.get_cart()
    dates = cart_module.get_dates()

    if not raw_cart or not dates:
        flash("Your cart is empty.", "info")
        return redirect(url_for("catalog.home"))

    start_date = _parse_date(dates["start"])
    end_date = _parse_date(dates["end"])
    days = max((end_date - start_date).days, 1)

    # Re-validate availability at checkout time to avoid race conditions
    booking_items = []
    subtotal = 0
    for pid, qty in raw_cart.items():
        product = Product.query.get(int(pid))
        if not product:
            continue
        available = product.is_available_between(start_date, end_date)
        if available < qty:
            flash(f"{product.name} no longer has enough stock for those dates. Please update your cart.", "danger")
            return redirect(url_for("booking.view_cart"))
        line_total = product.price_per_day * qty * days
        subtotal += line_total
        booking_items.append((product, qty))

    deposit = round(subtotal * Config.SECURITY_DEPOSIT_PERCENT / 100, 2)
    total = subtotal + deposit

    booking = Booking(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        subtotal=subtotal,
        deposit_amount=deposit,
        total_amount=total,
        status="pending",
    )
    db.session.add(booking)
    db.session.flush()  # get booking.id before commit

    for product, qty in booking_items:
        item = BookingItem(
            booking_id=booking.id,
            product_id=product.id,
            quantity=qty,
            price_per_day=product.price_per_day,
        )
        db.session.add(item)

    db.session.commit()

    return redirect(url_for("payment.pay", booking_id=booking.id))


@booking_bp.route("/my-bookings")
@login_required
def my_bookings():
    bookings = (
        Booking.query.filter_by(user_id=current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )
    return render_template("booking/my_bookings.html", bookings=bookings)
