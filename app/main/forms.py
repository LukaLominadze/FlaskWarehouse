from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length, ValidationError
from app.models import Product


class ProductForm(FlaskForm):
    sku = StringField('SKU', validators=[DataRequired(), Length(max=64)])
    name = StringField('Name', validators=[DataRequired(), Length(max=128)])
    category = StringField('Category', validators=[Optional(), Length(max=64)])
    unit = SelectField('Unit', choices=[
        ('pcs', 'Pieces'), ('kg', 'Kg'), ('g', 'Grams'),
        ('l', 'Liters'), ('ml', 'ML'), ('m', 'Meters'),
        ('box', 'Box'), ('pack', 'Pack'),
    ], default='pcs')
    current_stock = FloatField('Current Stock', validators=[DataRequired(), NumberRange(min=0)], default=0)
    min_stock = FloatField('Min Stock', validators=[DataRequired(), NumberRange(min=0)], default=0)
    purchase_price = FloatField('Purchase Price', validators=[DataRequired(), NumberRange(min=0)], default=0)
    sell_price = FloatField('Sell Price', validators=[DataRequired(), NumberRange(min=0)], default=0)
    currency = SelectField('Currency', choices=[
        ('GEL', 'GEL'), ('USD', 'USD'), ('EUR', 'EUR'), ('TRY', 'TRY'),
    ], default='GEL')
    submit = SubmitField('Save')

    def __init__(self, original_sku=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_sku = original_sku

    def validate_sku(self, field):
        if field.data != self.original_sku:
            if Product.query.filter_by(sku=field.data).first():
                raise ValidationError('SKU already exists.')


class SupplierForm(FlaskForm):
    company = StringField('Company', validators=[DataRequired(), Length(max=128)])
    contact = StringField('Contact', validators=[Optional(), Length(max=128)])
    country = StringField('Country', validators=[Optional(), Length(max=64)])
    lead_time = IntegerField('Lead Time (days)', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Save')


class StockInForm(FlaskForm):
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    supplier_id = SelectField('Supplier', coerce=int, validators=[Optional()])
    quantity = FloatField('Quantity', validators=[DataRequired(), NumberRange(min=0.01)])
    cost_per_unit = FloatField('Cost per Unit', validators=[Optional(), NumberRange(min=0)])
    date = StringField('Date', validators=[DataRequired()])
    reference = StringField('Reference', validators=[Optional(), Length(max=128)])
    submit = SubmitField('Receive Stock')


class StockOutForm(FlaskForm):
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    quantity = FloatField('Quantity', validators=[DataRequired(), NumberRange(min=0.01)])
    destination = StringField('Destination', validators=[Optional(), Length(max=128)])
    date = StringField('Date', validators=[DataRequired()])
    reference = StringField('Reference', validators=[Optional(), Length(max=128)])
    submit = SubmitField('Issue Stock')


class ExchangeRateForm(FlaskForm):
    currency = SelectField('Currency', choices=[
        ('USD', 'USD'), ('EUR', 'EUR'), ('TRY', 'TRY'),
        ('GBP', 'GBP'), ('RUB', 'RUB'),
    ])
    rate = FloatField('Rate (to GEL)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Update Rate')
