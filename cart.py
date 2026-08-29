"""
Session-based cart. Stores product_id -> quantity, plus rental dates,
in the Flask session so it survives across requests without a DB write
until checkout actually happens.
"""
from flask import session

CART_KEY = "cart"
DATES_KEY = "cart_dates"


def get_cart():
    return session.get(CART_KEY, {})


def save_cart(cart):
    session[CART_KEY] = cart
    session.modified = True


def add_item(product_id, quantity=1):
    cart = get_cart()
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + quantity
    save_cart(cart)


def update_item(product_id, quantity):
    cart = get_cart()
    pid = str(product_id)
    if quantity <= 0:
        cart.pop(pid, None)
    else:
        cart[pid] = quantity
    save_cart(cart)


def remove_item(product_id):
    cart = get_cart()
    cart.pop(str(product_id), None)
    save_cart(cart)


def clear_cart():
    session.pop(CART_KEY, None)
    session.pop(DATES_KEY, None)
    session.modified = True


def set_dates(start_date, end_date):
    session[DATES_KEY] = {"start": start_date.isoformat(), "end": end_date.isoformat()}
    session.modified = True


def get_dates():
    return session.get(DATES_KEY)
