# RentClone

A Flask + SQLite rental marketplace (bikes, cameras, gaming consoles, projectors,
party speakers) inspired by the general concept of sites like Rentix — built from
scratch with its own code, content, and design, not copied from any source.

## Features
- Product catalog with categories, search, product detail pages
- Session-based cart with date-range selection
- Availability checking that accounts for overlapping bookings
- User registration/login (Flask-Login, hashed passwords)
- Checkout → booking creation → **Razorpay** payment integration (test mode ready)
- Payment signature verification on the backend (never trust client-side "success" alone)
- Admin panel: manage products, categories, and booking statuses
- Dark UI styled with plain CSS (no frontend framework required)

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # then edit .env with your own SECRET_KEY and Razorpay keys
python seed.py                  # creates tables + sample data + admin user
python app.py                   # runs at http://127.0.0.1:5000
```

Default admin login (created by `seed.py`): `admin@example.com` / `admin123`
**Change this immediately if you deploy anywhere public.**

## Razorpay setup (for real payments)
1. Create a free account at https://dashboard.razorpay.com/
2. Grab your **test mode** Key ID and Key Secret from Settings → API Keys
3. Put them in `.env` as `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`
4. Use Razorpay's test card `4111 1111 1111 1111` (any future expiry, any CVV) to
   simulate a successful payment without moving real money
5. Switch to live keys only once you're ready to accept real payments — Razorpay
   requires KYC/business verification before enabling live mode

## Project structure
```
rentclone/
├── app.py                # Flask app factory
├── config.py              # env-based config
├── extensions.py          # db, login_manager singletons
├── models.py              # User, Category, Product, Booking, BookingItem, Payment
├── forms.py                # WTForms
├── cart.py                  # session cart helper
├── seed.py                   # sample data loader
├── blueprints/
│   ├── auth.py             # register/login/logout
│   ├── catalog.py          # home, categories, product pages, search
│   ├── booking.py           # cart, checkout, my bookings
│   ├── payment.py            # Razorpay order + verification
│   └── admin.py               # admin CRUD + booking management
├── templates/
└── static/css/style.css
```

## Deploying live (Render, free tier)
1. Push this folder to a GitHub repo.
2. On render.com: New → Web Service → connect the repo.
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
3. New → PostgreSQL (free tier) → copy its connection string into the web
   service's `DATABASE_URL` environment variable.
4. Add `SECRET_KEY`, `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET` as environment
   variables too.
5. After first deploy, open the Render Shell for the service and run
   `python seed.py` once to create tables and sample data.

Your site will be live at `https://<your-service-name>.onrender.com`.
(`Procfile` and `gunicorn`/`psycopg2-binary` are already included for this.)

## Things to harden before going live
- Move off SQLite to Postgres/MySQL for concurrent traffic
- Add rate limiting on login/register (e.g. Flask-Limiter)
- Add CSRF-safe file uploads for product images (currently URL-only)
- Add email confirmation and password reset flows
- Add Razorpay webhook handling (`payment.captured`, `payment.failed`) as a
  backup to client-side verification, in case the user closes the tab mid-payment
- Add proper logging/monitoring and a production WSGI server (gunicorn + nginx)
