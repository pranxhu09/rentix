import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


def _normalize_db_url(url):
    # Render/Heroku-style Postgres URLs start with postgres://, but SQLAlchemy
    # 1.4+ requires postgresql://. Fix it automatically so deployment doesn't break.
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = _normalize_db_url(
        os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(basedir, "rentclone.db"))
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "")
    CURRENCY = os.environ.get("CURRENCY", "INR")

    # Deposit/security charge percentage held on top of rent (business rule, adjust freely)
    SECURITY_DEPOSIT_PERCENT = 20
