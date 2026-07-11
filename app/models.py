from datetime import date, datetime, time
from flask import session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    trips = db.relationship('Trip', back_populates='owner', lazy='dynamic')
    memberships = db.relationship('TripMember', back_populates='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return session.get('user_id') == self.id


class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    destination = db.Column(db.String(128), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    is_public = db.Column(db.Boolean, default=False, nullable=False)

    owner = db.relationship('User', back_populates='trips')
    members = db.relationship('TripMember', back_populates='trip', lazy='dynamic')
    itineraries = db.relationship('Itinerary', back_populates='trip', lazy='dynamic')
    expenses = db.relationship('Expense', back_populates='trip', lazy='dynamic')
    packing_items = db.relationship('PackingItem', back_populates='trip', lazy='dynamic')


class TripMember(db.Model):
    __tablename__ = 'trip_members'

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(16), nullable=False, default='viewer')

    trip = db.relationship('Trip', back_populates='members')
    user = db.relationship('User', back_populates='memberships')


class Itinerary(db.Model):
    __tablename__ = 'itineraries'

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)

    trip = db.relationship('Trip', back_populates='itineraries')
    activities = db.relationship('Activity', back_populates='itinerary', lazy='dynamic')


class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itineraries.id'), nullable=False)
    time = db.Column(db.Time, nullable=True)
    title = db.Column(db.String(128), nullable=False)
    place_name = db.Column(db.String(128), nullable=True)
    duration_min = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    itinerary = db.relationship('Itinerary', back_populates='activities')


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    category = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    description = db.Column(db.String(256), nullable=True)
    date = db.Column(db.Date, nullable=True)

    trip = db.relationship('Trip', back_populates='expenses')


class PackingItem(db.Model):
    __tablename__ = 'packing_items'

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    category = db.Column(db.String(64), nullable=True)
    is_packed = db.Column(db.Boolean, default=False, nullable=False)

    trip = db.relationship('Trip', back_populates='packing_items')


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)
    category = db.Column(db.String(64), nullable=True)
    unit = db.Column(db.String(16), nullable=False, default='pcs')
    current_stock = db.Column(db.Float, nullable=False, default=0)
    min_stock = db.Column(db.Float, nullable=False, default=0)
    purchase_price = db.Column(db.Float, nullable=False, default=0)
    sell_price = db.Column(db.Float, nullable=False, default=0)
    currency = db.Column(db.String(3), nullable=False, default='GEL')

    movements = db.relationship('StockMovement', back_populates='product', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'category': self.category,
            'unit': self.unit,
            'current_stock': self.current_stock,
            'min_stock': self.min_stock,
            'purchase_price': self.purchase_price,
            'sell_price': self.sell_price,
            'currency': self.currency,
            'is_low_stock': self.current_stock < self.min_stock,
        }


class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(128), nullable=False)
    contact = db.Column(db.String(128), nullable=True)
    country = db.Column(db.String(64), nullable=True)
    lead_time = db.Column(db.Integer, nullable=True)

    movements = db.relationship('StockMovement', back_populates='supplier', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'company': self.company,
            'contact': self.contact,
            'country': self.country,
            'lead_time': self.lead_time,
        }


class StockMovement(db.Model):
    __tablename__ = 'stock_movements'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    type = db.Column(db.String(8), nullable=False)  # 'in' or 'out'
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    quantity = db.Column(db.Float, nullable=False)
    cost_per_unit = db.Column(db.Float, nullable=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    reference = db.Column(db.String(128), nullable=True)
    destination = db.Column(db.String(128), nullable=True)

    product = db.relationship('Product', back_populates='movements')
    supplier = db.relationship('Supplier', back_populates='movements')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'type': self.type,
            'supplier_id': self.supplier_id,
            'supplier_company': self.supplier.company if self.supplier else None,
            'quantity': self.quantity,
            'cost_per_unit': self.cost_per_unit,
            'date': self.date.isoformat(),
            'reference': self.reference,
            'destination': self.destination,
        }


class ExchangeRate(db.Model):
    __tablename__ = 'exchange_rates'

    id = db.Column(db.Integer, primary_key=True)
    base_currency = db.Column(db.String(3), nullable=False, default='GEL')
    target_currency = db.Column(db.String(3), nullable=False)
    rate = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)

    def to_dict(self):
        return {
            'id': self.id,
            'base_currency': self.base_currency,
            'target_currency': self.target_currency,
            'rate': self.rate,
            'date': self.date.isoformat(),
        }
