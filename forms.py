from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, TextAreaField, FloatField,
    IntegerField, SelectField, DateField, BooleanField
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange


class RegisterForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=160)])
    phone = StringField("Phone", validators=[Length(max=20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match")],
    )


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")


class BookingDatesForm(FlaskForm):
    start_date = DateField("Start date", validators=[DataRequired()])
    end_date = DateField("End date", validators=[DataRequired()])


class ProductForm(FlaskForm):
    name = StringField("Product name", validators=[DataRequired(), Length(max=160)])
    slug = StringField("Slug (url-friendly)", validators=[DataRequired(), Length(max=160)])
    description = TextAreaField("Description")
    image_url = StringField("Image URL", validators=[Length(max=300)])
    price_per_day = FloatField("Price per day (INR)", validators=[DataRequired(), NumberRange(min=0)])
    quantity_available = IntegerField("Quantity available", validators=[DataRequired(), NumberRange(min=0)])
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    is_active = BooleanField("Active / visible on site", default=True)


class CategoryForm(FlaskForm):
    name = StringField("Category name", validators=[DataRequired(), Length(max=80)])
    slug = StringField("Slug", validators=[DataRequired(), Length(max=80)])
    icon = StringField("Icon key", validators=[Length(max=50)])
