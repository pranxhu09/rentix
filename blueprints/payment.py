import razorpay
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from extensions import db
from models import Booking, Payment
import cart as cart_module

payment_bp = Blueprint("payment", __name__, url_prefix="/payment")


def get_razorpay_client():
    return razorpay.Client(
        auth=(current_app.config["RAZORPAY_KEY_ID"], current_app.config["RAZORPAY_KEY_SECRET"])
    )


@payment_bp.route("/pay/<int:booking_id>")
@login_required
def pay(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash("You are not authorized to view this booking.", "danger")
        return redirect(url_for("catalog.home"))

    if booking.status != "pending":
        flash("This booking has already been processed.", "info")
        return redirect(url_for("booking.my_bookings"))

    # Razorpay expects amount in the smallest currency unit (paise for INR)
    amount_paise = int(round(booking.total_amount * 100))

    if not current_app.config["RAZORPAY_KEY_ID"]:
        flash(
            "Payment gateway is not configured yet. Add RAZORPAY_KEY_ID and "
            "RAZORPAY_KEY_SECRET to your .env file to enable checkout.",
            "warning",
        )
        return render_template("booking/payment_not_configured.html", booking=booking)

    client = get_razorpay_client()
    order = client.order.create(
        {
            "amount": amount_paise,
            "currency": current_app.config["CURRENCY"],
            "receipt": f"booking_{booking.id}",
            "payment_capture": 1,
        }
    )

    payment = Payment.query.filter_by(booking_id=booking.id).first()
    if not payment:
        payment = Payment(booking_id=booking.id, amount=booking.total_amount, currency=current_app.config["CURRENCY"])
        db.session.add(payment)
    payment.razorpay_order_id = order["id"]
    payment.status = "created"
    db.session.commit()

    return render_template(
        "booking/checkout_pay.html",
        booking=booking,
        order=order,
        razorpay_key_id=current_app.config["RAZORPAY_KEY_ID"],
        amount_paise=amount_paise,
    )


@payment_bp.route("/verify", methods=["POST"])
@login_required
def verify():
    booking_id = request.form.get("booking_id")
    razorpay_order_id = request.form.get("razorpay_order_id")
    razorpay_payment_id = request.form.get("razorpay_payment_id")
    razorpay_signature = request.form.get("razorpay_signature")

    booking = Booking.query.get_or_404(booking_id)
    payment = Payment.query.filter_by(booking_id=booking.id).first()

    client = get_razorpay_client()
    params = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
    }

    try:
        client.utility.verify_payment_signature(params)
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = "paid"
        booking.status = "confirmed"
        db.session.commit()

        cart_module.clear_cart()
        flash("Payment successful! Your booking is confirmed.", "success")
        return redirect(url_for("booking.my_bookings"))
    except razorpay.errors.SignatureVerificationError:
        payment.status = "failed"
        db.session.commit()
        flash("Payment verification failed. Please try again or contact support.", "danger")
        return redirect(url_for("payment.pay", booking_id=booking.id))
