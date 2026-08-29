from flask import Blueprint, render_template, request, abort

from models import Category, Product

catalog_bp = Blueprint("catalog", __name__)


@catalog_bp.route("/")
def home():
    categories = Category.query.all()
    featured = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(8).all()
    return render_template("catalog/home.html", categories=categories, featured=featured)


@catalog_bp.route("/category/<slug>")
def category_detail(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    products = Product.query.filter_by(category_id=category.id, is_active=True).all()
    return render_template("catalog/category.html", category=category, products=products)


@catalog_bp.route("/product/<slug>")
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    related = (
        Product.query.filter_by(category_id=product.category_id, is_active=True)
        .filter(Product.id != product.id)
        .limit(4)
        .all()
    )
    return render_template("catalog/product.html", product=product, related=related)


@catalog_bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = []
    if q:
        results = Product.query.filter(
            Product.is_active == True,  # noqa: E712
            Product.name.ilike(f"%{q}%"),
        ).all()
    return render_template("catalog/search.html", query=q, results=results)
